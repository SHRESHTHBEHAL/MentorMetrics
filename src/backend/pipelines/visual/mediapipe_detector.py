import mediapipe as mp
import numpy as np
from typing import Dict, Any, Optional, Tuple
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

mp_face_detection = mp.solutions.face_detection
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose

_face_detector = None
_hands_detector = None
_pose_detector = None

def _initialize_detectors(
    min_face_confidence: float = 0.7,
    min_hand_confidence: float = 0.6
):
    
    global _face_detector, _hands_detector, _pose_detector
    
    if _face_detector is None:
        _face_detector = mp_face_detection.FaceDetection(
            min_detection_confidence=min_face_confidence
        )
        logger.info("Face detector initialized")
    
    if _hands_detector is None:
        _hands_detector = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=min_hand_confidence,
            min_tracking_confidence=0.5
        )
        logger.info("Hands detector initialized")
    
    if _pose_detector is None:
        _pose_detector = mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        logger.info("Pose detector initialized")

def analyze_frame(
    frame_rgb: np.ndarray,
    min_face_confidence: float = 0.7,
    min_hand_confidence: float = 0.6
) -> Dict[str, Any]:
    
    _initialize_detectors(min_face_confidence, min_hand_confidence)
    
    result = {
        "face_detected": False,
        "face_confidence": None,
        "gaze_direction": None,
        "hands_detected": False,
        "hand_count": 0,
        "body_movement": None,
        "raw": {
            "face": None,
            "hands": None,
            "pose": None
        }
    }
    
    try:
        face_results = _face_detector.process(frame_rgb)
        if face_results.detections:
            detection = face_results.detections[0]  # Use first face
            result["face_detected"] = True
            result["face_confidence"] = detection.score[0]
            
            gaze = _estimate_gaze_direction(detection, frame_rgb.shape)
            result["gaze_direction"] = gaze
            
            result["raw"]["face"] = {
                "score": detection.score[0],
                "bbox": _get_face_bbox(detection, frame_rgb.shape)
            }
    
    except Exception as e:
        result["face_detected"] = False
    
    try:
        hands_results = _hands_detector.process(frame_rgb)
        if hands_results.multi_hand_landmarks:
            result["hands_detected"] = True
            result["hand_count"] = len(hands_results.multi_hand_landmarks)
            
            hand_data = []
            for idx, hand_landmarks in enumerate(hands_results.multi_hand_landmarks):
                handedness = hands_results.multi_handedness[idx].classification[0].label
                hand_data.append({
                    "handedness": handedness,
                    "landmarks": [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                })
            result["raw"]["hands"] = hand_data
    
    except Exception as e:
        result["hands_detected"] = False
    
    try:
        pose_results = _pose_detector.process(frame_rgb)
        if pose_results.pose_landmarks:
            movement = _calculate_body_movement(pose_results.pose_landmarks)
            result["body_movement"] = movement
            
            result["raw"]["pose"] = {
                "landmarks": [(lm.x, lm.y, lm.z) for lm in pose_results.pose_landmarks.landmark]
            }
    
    except Exception as e:
        result["body_movement"] = None
    
    return result

def _estimate_gaze_direction(
    face_detection,
    frame_shape: Tuple[int, int, int]
) -> str:
    """
    Estimate gaze direction based on face position in frame.
    More lenient detection - if face is roughly centered, count as "forward" eye contact.
    """
    try:
        bbox = face_detection.location_data.relative_bounding_box
        
        face_center_x = bbox.xmin + (bbox.width / 2)
        face_center_y = bbox.ymin + (bbox.height / 2)
        
        frame_center_x = 0.5
        
        horizontal_deviation = abs(face_center_x - frame_center_x)
        
        # MORE LENIENT thresholds - count as "forward" if face is anywhere in center 60%
        HORIZONTAL_THRESHOLD = 0.30  # 30% deviation from center (was 15%)
        VERTICAL_DOWN_THRESHOLD = 0.75  # Only count as "down" if face is really low
        
        if face_center_y > VERTICAL_DOWN_THRESHOLD:
            return "down"
        elif horizontal_deviation > HORIZONTAL_THRESHOLD:
            return "away"
        else:
            return "forward"
    
    except Exception:
        return "forward"  # Default to forward when face detected

def _get_face_bbox(
    face_detection,
    frame_shape: Tuple[int, int, int]
) -> Dict[str, float]:
    
    try:
        bbox = face_detection.location_data.relative_bounding_box
        return {
            "xmin": bbox.xmin,
            "ymin": bbox.ymin,
            "width": bbox.width,
            "height": bbox.height
        }
    except Exception:
        return {}

def _calculate_body_movement(pose_landmarks) -> float:
    
    try:
        left_shoulder = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
        
        shoulder_width = abs(right_shoulder.x - left_shoulder.x)
        hip_width = abs(right_hip.x - left_hip.x)
        
        avg_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
        avg_hip_y = (left_hip.y + right_hip.y) / 2
        torso_length = abs(avg_hip_y - avg_shoulder_y)
        
        width_variation = abs(shoulder_width - hip_width)
        
        movement_score = min(width_variation * 20, 10.0)
        
        return round(movement_score, 2)
    
    except Exception:
        return 0.0

def cleanup_detectors():
    
    global _face_detector, _hands_detector, _pose_detector
    
    if _face_detector is not None:
        _face_detector.close()
        _face_detector = None
    
    if _hands_detector is not None:
        _hands_detector.close()
        _hands_detector = None
    
    if _pose_detector is not None:
        _pose_detector.close()
        _pose_detector = None
    
    logger.info("MediaPipe detectors cleaned up")

def batch_analyze_frames(
    frames: list,
    min_face_confidence: float = 0.7,
    min_hand_confidence: float = 0.6,
    log_progress: bool = True
) -> list:
    
    results = []
    total = len(frames)
    
    if log_progress:
        logger.info(f"Starting batch analysis of {total} frames")
    
    for idx, frame_data in enumerate(frames):
        frame_rgb = frame_data.get("frame")
        if frame_rgb is None:
            results.append(None)
            continue
        
        analysis = analyze_frame(
            frame_rgb,
            min_face_confidence=min_face_confidence,
            min_hand_confidence=min_hand_confidence
        )
        
        analysis["timestamp"] = frame_data.get("timestamp")
        analysis["frame_number"] = frame_data.get("frame_number")
        
        results.append(analysis)
        
        if log_progress and (idx + 1) % max(1, total // 5) == 0:
            logger.info(f"Processed {idx + 1}/{total} frames ({(idx+1)/total*100:.0f}%)")
    
    if log_progress:
        logger.info(f"Batch analysis completed: {total} frames processed")
    
    return results
