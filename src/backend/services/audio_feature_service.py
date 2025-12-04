from src.backend.utils.supabase_client import supabase
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class AudioFeatureService:
    @staticmethod
    def save_audio_features(session_id: str, features_dict: dict):
        if not session_id or not features_dict:
            logger.error("Invalid input for save_audio_features")
            return None

        try:
            logger.info(f"Saving audio features for session {session_id}")
            
            data = {
                "session_id": session_id,
                "words_per_minute": features_dict.get("words_per_minute"),
                "silence_ratio": features_dict.get("silence_ratio"),
                "avg_volume": features_dict.get("avg_volume"),
                "volume_variation": features_dict.get("volume_variation"),
                "clarity_score": features_dict.get("clarity_score"),
                "raw_features": features_dict.get("raw_features", {})
            }
            
            response = supabase.table("audio_features").insert(data).execute()
            
            if response.data:
                logger.info(f"Audio features saved successfully for session {session_id}")
                return response.data[0]['id']
            else:
                logger.warning(f"No rows inserted for audio features session {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"DB failure saving audio features for session {session_id}: {str(e)}")
            return None

    @staticmethod
    def get_audio_features(session_id: str):
        if not session_id:
            return None
            
        try:
            response = supabase.table("audio_features").select("*").eq("session_id", session_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                logger.info(f"Audio features not found for session {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching audio features for session {session_id}: {str(e)}")
            return None
