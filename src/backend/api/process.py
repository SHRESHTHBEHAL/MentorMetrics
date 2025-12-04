from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Depends
from src.backend.services.pipeline_runner import run_full_pipeline_async
from src.backend.services.session_service import SessionService
from src.backend.services.user_service import UserService
from src.backend.services.analytics_service import AnalyticsService
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.post("/{session_id}")
def process_session_endpoint(
    session_id: str, 
    background_tasks: BackgroundTasks,
    request: Request
):
    
    logger.info(f"[API] POST /process/{session_id} - Pipeline processing requested")
    
    user_id = UserService.get_user_id(request)
    
    try:
        session = SessionService.get_session(session_id)
        if not session:
            logger.error(f"[API] Session {session_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
            
        if session.get("user_id") != user_id:
            logger.warning(f"[API] User {user_id} attempted to process session {session_id} owned by {session.get('user_id')}")
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this session"
            )
        
        logger.info(f"[API] Session validated: {session.get('filename')}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Error validating session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Session validation failed: {str(e)}"
        )
    
    current_status = session.get("status", "uploaded")
    
    if current_status == "processing":
        logger.warning(f"[API] Session {session_id} is already being processed")
        return {
            "status": "already_processing",
            "session_id": session_id,
            "message": "Session is already being processed. Please wait for completion."
        }
    
    if current_status == "complete":
        logger.warning(f"[API] Session {session_id} is already complete")
        return {
            "status": "already_complete",
            "session_id": session_id,
            "message": "Session has already been processed. Results are available."
        }
    
    try:
        success = SessionService.update_session_status(session_id, "processing")
        if not success:
            logger.error(f"[API] Failed to update session {session_id} status to 'processing'")
            raise HTTPException(
                status_code=500,
                detail="Failed to update session status"
            )
        
        logger.info(f"[API] Session {session_id} status set to 'processing'")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Error updating session status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update session status: {str(e)}"
        )
    
    logger.info(f"[API] Queueing pipeline job for session {session_id}")
    
    try:
        background_tasks.add_task(run_full_pipeline_async, session_id)
        logger.info(f"[API] Pipeline job queued successfully for session {session_id}")
        
        AnalyticsService.record_event(
            event_name="pipeline_start",
            session_id=session_id,
            user_id=user_id,
            metadata={"trigger": "manual_process"}
        )
        
    except Exception as e:
        logger.error(f"[API] Failed to queue pipeline job: {str(e)}")
        try:
            SessionService.update_session_status(session_id, "uploaded")
        except:
            pass
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue processing job: {str(e)}"
        )
    
    logger.info(f"[API] Returning success response for session {session_id}")
    
    return {
        "status": "processing_started",
        "session_id": session_id,
        "message": "Pipeline processing started in background. Poll session status for completion."
    }

@router.get("/status/{session_id}")
def get_session_status_endpoint(
    session_id: str,
    request: Request
):
    
    logger.info(f"[API] GET /status/{session_id} - Status check requested")
    
    user_id = UserService.get_user_id(request)
    
    from src.backend.utils.cache import get_cache, set_cache, clear_cache
    cache_key = f"status:{session_id}"
    cached_status = get_cache(cache_key)
    
    if cached_status:
        logger.info(f"[API] Cache hit for status: {session_id}")
        return cached_status
    
    try:
        status_info = SessionService.get_session_status(session_id)
        
        if not status_info:
            logger.error(f"[API] Session {session_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
            
        if status_info.get("user_id") != user_id:
            logger.warning(f"[API] User {user_id} attempted to access session {session_id} owned by {status_info.get('user_id')}")
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this session"
            )
        
        logger.info(f"[API] Session {session_id} status: {status_info.get('status')}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Error fetching session status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch session status: {str(e)}"
        )
    
    current_status = status_info.get("status", "unknown")
    
    progress = {
        "percentage": 0,
        "current_stage": "Not started"
    }
    
    if current_status == "uploaded":
        progress = {"percentage": 0, "current_stage": "Uploaded - Ready for processing"}
    elif current_status == "processing":
        completion_meta = status_info.get("metadata", {}).get("completion_metadata", {})
        pipeline_stages = completion_meta.get("pipeline_stages", {})
        
        if pipeline_stages:
            completed_stages = sum(1 for v in pipeline_stages.values() if isinstance(v, (int, float)) and v > 0)
            total_stages = 7  # Total pipeline stages
            progress_pct = int((completed_stages / total_stages) * 100)
            progress = {
                "percentage": min(progress_pct, 90),  # Cap at 90% until complete
                "current_stage": "Processing pipeline stages"
            }
        else:
            progress = {"percentage": 50, "current_stage": "Processing in progress"}
    elif current_status == "complete":
        progress = {"percentage": 100, "current_stage": "Complete"}
    elif current_status == "failed":
        progress = {"percentage": 0, "current_stage": "Failed"}
    
    response_metadata = status_info.get("metadata", {})
    response_metadata["stages_completed"] = status_info.get("stages_completed", [])

    response = {
        "session_id": status_info["session_id"],
        "status": current_status,
        "filename": status_info.get("filename", ""),
        "has_transcript": status_info.get("has_transcript", False),
        "progress": progress,
        "metadata": response_metadata
    }
    
    logger.info(f"[API] Returning status response for session {session_id}")
    
    if current_status in ["complete", "failed"]:
        set_cache(cache_key, response, ttl_seconds=300) # 5 minutes
    elif current_status == "processing":
        set_cache(cache_key, response, ttl_seconds=2) # 2 seconds to allow some buffering but keep UI live
        
    return response

@router.post("/restart/{session_id}")
def restart_session_endpoint(
    session_id: str, 
    background_tasks: BackgroundTasks,
    request: Request
):
    
    logger.info(f"[API] POST /restart/{session_id} - Session restart requested")
    
    user_id = UserService.get_user_id(request)
    
    try:
        session = SessionService.get_session(session_id)
        if not session:
            logger.error(f"[API] Session {session_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
            
        if session.get("user_id") != user_id:
            logger.warning(f"[API] User {user_id} attempted to restart session {session_id} owned by {session.get('user_id')}")
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this session"
            )
        
        logger.info(f"[API] Session validated: {session.get('filename')}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Error validating session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Session validation failed: {str(e)}"
        )
    
    logger.info(f"[API] Cleaning previous evaluation data for session {session_id}")
    
    from src.backend.utils.cache import clear_cache
    clear_cache(f"results:{session_id}")
    clear_cache(f"status:{session_id}")
    
    try:
        from src.backend.utils.supabase_client import supabase
        
        deleted_count = 0
        
        try:
            result = supabase.table("transcripts").delete().eq("session_id", session_id).execute()
            if result.data:
                deleted_count += len(result.data)
                logger.info(f"[API] Deleted {len(result.data)} transcript records")
        except Exception as e:
            logger.warning(f"[API] Error deleting transcripts: {str(e)}")
        
        try:
            result = supabase.table("text_evaluations").delete().eq("session_id", session_id).execute()
            if result.data:
                deleted_count += len(result.data)
                logger.info(f"[API] Deleted {len(result.data)} text evaluation records")
        except Exception as e:
            logger.warning(f"[API] Error deleting text evaluations: {str(e)}")
        
        try:
            result = supabase.table("visual_evaluations").delete().eq("session_id", session_id).execute()
            if result.data:
                deleted_count += len(result.data)
                logger.info(f"[API] Deleted {len(result.data)} visual evaluation records")
        except Exception as e:
            logger.warning(f"[API] Error deleting visual evaluations: {str(e)}")
        
        try:
            result = supabase.table("final_scores").delete().eq("session_id", session_id).execute()
            if result.data:
                deleted_count += len(result.data)
                logger.info(f"[API] Deleted {len(result.data)} final score records")
        except Exception as e:
            logger.warning(f"[API] Error deleting final scores: {str(e)}")
        
        try:
            result = supabase.table("reports").delete().eq("session_id", session_id).execute()
            if result.data:
                deleted_count += len(result.data)
                logger.info(f"[API] Deleted {len(result.data)} report records")
        except Exception as e:
            logger.warning(f"[API] Error deleting reports: {str(e)}")
        
        logger.info(f"[API] Cleaned {deleted_count} evaluation records total")
        
    except Exception as e:
        logger.error(f"[API] Error cleaning evaluation data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clean previous evaluation data: {str(e)}"
        )
    
    logger.info(f"[API] Resetting session metadata")
    
    try:
        from src.backend.utils.supabase_client import supabase
        
        supabase.table("sessions").update({
            "status": "pending",
            "has_transcript": False,
            "stages_completed": [],
            "last_successful_stage": None,
            "completed_at": None,
            "completion_metadata": None
        }).eq("id", session_id).execute()
        
        logger.info(f"[API] Session {session_id} reset to pending state")
        
    except Exception as e:
        logger.error(f"[API] Error resetting session metadata: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset session metadata: {str(e)}"
        )
    
    logger.info(f"[API] Queueing pipeline for reprocessing")
    
    try:
        background_tasks.add_task(run_full_pipeline_async, session_id)
        background_tasks.add_task(run_full_pipeline_async, session_id)
        logger.info(f"[API] Pipeline queued successfully")
        
        AnalyticsService.record_event(
            event_name="pipeline_restart",
            session_id=session_id,
            user_id=user_id,
            metadata={"trigger": "manual_restart"}
        )
        
    except Exception as e:
        logger.error(f"[API] Failed to queue pipeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue processing: {str(e)}"
        )
    
    logger.info(f"[API] Session {session_id} restart complete - processing started")
    
    return {
        "status": "restarted",
        "session_id": session_id,
        "message": "Pipeline restarted successfully. All previous data has been cleaned and processing has started from the beginning."
    }
