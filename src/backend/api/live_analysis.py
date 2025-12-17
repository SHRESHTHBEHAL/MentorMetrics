from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import numpy as np
import cv2
import base64
from typing import Dict, Any, Optional
from src.backend.pipelines.visual import mediapipe_detector
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

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
            
        # Convert BGR to RGB (MediaPipe uses RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Analyze frame
        results = mediapipe_detector.analyze_frame(frame_rgb)
        
        # Simplify results for frontend
        response = {
            "eye_contact": False,
            "gestures": 0,
            "face_detected": results.get("face_detected", False),
            "pose_score": 0.0
        }
        
        # Interpret Eye Contact
        if results.get("face_detected"):
            gaze = results.get("gaze_direction")
            # If gaze is 'forward', we consider it good eye contact
            response["eye_contact"] = (gaze == "forward")
            
        # Interpret Gestures
        if results.get("hands_detected"):
            response["gestures"] = results.get("hand_count", 0)
            
        # Interpret Pose/Body Movement
        if results.get("body_movement"):
            response["pose_score"] = results.get("body_movement", 0.0)
            
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing live frame: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
