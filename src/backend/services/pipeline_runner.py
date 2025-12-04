from typing import Dict, Any
from src.backend.utils.logger import setup_logger
from src.backend.services.session_service import SessionService
from src.backend.pipelines.process_pipeline import process_session

logger = setup_logger(__name__)

def run_full_pipeline(session_id: str) -> Dict[str, Any]:
    
    if not session_id:
        logger.error("run_full_pipeline: session_id is required")
        return {
            "status": "error",
            "error": "session_id is required"
        }
    
    try:
        logger.info(f"Pipeline run requested for session: {session_id}")
        
        session = SessionService.get_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return {
                "status": "error",
                "session_id": session_id,
                "error": "Session not found"
            }
        
        logger.info(f"Session validated: {session.get('filename')}")
        logger.info(f"Starting full pipeline execution for session {session_id}")
        
        result = process_session(session_id)
        
        if result.get("status") == "complete":
            logger.info(f"Pipeline completed successfully for session {session_id}")
            logger.info(f"  Mentor Score: {result.get('mentor_score', 'N/A')}")
        else:
            logger.error(f"Pipeline failed for session {session_id}: {result.get('error', 'Unknown error')}")
        
        return {
            "status": "processing_started",
            "session_id": session_id
        }
    
    except Exception as e:
        logger.error(f"Pipeline execution failed for session {session_id}: {str(e)}")
        
        try:
            SessionService.update_session_status(session_id, "failed")
        except Exception as status_error:
            logger.error(f"Failed to update session status: {str(status_error)}")
        
        return {
            "status": "error",
            "session_id": session_id,
            "error": str(e)
        }

def run_full_pipeline_async(session_id: str) -> None:
    
    logger.info(f"[ASYNC] Starting background pipeline execution for session {session_id}")
    
    try:
        result = process_session(session_id)
        
        if result.get("status") == "complete":
            logger.info(f"[ASYNC] Pipeline completed successfully for session {session_id}")
            logger.info(f"[ASYNC]   Mentor Score: {result.get('mentor_score', 'N/A')}/10")
            logger.info(f"[ASYNC]   Duration: {result.get('duration_sec', 'N/A')}s")
        else:
            logger.error(f"[ASYNC] Pipeline failed for session {session_id}")
            logger.error(f"[ASYNC]   Error: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        logger.error(f"[ASYNC] Fatal error in pipeline execution for session {session_id}")
        logger.error(f"[ASYNC] Exception: {str(e)}", exc_info=True)
        
        try:
            SessionService.update_session_status(session_id, "failed")
            logger.info(f"[ASYNC] Updated session {session_id} status to 'failed'")
        except Exception as status_error:
            logger.error(f"[ASYNC] Failed to update session status: {str(status_error)}")
    
    logger.info(f"[ASYNC] Background pipeline execution finished for session {session_id}")

__all__ = ['run_full_pipeline', 'run_full_pipeline_async']
