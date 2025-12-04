import cv2
import numpy as np
import os
import time
from typing import List, Dict, Any, Optional
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class FrameExtractionError(Exception):
    
    pass

def extract_frames(
    video_path: str, 
    fps: int = 2,
    max_frames: int = 1000
) -> List[Dict[str, Any]]:
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if fps <= 0:
        raise ValueError(f"FPS must be positive, got: {fps}")
    
    if max_frames <= 0:
        raise ValueError(f"max_frames must be positive, got: {max_frames}")
    
    frames = []
    cap = None
    
    try:
        start_time = time.time()
        logger.info(f"Starting frame extraction from {video_path} at {fps} FPS")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise FrameExtractionError(f"Failed to open video: {video_path}")
        
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / original_fps if original_fps > 0 else 0
        
        if original_fps == 0:
            raise FrameExtractionError("Video has invalid FPS (0)")
        
        logger.info(f"Video properties: {original_fps:.2f} FPS, {total_frames} total frames, {duration:.2f}s duration")
        
        frame_interval = int(original_fps / fps)
        if frame_interval == 0:
            frame_interval = 1
            logger.warning(f"Requested FPS ({fps}) higher than video FPS ({original_fps}), extracting every frame")
        
        frame_count = 0
        extracted_count = 0
        failed_count = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                try:
                    if frame is None or frame.size == 0:
                        logger.warning(f"Corrupted frame at frame_count={frame_count}, skipping")
                        failed_count += 1
                        frame_count += 1
                        continue
                    
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    timestamp = frame_count / original_fps
                    
                    frames.append({
                        "frame": frame_rgb,
                        "timestamp": timestamp,
                        "frame_number": frame_count
                    })
                    
                    extracted_count += 1
                    
                    if extracted_count >= max_frames:
                        logger.info(f"Reached max_frames limit ({max_frames}), stopping extraction")
                        break
                
                except Exception as e:
                    logger.warning(f"Error processing frame {frame_count}: {str(e)}")
                    failed_count += 1
            
            frame_count += 1
        
        extraction_duration = time.time() - start_time
        
        if len(frames) == 0:
            raise FrameExtractionError("No frames could be extracted from video")
        
        if len(frames) > 1:
            timestamps = [f["timestamp"] for f in frames]
            intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            avg_interval = sum(intervals) / len(intervals)
        else:
            avg_interval = 0.0
        
        logger.info(f"Frame extraction completed:")
        logger.info(f"  - Extracted {extracted_count} frames")
        logger.info(f"  - Failed frames: {failed_count}")
        logger.info(f"  - Average interval: {avg_interval:.3f}s")
        logger.info(f"  - Extraction duration: {extraction_duration:.2f}s")
        logger.info(f"  - Effective FPS: {extracted_count/duration:.2f}")
        
        return frames
    
    except cv2.error as e:
        raise FrameExtractionError(f"OpenCV error during frame extraction: {str(e)}")
    
    except Exception as e:
        if isinstance(e, (FrameExtractionError, FileNotFoundError, ValueError)):
            raise
        raise FrameExtractionError(f"Unexpected error during frame extraction: {str(e)}")
    
    finally:
        if cap is not None:
            cap.release()
            logger.info("Video capture released")

def get_video_metadata(video_path: str) -> Optional[Dict[str, Any]]:
    
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return None
    
    cap = None
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return None
        
        metadata = {
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        return metadata
    
    except Exception as e:
        logger.error(f"Error extracting video metadata: {str(e)}")
        return None
    
    finally:
        if cap is not None:
            cap.release()
