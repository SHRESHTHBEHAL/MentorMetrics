from fastapi import APIRouter, HTTPException, Request, Depends
from src.backend.services.user_service import UserService
from src.backend.utils.supabase_client import supabase
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/list")
def list_sessions(request: Request):
    
    user_id = UserService.get_user_id(request)
    
    logger.info(f"[API] GET /sessions/list - Listing sessions for user {user_id}")
    
    try:
        response = supabase.table("sessions")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
            
        sessions = response.data
        
        result = []
        for session in sessions:
            mentor_score = None
            if session.get("completion_metadata"):
                mentor_score = session.get("completion_metadata", {}).get("mentor_score")
            
            result.append({
                "id": session["id"],
                "filename": session["filename"],
                "status": session["status"],
                "created_at": session["created_at"],
                "mentor_score": mentor_score,
                "file_url": session["file_url"]
            })
            
        return result
        
    except Exception as e:
        logger.error(f"[API] Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@router.get("/{session_id}")
def get_session_status(session_id: str, request: Request):
    
    user_id = UserService.get_user_id(request)
    
    logger.info(f"[API] GET /sessions/{session_id} - Getting status for user {user_id}")
    
    try:
        response = supabase.table("sessions")\
            .select("*")\
            .eq("id", session_id)\
            .execute()
            
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Session not found")
            
        session = response.data[0]
        
        import os
        DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
        if not DEV_MODE and session.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "id": session["id"],
            "filename": session["filename"],
            "status": session["status"],
            "file_url": session["file_url"],
            "has_transcript": session.get("has_transcript", False),
            "stages_completed": session.get("stages_completed", []),
            "last_successful_stage": session.get("last_successful_stage"),
            "created_at": session["created_at"],
            "updated_at": session.get("updated_at"),
            "completed_at": session.get("completed_at"),
            "completion_metadata": session.get("completion_metadata", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Error getting session status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session status: {str(e)}")
