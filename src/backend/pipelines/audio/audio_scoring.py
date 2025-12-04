from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def compute_audio_scores(wpm_value: float, silence_dict: dict, clarity_dict: dict) -> dict:
    try:
        wpm_score = 0.0
        if wpm_value is None:
            wpm_score = 0.0
        elif 120 <= wpm_value <= 150:
            wpm_score = 10.0
        elif wpm_value > 150:
            wpm_score = max(0.0, 10.0 - (wpm_value - 150) * 0.2)
        else: # wpm_value < 120
            wpm_score = max(0.0, 10.0 - (120 - wpm_value) * 0.1)
            
        wpm_score = round(wpm_score, 2)

        silence_ratio = silence_dict.get("silence_ratio", 0.0)
        silence_score = 0.0
        
        if silence_ratio <= 0.15:
            silence_score = 10.0
        else:
            silence_score = max(0.0, 10.0 - (silence_ratio - 0.15) * 20)
            
        silence_score = round(silence_score, 2)

        clarity_score = clarity_dict.get("clarity_score", 0.0)
        
        weights = {"wpm": 0.4, "silence": 0.2, "clarity": 0.4}
        
        audio_overall = (
            (wpm_score * weights["wpm"]) +
            (silence_score * weights["silence"]) +
            (clarity_score * weights["clarity"])
        )
        audio_overall = round(audio_overall, 2)
        
        logger.info(f"Audio Scoring: WPM={wpm_score}, Silence={silence_score}, Clarity={clarity_score} -> Overall={audio_overall}")
        
        return {
            "wpm": wpm_value,
            "wpm_score": wpm_score,
            "silence_ratio": silence_ratio,
            "silence_score": silence_score,
            "clarity_score": clarity_score,
            "audio_overall": audio_overall,
            "words_per_minute": wpm_value,  # For AudioFeatureService compatibility
            "raw_features": {
                "wpm": wpm_value,
                "silence": silence_dict,
                "clarity": clarity_dict
            }
        }

    except Exception as e:
        logger.error(f"Audio scoring failed: {str(e)}")
        return {
            "wpm_score": 0.0,
            "silence_score": 0.0,
            "clarity_score": 0.0,
            "audio_overall": 0.0,
            "raw": {"error": str(e)}
        }
