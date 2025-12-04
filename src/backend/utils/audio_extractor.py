import os
import subprocess
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def extract_audio_from_video(video_path: str, output_audio_path: str) -> str:
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        raise FileNotFoundError(f"Video file not found: {video_path}")

    try:
        logger.info(f"Starting audio extraction from {video_path} to {output_audio_path}")
        
        command = [
            "ffmpeg",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            output_audio_path
        ]
        
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"Audio extraction completed: {output_audio_path}")
        return output_audio_path

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed: {e.stderr}")
        raise RuntimeError(f"Audio extraction failed: {e.stderr}")
    except Exception as e:
        logger.error(f"Audio extraction failed: {str(e)}")
        raise RuntimeError(f"Audio extraction failed: {str(e)}")
