from fastapi import APIRouter, HTTPException, Request, Depends
from src.backend.services.session_service import SessionService
from src.backend.services.user_service import UserService
from src.backend.services.transcript_service import TranscriptService
from src.backend.services.text_evaluation_service import TextEvaluationService
from src.backend.services.visual_evaluation_service import VisualEvaluationService
from src.backend.services.final_score_service import FinalScoreService
from src.backend.services.report_service import ReportService
from src.backend.utils.logger import setup_logger
from src.backend.services.analytics_service import AnalyticsService

logger = setup_logger(__name__)

router = APIRouter()

@router.get("/{session_id}")
def get_session_debug_data(
    session_id: str,
    request: Request
):
    
    logger.info(f"[Debug] GET /debug/{session_id} requested")
    
    user_id = UserService.get_user_id(request)
    
    AnalyticsService.record_event(
        event_name="debug_access",
        session_id=session_id,
        user_id=user_id,
        metadata={"endpoint": "get_session_debug_data"}
    )
    
    try:
        session = SessionService.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        if session.get("user_id") != user_id:
             raise HTTPException(status_code=403, detail="Unauthorized")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Debug] Error validating session: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    debug_data = {
        "session_metadata": session,
        "transcript": None,
        "text_evaluation": None,
        "visual_evaluation": None,
        "final_scores": None,
        "report": None,
        "audio_features": "Not implemented yet" # Placeholder
    }
    
    try:
        debug_data["transcript"] = TranscriptService.get_transcript(session_id)
    except Exception as e:
        debug_data["transcript"] = {"error": str(e)}
        
    try:
        debug_data["text_evaluation"] = TextEvaluationService.get_text_evaluation(session_id)
    except Exception as e:
        debug_data["text_evaluation"] = {"error": str(e)}
        
    try:
        debug_data["visual_evaluation"] = VisualEvaluationService.get_visual_evaluation(session_id)
    except Exception as e:
        debug_data["visual_evaluation"] = {"error": str(e)}
        
    try:
        debug_data["final_scores"] = FinalScoreService.get_all_parameter_scores(session_id)
    except Exception as e:
        debug_data["final_scores"] = {"error": str(e)}
        
    try:
        debug_data["report"] = ReportService.get_report(session_id)
    except Exception as e:
        debug_data["report"] = {"error": str(e)}
        
    return debug_data
