from pydub import AudioSegment, silence
from src.backend.utils.logger import setup_logger
import os

logger = setup_logger(__name__)

def detect_silence_intervals(audio_path: str, min_silence_len=800, silence_thresh=-40) -> dict:
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        logger.info(f"Starting silence detection for {audio_path}")
        
        audio = AudioSegment.from_file(audio_path)
        
        if audio.channels > 1:
            audio = audio.set_channels(1)
            
        duration_seconds = len(audio) / 1000.0
        
        if duration_seconds < 2:
            logger.warning(f"Audio too short for silence detection: {duration_seconds}s")
            return {
                "silence_ratio": 0.0,
                "total_silence_seconds": 0.0,
                "silence_segments": []
            }

        silence_segments = silence.detect_silence(
            audio, 
            min_silence_len=min_silence_len, 
            silence_thresh=silence_thresh
        )
        
        silence_intervals = []
        total_silence_ms = 0
        
        for start, end in silence_segments:
            silence_intervals.append({
                "start": start / 1000.0,
                "end": end / 1000.0
            })
            total_silence_ms += (end - start)
            
        total_silence_seconds = total_silence_ms / 1000.0
        silence_ratio = total_silence_seconds / duration_seconds if duration_seconds > 0 else 0
        
        logger.info(f"Silence detection completed. Ratio: {silence_ratio:.2f}, Segments: {len(silence_intervals)}")
        
        return {
            "silence_ratio": round(silence_ratio, 2),
            "total_silence_seconds": round(total_silence_seconds, 2),
            "silence_segments": silence_intervals
        }

    except Exception as e:
        logger.error(f"Silence detection failed: {str(e)}")
        raise RuntimeError(f"Silence detection failed: {str(e)}")
