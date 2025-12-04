from typing import List, Dict, Any, Optional
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def calculate_wpm(segments: List[Dict[str, Any]]) -> Optional[float]:
    if not segments:
        logger.warning("WPM Calculator: Empty segments list")
        return None

    try:
        if 'start' not in segments[0] or 'end' not in segments[-1]:
             logger.error("WPM Calculator: Missing timestamps in segments")
             return None

        start_time = segments[0]['start']
        end_time = segments[-1]['end']
        
        if not isinstance(start_time, (int, float)) or not isinstance(end_time, (int, float)):
             logger.error("WPM Calculator: Invalid timestamp types")
             return None

        duration_seconds = end_time - start_time
        
        if duration_seconds < 5:
            logger.warning(f"WPM Calculator: Duration too short ({duration_seconds}s)")
            return None

        total_words = 0
        for segment in segments:
            text = segment.get('text', '')
            if isinstance(text, str):
                words = text.strip().split()
                total_words += len(words)
        
        duration_minutes = duration_seconds / 60.0
        if duration_minutes == 0:
            return None
            
        wpm = total_words / duration_minutes
        
        logger.info(f"WPM Calculator: {len(segments)} segments, {total_words} words, {duration_seconds:.2f}s duration")
        
        return round(wpm, 2)

    except Exception as e:
        logger.error(f"WPM Calculator failed: {str(e)}")
        return None
