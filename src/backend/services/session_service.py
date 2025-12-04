import os
import tempfile
from datetime import datetime
from src.backend.utils.supabase_client import supabase
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

VALID_STATUSES = ["pending", "processing", "complete", "failed"]

class SessionService:
    @staticmethod
    def get_session(session_id: str):
        try:
            response = supabase.table("sessions").select("*").eq("id", session_id).execute()
            if not response.data:
                return None
            return response.data[0]
        except Exception as e:
            logger.error(f"Error fetching session {session_id}: {str(e)}")
            raise

    @staticmethod
    def update_status(session_id: str, status: str):
        
        try:
            supabase.table("sessions").update({"status": status}).eq("id", session_id).execute()
        except Exception as e:
            logger.error(f"Error updating session status {session_id}: {str(e)}")
            raise
    
    @staticmethod
    def update_session_status(session_id: str, status: str):
        
        if not session_id:
            logger.error("update_session_status: session_id is required")
            return False
        
        if status not in VALID_STATUSES:
            logger.error(f"update_session_status: Invalid status '{status}'. Must be one of: {VALID_STATUSES}")
            return False
        
        try:
            logger.info(f"Updating session {session_id} status to: {status}")
            
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = supabase.table("sessions").update(update_data).eq("id", session_id).execute()
            
            if response.data:
                logger.info(f"Session {session_id} status updated successfully")
                return True
            else:
                logger.warning(f"No session updated for {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating session status for {session_id}: {str(e)}")
            return False
    
    @staticmethod
    def mark_session_completed(session_id: str, completion_metadata: dict = None):
        
        if not session_id:
            logger.error("mark_session_completed: session_id is required")
            return False
        
        try:
            logger.info(f"Marking session {session_id} as completed")
            
            metadata = completion_metadata or {}
            
            if "finished_at" not in metadata:
                metadata["finished_at"] = datetime.utcnow().isoformat()
            
            update_data = {
                "status": "complete",
                "completed_at": datetime.utcnow().isoformat(),
                "completion_metadata": metadata,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = supabase.table("sessions").update(update_data).eq("id", session_id).execute()
            
            if response.data:
                logger.info(f"Session {session_id} marked as completed successfully")
                if "mentor_score" in metadata:
                    logger.info(f"  Mentor Score: {metadata['mentor_score']}/10")
                return True
            else:
                logger.warning(f"No session updated for {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error marking session {session_id} as completed: {str(e)}")
            return False

    @staticmethod
    def download_video(session_id: str, filename: str) -> str:
        try:
            bucket_name = "videos"
            logger.info(f"Downloading video {filename} for session {session_id}")
            
            data = supabase.storage.from_(bucket_name).download(filename)
            
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, f"{session_id}_{filename}")
            
            with open(file_path, "wb") as f:
                f.write(data)
                
            return file_path
        except Exception as e:
            logger.error(f"Error downloading video for session {session_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_session_status(session_id: str):
        
        if not session_id:
            return None
        
        try:
            session = SessionService.get_session(session_id)
            
            if not session:
                return None
            
            status_response = {
                "session_id": session_id,
                "user_id": session.get("user_id"),
                "status": session.get("status", "unknown"),
                "filename": session.get("filename", ""),
                "has_transcript": session.get("has_transcript", False),
                "stages_completed": session.get("stages_completed", []),
                "metadata": {
                    "created_at": session.get("created_at"),
                    "updated_at": session.get("updated_at")
                }
            }
            
            if session.get("completed_at"):
                status_response["metadata"]["completed_at"] = session.get("completed_at")
            
            if session.get("completion_metadata"):
                status_response["metadata"]["completion_metadata"] = session.get("completion_metadata")
            
            return status_response
            
        except Exception as e:
            logger.error(f"Error getting session status for {session_id}: {str(e)}")
            return None
