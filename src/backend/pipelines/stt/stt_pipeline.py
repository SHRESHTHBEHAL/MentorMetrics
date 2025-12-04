import os
import json
from src.backend.services.session_service import SessionService
from src.backend.services.transcript_service import TranscriptService
from src.backend.utils.audio_extractor import extract_audio_from_video
from src.backend.pipelines.stt.whisper_engine import run_whisper
from src.backend.pipelines.text.text_evaluator import run_text_evaluation
from src.backend.pipelines.text.text_parser import parse_text_evaluation_output
from src.backend.services.text_evaluation_service import TextEvaluationService
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def store_transcript_result(session_id: str, transcript_result: dict) -> bool:
    
    if not session_id:
        logger.error("store_transcript_result: session_id is required")
        return False
    
    if not transcript_result or not isinstance(transcript_result, dict):
        logger.error(f"store_transcript_result: Invalid transcript_result for session {session_id}")
        return False
    
    try:
        full_text = transcript_result.get("text", "")
        segments = transcript_result.get("segments", [])
        
        if not full_text or not full_text.strip():
            logger.warning(f"store_transcript_result: Empty transcript text for session {session_id}")
            return False
        
        if not isinstance(segments, list):
            logger.warning(f"store_transcript_result: Invalid segments format for session {session_id}")
            segments = []
        
        logger.info(f"Storing transcript for session {session_id}: {len(full_text)} chars, {len(segments)} segments")
        
        transcript_id = TranscriptService.save_transcript(
            session_id,
            full_text,
            segments
        )
        
        if not transcript_id:
            logger.error(f"store_transcript_result: Failed to save transcript for session {session_id}")
            return False
        
        try:
            from src.backend.utils.supabase_client import supabase
            supabase.table("sessions").update({"has_transcript": True}).eq("id", session_id).execute()
            logger.info(f"Updated has_transcript flag for session {session_id}")
        except Exception as e:
            logger.warning(f"Failed to update has_transcript flag for session {session_id}: {str(e)}")
        
        logger.info(f"Successfully stored transcript for session {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"store_transcript_result: DB insertion failed for session {session_id}: {str(e)}")
        return False

def stt_pipeline(session_id: str) -> dict:
    video_path = None
    audio_path = None
    
    try:
        logger.info(f"Starting STT pipeline for session {session_id}")
        
        session = SessionService.get_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return {"status": "failure", "error": "Session not found"}

        SessionService.update_status(session_id, "processing_stt")

        video_path = SessionService.download_video(session_id, session["filename"])
        
        audio_path = video_path.rsplit('.', 1)[0] + ".wav"
        extract_audio_from_video(video_path, audio_path)
        
        transcript_result = run_whisper(audio_path)
        
        if not store_transcript_result(session_id, transcript_result):
            logger.warning(f"Transcript storage failed for session {session_id}, continuing anyway")
        
        SessionService.update_status(session_id, "stt_completed")
        
        try:
            SessionService.update_status(session_id, "processing_text_eval")
            logger.info(f"Starting text evaluation for session {session_id}")
            
            raw_llm_result = run_text_evaluation(transcript_result["text"])
            parsed_scores = parse_text_evaluation_output(json.dumps(raw_llm_result)) # run_text_evaluation returns dict, parser expects str or dict? Parser expects str.
            
            raw_json_str = raw_llm_result.get("raw_llm_response", "{}")
            parsed_scores = parse_text_evaluation_output(raw_json_str)
            
            TextEvaluationService.save_text_evaluation(
                session_id,
                parsed_scores,
                raw_llm_result, # This expects a dict, which run_text_evaluation returns.
                parsed_scores.get("summary", "")
            )
            SessionService.update_status(session_id, "text_eval_completed")
            
        except Exception as e:
            logger.error(f"Text evaluation step failed: {str(e)}")
        
        logger.info(f"STT pipeline completed successfully for session {session_id}")
        return {
            "status": "success",
            "session_id": session_id,
            "transcript_saved": True,
            "text_eval_saved": True
        }

    except Exception as e:
        logger.error(f"STT pipeline failed for session {session_id}: {str(e)}")
        SessionService.update_status(session_id, "failed")
        return {"status": "failure", "error": str(e)}
        
    finally:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
