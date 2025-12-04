from typing import Dict, Any
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

VISUAL_WEIGHTS = {
    "face_visibility": 0.35,
    "gaze_forward": 0.25,
    "gesture": 0.20,
    "movement": 0.20
}

DEFAULT_METRICS = {
    "face_visibility_ratio": 0.5,  # Neutral
    "gaze_forward_ratio": 0.5,     # Neutral
    "gesture_activity_ratio": 0.3,  # Slightly low
    "body_movement_activity": 5.0   # Mid-range
}

def compute_visual_scores(engagement_metrics: Dict[str, Any]) -> Dict[str, float]:
    
    if not engagement_metrics or not isinstance(engagement_metrics, dict):
        logger.warning("Invalid engagement_metrics provided, using defaults")
        engagement_metrics = {}
    
    logger.info("Computing visual scores from engagement metrics")
    
    face_visibility = engagement_metrics.get(
        "face_visibility_ratio",
        DEFAULT_METRICS["face_visibility_ratio"]
    )
    gaze_forward = engagement_metrics.get(
        "gaze_forward_ratio",
        DEFAULT_METRICS["gaze_forward_ratio"]
    )
    gesture_activity = engagement_metrics.get(
        "gesture_activity_ratio",
        DEFAULT_METRICS["gesture_activity_ratio"]
    )
    body_movement = engagement_metrics.get(
        "body_movement_activity",
        DEFAULT_METRICS["body_movement_activity"]
    )
    hand_frequency = engagement_metrics.get("hand_movement_frequency", 0.0)
    
    face_visibility_score = _clamp_score(face_visibility * 10)
    
    gaze_forward_score = _clamp_score(gaze_forward * 10)
    
    gesture_activity_component = gesture_activity * 10 * 0.6
    
    if hand_frequency <= 10:
        frequency_component = hand_frequency * 0.4  # Scale 0-10 → 0-4
    elif 10 < hand_frequency <= 40:
        frequency_component = 4.0  # Optimal range
    else:
        frequency_component = max(0, 4.0 - (hand_frequency - 40) * 0.05)
    
    gesture_score = _clamp_score(gesture_activity_component + frequency_component)
    
    if 3 <= body_movement <= 7:
        movement_score = 10.0
    elif body_movement < 3:
        movement_score = body_movement * 3.33
    else:
        movement_score = max(0, 10 - (body_movement - 7) * 1.5)
    
    movement_score = _clamp_score(movement_score)
    
    logger.info(f"Raw visual scores computed:")
    logger.info(f"  - Face visibility: {face_visibility_score:.2f}/10")
    logger.info(f"  - Gaze forward: {gaze_forward_score:.2f}/10")
    logger.info(f"  - Gesture: {gesture_score:.2f}/10")
    logger.info(f"  - Movement: {movement_score:.2f}/10")
    
    visual_overall = (
        face_visibility_score * VISUAL_WEIGHTS["face_visibility"] +
        gaze_forward_score * VISUAL_WEIGHTS["gaze_forward"] +
        gesture_score * VISUAL_WEIGHTS["gesture"] +
        movement_score * VISUAL_WEIGHTS["movement"]
    )
    
    visual_overall = _clamp_score(visual_overall)
    
    logger.info(f"Visual score weights:")
    logger.info(f"  - Face visibility: {VISUAL_WEIGHTS['face_visibility']:.0%}")
    logger.info(f"  - Gaze forward: {VISUAL_WEIGHTS['gaze_forward']:.0%}")
    logger.info(f"  - Gesture: {VISUAL_WEIGHTS['gesture']:.0%}")
    logger.info(f"  - Movement: {VISUAL_WEIGHTS['movement']:.0%}")
    logger.info(f"Final visual_overall score: {visual_overall:.2f}/10")
    
    return {
        "face_visibility_score": round(face_visibility_score, 2),
        "gaze_forward_score": round(gaze_forward_score, 2),
        "gesture_score": round(gesture_score, 2),
        "movement_score": round(movement_score, 2),
        "visual_overall": round(visual_overall, 2),
        "raw": engagement_metrics
    }

def _clamp_score(score: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
    
    return max(min_val, min(max_val, score))

def get_visual_score_breakdown(visual_scores: Dict[str, float]) -> Dict[str, Any]:
    
    breakdown = {
        "scores": {
            "face_visibility": visual_scores.get("face_visibility_score", 0),
            "gaze_forward": visual_scores.get("gaze_forward_score", 0),
            "gesture": visual_scores.get("gesture_score", 0),
            "movement": visual_scores.get("movement_score", 0),
            "overall": visual_scores.get("visual_overall", 0)
        },
        "weights": VISUAL_WEIGHTS,
        "contributions": {},
        "interpretation": {}
    }
    
    for metric, weight in VISUAL_WEIGHTS.items():
        score_key = f"{metric}_score"
        score = visual_scores.get(score_key, 0)
        contribution = score * weight
        breakdown["contributions"][metric] = round(contribution, 2)
    
    overall = visual_scores.get("visual_overall", 0)
    if overall >= 8:
        interpretation = "Excellent visual engagement"
    elif overall >= 6:
        interpretation = "Good visual engagement"
    elif overall >= 4:
        interpretation = "Moderate visual engagement"
    else:
        interpretation = "Low visual engagement"
    
    breakdown["interpretation"]["overall"] = interpretation
    breakdown["interpretation"]["grade"] = _score_to_grade(overall)
    
    return breakdown

def _score_to_grade(score: float) -> str:
    
    if score >= 9:
        return "A+"
    elif score >= 8:
        return "A"
    elif score >= 7:
        return "B+"
    elif score >= 6:
        return "B"
    elif score >= 5:
        return "C+"
    elif score >= 4:
        return "C"
    elif score >= 3:
        return "D"
    else:
        return "F"

def validate_engagement_metrics(metrics: Dict[str, Any]) -> bool:
    
    required_fields = [
        "face_visibility_ratio",
        "gaze_forward_ratio",
        "gesture_activity_ratio",
        "body_movement_activity"
    ]
    
    if not metrics or not isinstance(metrics, dict):
        return False
    
    for field in required_fields:
        if field not in metrics:
            logger.warning(f"Missing required field: {field}")
            return False
    
    return True
