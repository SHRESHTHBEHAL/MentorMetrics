from src.backend.utils.supabase_client import supabase
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class TranscriptService:
    @staticmethod
    def save_transcript(session_id: str, full_text: str, segments: list):
        if not session_id or not full_text:
            logger.error("Invalid input for save_transcript")
            return None

        try:
            logger.info(f"Transcript save started for session {session_id}")
            
            data = {
                "session_id": session_id,
                "raw_text": full_text,
                "segments": segments,
                "word_timestamps": [] 
            }
            
            response = supabase.table("transcripts").insert(data).execute()
            
            if response.data:
                logger.info(f"Transcript saved successfully. Rows inserted: {len(response.data)}")
                return response.data[0]['id']
            else:
                logger.warning(f"No rows inserted for transcript session {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"DB failure saving transcript for session {session_id}: {str(e)}")
            return None

    @staticmethod
    def get_transcript(session_id: str):
        if not session_id:
            return None
            
        try:
            response = supabase.table("transcripts").select("*").eq("session_id", session_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                logger.info(f"Transcript not found for session {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching transcript for session {session_id}: {str(e)}")
            return None
