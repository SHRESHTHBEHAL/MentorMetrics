import librosa
import numpy as np
import os
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def analyze_audio_clarity(audio_path: str) -> dict:
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        logger.info(f"Starting audio clarity analysis for {audio_path}")
        
        y, sr = librosa.load(audio_path, sr=16000, mono=True)
        
        rms = librosa.feature.rms(y=y)[0]
        avg_volume = float(np.mean(rms))
        volume_variation = float(np.std(rms))
        
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        avg_centroid = float(np.mean(spectral_centroid))
        
        vol_score = min(avg_volume * 100, 1.0) 
        
        var_score = min(volume_variation * 100, 1.0)
        
        centroid_score = 1.0
        if avg_centroid < 500 or avg_centroid > 4000:
            centroid_score = 0.5
            
        raw_score = (vol_score * 0.4) + (var_score * 0.4) + (centroid_score * 0.2)
        clarity_score = round(raw_score * 10, 2) # Scale to 0-10
        
        logger.info(f"Clarity analysis completed. Score: {clarity_score}")
        
        return {
            "avg_volume": round(avg_volume, 4),
            "volume_variation": round(volume_variation, 4),
            "clarity_score": clarity_score,
            "raw": {
                "avg_centroid": round(avg_centroid, 2),
                "vol_score": round(vol_score, 2),
                "var_score": round(var_score, 2)
            }
        }

    except Exception as e:
        logger.error(f"Clarity analysis failed: {str(e)}")
        return {
            "avg_volume": 0.0,
            "volume_variation": 0.0,
            "clarity_score": 0.0,
            "raw": {"error": str(e)}
        }
