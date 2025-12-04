from typing import List, Dict, Any, Optional
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def compute_engagement_metrics(frames_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    
    if not frames_results or len(frames_results) == 0:
        logger.warning("No frames provided for engagement analysis")
        return _get_empty_metrics(frames_results)
    
    logger.info(f"Computing engagement metrics for {len(frames_results)} frames")
    
    total_frames = len(frames_results)
    face_detected_count = 0
    gaze_forward_count = 0
    hands_detected_count = 0
    gesture_frames_count = 0
    body_movements = []
    
    for frame_result in frames_results:
        if frame_result is None or not isinstance(frame_result, dict):
            continue
        
        if frame_result.get("face_detected", False):
            face_detected_count += 1
        
        gaze = frame_result.get("gaze_direction")
        if gaze == "forward":
            gaze_forward_count += 1
        
        if frame_result.get("hands_detected", False):
            hands_detected_count += 1
        
        hand_count = frame_result.get("hand_count", 0)
        if hand_count > 0:
            gesture_frames_count += 1
        
        body_movement = frame_result.get("body_movement")
        if body_movement is not None and isinstance(body_movement, (int, float)):
            body_movements.append(body_movement)
    
    metrics = {}
    
    metrics["face_visibility_ratio"] = round(
        face_detected_count / total_frames if total_frames > 0 else 0.0,
        3
    )
    
    metrics["gaze_forward_ratio"] = round(
        gaze_forward_count / face_detected_count if face_detected_count > 0 else 0.0,
        3
    )
    
    duration_minutes = _estimate_duration_minutes(frames_results)
    metrics["hand_movement_frequency"] = round(
        hands_detected_count / duration_minutes if duration_minutes > 0 else hands_detected_count,
        2
    )
    
    metrics["body_movement_activity"] = round(
        sum(body_movements) / len(body_movements) if body_movements else 0.0,
        2
    )
    
    metrics["gesture_activity_ratio"] = round(
        gesture_frames_count / total_frames if total_frames > 0 else 0.0,
        3
    )
    
    metrics["raw"] = frames_results
    
    logger.info(f"Engagement metrics computed:")
    logger.info(f"  - Face visibility: {metrics['face_visibility_ratio']:.1%}")
    logger.info(f"  - Gaze forward: {metrics['gaze_forward_ratio']:.1%}")
    logger.info(f"  - Hand movement frequency: {metrics['hand_movement_frequency']:.1f}/min")
    logger.info(f"  - Body movement activity: {metrics['body_movement_activity']:.1f}/10")
    logger.info(f"  - Gesture activity: {metrics['gesture_activity_ratio']:.1%}")
    
    return metrics

def _estimate_duration_minutes(frames_results: List[Dict[str, Any]]) -> float:
    
    try:
        timestamps = []
        for frame in frames_results:
            if frame and isinstance(frame, dict):
                ts = frame.get("timestamp")
                if ts is not None and isinstance(ts, (int, float)):
                    timestamps.append(ts)
        
        if len(timestamps) < 2:
            return len(frames_results) / 120.0
        
        duration_seconds = max(timestamps) - min(timestamps)
        return duration_seconds / 60.0
    
    except Exception:
        return len(frames_results) / 120.0

def _get_empty_metrics(frames_results: Optional[List] = None) -> Dict[str, Any]:
    
    return {
        "face_visibility_ratio": 0.0,
        "gaze_forward_ratio": 0.0,
        "hand_movement_frequency": 0.0,
        "body_movement_activity": 0.0,
        "gesture_activity_ratio": 0.0,
        "raw": frames_results or []
    }

def compute_detailed_metrics(frames_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    
    base_metrics = compute_engagement_metrics(frames_results)
    
    if not frames_results:
        return base_metrics
    
    gaze_distribution = {"forward": 0, "away": 0, "down": 0, "unknown": 0}
    hand_statistics = {"left_only": 0, "right_only": 0, "both": 0}
    confidence_scores = {"face": [], "hand": []}
    
    for frame_result in frames_results:
        if not frame_result or not isinstance(frame_result, dict):
            continue
        
        gaze = frame_result.get("gaze_direction")
        if gaze in gaze_distribution:
            gaze_distribution[gaze] += 1
        else:
            gaze_distribution["unknown"] += 1
        
        face_conf = frame_result.get("face_confidence")
        if face_conf is not None:
            confidence_scores["face"].append(face_conf)
        
        hand_count = frame_result.get("hand_count", 0)
        if hand_count == 2:
            hand_statistics["both"] += 1
        elif hand_count == 1:
            hand_statistics["left_only"] += 1  # Placeholder
    
    base_metrics["detailed"] = {
        "gaze_distribution": gaze_distribution,
        "hand_statistics": hand_statistics,
        "average_face_confidence": round(
            sum(confidence_scores["face"]) / len(confidence_scores["face"])
            if confidence_scores["face"] else 0.0,
            3
        ),
        "total_analyzed_frames": len(frames_results),
        "valid_frames": sum(1 for f in frames_results if f is not None)
    }
    
    return base_metrics

def normalize_metrics_for_scoring(
    metrics: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    
    if weights is None:
        weights = {
            "face_visibility_ratio": 0.25,
            "gaze_forward_ratio": 0.20,
            "hand_movement_frequency": 0.25,
            "body_movement_activity": 0.15,
            "gesture_activity_ratio": 0.15
        }
    
    normalized = {}
    
    normalized["face_visibility_score"] = round(
        metrics.get("face_visibility_ratio", 0.0) * 10,
        2
    )
    
    normalized["gaze_forward_score"] = round(
        metrics.get("gaze_forward_ratio", 0.0) * 10,
        2
    )
    
    freq = metrics.get("hand_movement_frequency", 0.0)
    if freq <= 10:
        hand_score = freq
    elif freq <= 40:
        hand_score = 10.0
    else:
        hand_score = max(0, 10 - (freq - 40) * 0.2)  # Penalty for excessive movement
    normalized["hand_movement_score"] = round(hand_score, 2)
    
    body_movement = metrics.get("body_movement_activity", 0.0)
    if 3 <= body_movement <= 7:
        body_score = 10.0
    elif body_movement < 3:
        body_score = body_movement * 3.33  # Scale up low movement
    else:
        body_score = max(0, 10 - (body_movement - 7) * 1.5)  # Penalize high movement
    normalized["body_movement_score"] = round(body_score, 2)
    
    normalized["gesture_activity_score"] = round(
        metrics.get("gesture_activity_ratio", 0.0) * 10,
        2
    )
    
    total_weight = sum(weights.values())
    weighted_sum = sum(
        normalized.get(f"{key.replace('_ratio', '').replace('_frequency', '').replace('_activity', '')}_score", 0) * weight
        for key, weight in weights.items()
    )
    
    normalized["overall_engagement_score"] = round(
        weighted_sum / total_weight if total_weight > 0 else 0.0,
        2
    )
    
    logger.info(f"Normalized engagement score: {normalized['overall_engagement_score']:.1f}/10")
    
    return normalized
