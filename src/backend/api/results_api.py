from fastapi import APIRouter, HTTPException, Request, Depends
from src.backend.services.session_service import SessionService
from src.backend.services.transcript_service import TranscriptService
from src.backend.services.text_evaluation_service import TextEvaluationService
from src.backend.services.visual_evaluation_service import VisualEvaluationService
from src.backend.services.final_score_service import FinalScoreService
from src.backend.services.report_service import ReportService
from src.backend.services.user_service import UserService
from src.backend.services.analytics_service import AnalyticsService
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.get("/{session_id}")
def get_session_results(
    session_id: str,
    request: Request
):
    
    logger.info(f"[API] GET /results/{session_id} - Results requested")
    
    user_id = UserService.get_user_id(request)
    
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
        
        logger.info(f"[API] Session validated: {status_info.get('status')}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Error validating session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Session validation failed: {str(e)}"
        )
    
    session_status = status_info.get("status", "unknown")
    
    if session_status != "complete":
        logger.warning(f"[API] Session {session_id} not complete yet (status: {session_status})")
        return {
            "status": "processing",
            "message": "Processing not finished yet. Please check back later.",
            "session_id": session_id,
            "current_status": session_status
        }
    
    from src.backend.utils.cache import get_cache, set_cache
    cache_key = f"results:{session_id}"
    cached_results = get_cache(cache_key)
    
    if cached_results:
        logger.info(f"[API] Cache hit for results: {session_id}")
        return cached_results

    logger.info(f"[API] Fetching all evaluation data for session {session_id}")
    
    results = {
        "session_id": session_id,
        "status": "complete",
        "filename": status_info.get("filename", "")
    }
    
    try:
        final_scores = FinalScoreService.get_all_parameter_scores(session_id)
        if final_scores:
            results["scores"] = final_scores
            logger.info(f"[API] Final scores retrieved: mentor_score={final_scores.get('mentor_score', 'N/A')}")
        else:
            results["scores"] = None
            logger.warning(f"[API] No final scores found for session {session_id}")
    except Exception as e:
        logger.error(f"[API] Error fetching final scores: {str(e)}")
        results["scores"] = None
    
    try:
        report = ReportService.get_report(session_id)
        if report:
            results["report"] = {
                "summary": report.get("summary", ""),
                "strengths": report.get("strengths", []),
                "improvements": report.get("improvements", []),
                "actionable_tips": report.get("actionable_tips", [])
            }
            logger.info(f"[API] Report retrieved")
        else:
            results["report"] = None
            logger.warning(f"[API] No report found for session {session_id}")
    except Exception as e:
        logger.error(f"[API] Error fetching report: {str(e)}")
        results["report"] = None
    
    try:
        transcript = TranscriptService.get_transcript(session_id)
        if transcript:
            results["transcript"] = {
                "text": transcript.get("full_text", ""),
                "segments": transcript.get("segments", [])
            }
            logger.info(f"[API] Transcript retrieved ({len(transcript.get('full_text', ''))} chars)")
        else:
            results["transcript"] = None
            logger.warning(f"[API] No transcript found for session {session_id}")
    except Exception as e:
        logger.error(f"[API] Error fetching transcript: {str(e)}")
        results["transcript"] = None
    
    try:
        text_eval = TextEvaluationService.get_text_evaluation(session_id)
        if text_eval:
            results["text"] = {
                "clarity_score": text_eval.get("clarity_score"),
                "structure_score": text_eval.get("structure_score"),
                "technical_correctness_score": text_eval.get("technical_correctness_score"),
                "explanation_quality_score": text_eval.get("explanation_quality_score"),
                "summary_feedback": text_eval.get("summary_feedback", "")
            }
            logger.info(f"[API] Text evaluation retrieved")
        else:
            results["text"] = None
            logger.warning(f"[API] No text evaluation found for session {session_id}")
    except Exception as e:
        logger.error(f"[API] Error fetching text evaluation: {str(e)}")
        results["text"] = None
    
    try:
        visual_eval = VisualEvaluationService.get_visual_evaluation(session_id)
        if visual_eval:
            results["visual"] = {
                "face_visibility_score": visual_eval.get("face_visibility_score"),
                "gaze_forward_score": visual_eval.get("gaze_forward_score"),
                "gesture_score": visual_eval.get("gesture_score"),
                "movement_score": visual_eval.get("movement_score"),
                "visual_overall": visual_eval.get("visual_overall")
            }
            logger.info(f"[API] Visual evaluation retrieved")
        else:
            results["visual"] = None
            logger.warning(f"[API] No visual evaluation found for session {session_id}")
    except Exception as e:
        logger.error(f"[API] Error fetching visual evaluation: {str(e)}")
        results["visual"] = None
    
    try:
        from src.backend.services.audio_feature_service import AudioFeatureService
        audio_eval = AudioFeatureService.get_audio_features(session_id)
        if audio_eval:
            wpm = audio_eval.get("words_per_minute")
            silence_ratio = audio_eval.get("silence_ratio")
            clarity_score = audio_eval.get("clarity_score")
            
            wpm_score = None
            if wpm is not None:
                if 120 <= wpm <= 150:
                    wpm_score = 10.0
                elif wpm > 150:
                    wpm_score = max(0.0, 10.0 - (wpm - 150) * 0.2)
                else:
                    wpm_score = max(0.0, 10.0 - (120 - wpm) * 0.1)
                wpm_score = round(wpm_score, 2)
            
            silence_score = None
            if silence_ratio is not None:
                if silence_ratio <= 0.15:
                    silence_score = 10.0
                else:
                    silence_score = max(0.0, 10.0 - (silence_ratio - 0.15) * 20)
                silence_score = round(silence_score, 2)
            
            audio_overall = None
            if wpm_score is not None and silence_score is not None and clarity_score is not None:
                audio_overall = round(
                    (wpm_score * 0.4) + (silence_score * 0.2) + (clarity_score * 0.4),
                    2
                )
            
            results["audio"] = {
                "wpm": wpm,
                "wpm_score": wpm_score,
                "silence_ratio": silence_ratio,
                "silence_score": silence_score,
                "clarity_score": clarity_score,
                "audio_overall": audio_overall
            }
            logger.info(f"[API] Audio evaluation retrieved: wpm={wpm}, audio_overall={audio_overall}")
        else:
            results["audio"] = None
            logger.warning(f"[API] No audio evaluation found for session {session_id}")
    except Exception as e:
        logger.error(f"[API] Error fetching audio evaluation: {str(e)}")
        results["audio"] = None
    
    logger.info(f"[API] Successfully compiled results for session {session_id}")
    logger.info(f"[API] Available data: scores={results['scores'] is not None}, "
                f"report={results['report'] is not None}, "
                f"transcript={results['transcript'] is not None}, "
                f"text={results['text'] is not None}, "
                f"visual={results['visual'] is not None}")
    
    AnalyticsService.record_event(
        event_name="results_viewed",
        session_id=session_id,
        user_id=user_id,
        metadata={"has_scores": results['scores'] is not None}
    )
    
    set_cache(cache_key, results, ttl_seconds=600)
    
    return results
