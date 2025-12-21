from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import numpy as np
import cv2
import base64
from typing import Dict, Any
from src.backend.utils.logger import setup_logger
import mediapipe as mp

logger = setup_logger(__name__)

router = APIRouter()

# Initialize MediaPipe solutions for live analysis
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands

# Lazy-loaded detectors
_face_mesh = None
_hands = None

def _get_face_mesh():
    global _face_mesh
    if _face_mesh is None:
        _face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    return _face_mesh

def _get_hands():
    global _hands
    if _hands is None:
        _hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    return _hands

class LiveFrameRequest(BaseModel):
    image: str  # Base64 encoded image

@router.post("/analyze")
async def analyze_live_frame(request: LiveFrameRequest) -> Dict[str, Any]:
    try:
        # Decode base64 image
        if "," in request.image:
            header, encoded = request.image.split(",", 1)
        else:
            encoded = request.image
            
        image_data = base64.b64decode(encoded)
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame.shape[:2]
        
        response = {
            "eye_contact": False,
            "gestures": 0,
            "face_detected": False,
            "pose_score": 0.0
        }
        
        # === FACE MESH ANALYSIS FOR EYE CONTACT ===
        face_mesh = _get_face_mesh()
        face_results = face_mesh.process(frame_rgb)
        
        if face_results.multi_face_landmarks:
            response["face_detected"] = True
            landmarks = face_results.multi_face_landmarks[0].landmark
            
            # Get key eye landmarks for gaze detection
            # Iris landmarks: Right iris center (468), Left iris center (473)
            # Eye corners for reference
            try:
                # Left eye: landmarks 33 (outer corner), 133 (inner corner)
                # Right eye: landmarks 362 (outer corner), 263 (inner corner)
                # Nose tip: 1
                
                left_eye_outer = landmarks[33]
                left_eye_inner = landmarks[133]
                right_eye_outer = landmarks[362]
                right_eye_inner = landmarks[263]
                nose_tip = landmarks[1]
                
                # Calculate eye center positions
                left_eye_center_x = (left_eye_outer.x + left_eye_inner.x) / 2
                right_eye_center_x = (right_eye_outer.x + right_eye_inner.x) / 2
                
                # Calculate face center (average of nose and eyes)
                face_center_x = (left_eye_center_x + right_eye_center_x) / 2
                
                # Check if face is roughly centered (looking at camera)
                # If face center is within 25% of frame center, consider it eye contact
                horizontal_offset = abs(face_center_x - 0.5)
                
                # Check vertical - if they're looking down (nose tip too low)
                vertical_offset = nose_tip.y
                
                # Eye contact if:
                # 1. Face is horizontally centered (within 25% of center)
                # 2. Face is not looking too far down (y < 0.7)
                if horizontal_offset < 0.25 and vertical_offset < 0.7:
                    response["eye_contact"] = True
                else:
                    response["eye_contact"] = False
                    
            except (IndexError, AttributeError):
                # If landmark access fails, default based on face detection
                response["eye_contact"] = False
        
        # === HANDS ANALYSIS FOR GESTURES ===
        hands = _get_hands()
        hands_results = hands.process(frame_rgb)
        
        if hands_results.multi_hand_landmarks:
            gesture_count = 0
            for hand_landmarks in hands_results.multi_hand_landmarks:
                # Get wrist position (landmark 0)
                wrist = hand_landmarks.landmark[0]
                
                # Count any hand that is visible in upper 80% of frame
                # (y values go from 0=top to 1=bottom)
                if wrist.y < 0.8:
                    gesture_count += 1
                    
            response["gestures"] = gesture_count
            logger.debug(f"Hands detected: {gesture_count}")
            
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing live frame: {str(e)}")
        # Return safe defaults
        return {
            "eye_contact": False,
            "gestures": 0,
            "face_detected": False,
            "pose_score": 0.0
        }
