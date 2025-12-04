from src.backend.utils.supabase_client import supabase
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class ReportService:
    @staticmethod
    def save_report(
        session_id: str,
        summary: str,
        strengths: list,
        improvements: list,
        actionable_tips: list,
        raw_llm_response: dict = None
    ):
        
        if not session_id:
            logger.error("save_report: session_id is required")
            return None
        
        try:
            if not ReportService.validate_session_exists(session_id):
                logger.error(f"Session {session_id} does not exist")
                return None
            
            logger.info(f"Saving report for session {session_id}")
            
            data = {
                "session_id": session_id,
                "summary": summary or "",
                "strengths": strengths or [],
                "improvements": improvements or [],
                "actionable_tips": actionable_tips or [],
                "raw_llm_response": raw_llm_response or {}
            }
            
            response = supabase.table("reports").insert(data).execute()
            
            if response.data:
                logger.info(f"Report saved successfully for session {session_id}")
                logger.info(f"  Summary length: {len(summary)} chars")
                logger.info(f"  Strengths: {len(strengths)} items")
                logger.info(f"  Improvements: {len(improvements)} items")
                logger.info(f"  Tips: {len(actionable_tips)} items")
                return response.data[0]['id']
            else:
                logger.warning(f"No rows inserted for report session {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"DB failure saving report for session {session_id}: {str(e)}")
            return None

    @staticmethod
    def get_report(session_id: str):
        
        if not session_id:
            return None
            
        try:
            logger.info(f"Fetching report for session {session_id}")
            response = supabase.table("reports").select("*").eq("session_id", session_id).execute()
            
            if response.data:
                logger.info(f"Report retrieved for session {session_id}")
                return response.data[0]
            else:
                logger.info(f"Report not found for session {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching report for session {session_id}: {str(e)}")
            return None
    
    @staticmethod
    def validate_session_exists(session_id: str) -> bool:
        
        if not session_id:
            return False
        
        try:
            response = supabase.table("sessions").select("id").eq("id", session_id).execute()
            return response.data and len(response.data) > 0
        except Exception as e:
            logger.error(f"Error validating session {session_id}: {str(e)}")
            return False
    
    @staticmethod
    def get_report_summary_only(session_id: str) -> str:
        
        report = ReportService.get_report(session_id)
        
        if not report:
            return None
        
        return report.get("summary", "")
