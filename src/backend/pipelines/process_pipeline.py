import time
from datetime import datetime
from typing import Dict, Any, List
from src.backend.utils.logger import setup_logger
from src.backend.utils.config import Config
from src.backend.services.session_service import SessionService
from src.backend.services.transcript_service import TranscriptService
from src.backend.services.text_evaluation_service import TextEvaluationService
from src.backend.services.visual_evaluation_service import VisualEvaluationService
from src.backend.services.final_score_service import FinalScoreService
from src.backend.services.report_service import ReportService
from src.backend.pipelines.stt.stt_pipeline import stt_pipeline
from src.backend.pipelines.fusion.fusion_engine import compute_fusion_scores
from src.backend.pipelines.report.report_generator import generate_report

import os
from src.backend.services.audio_feature_service import AudioFeatureService
from src.backend.pipelines.audio.wpm_calculator import calculate_wpm
from src.backend.pipelines.audio.silence_detector import detect_silence_intervals
from src.backend.pipelines.audio.clarity_analyzer import analyze_audio_clarity
from src.backend.pipelines.audio.audio_scoring import compute_audio_scores
from src.backend.utils.audio_extractor import extract_audio_from_video

from src.backend.pipelines.visual.frame_extractor import extract_frames
from src.backend.pipelines.visual.mediapipe_detector import batch_analyze_frames, cleanup_detectors
from src.backend.pipelines.visual.engagement_analyzer import compute_engagement_metrics
from src.backend.pipelines.visual.visual_scoring import compute_visual_scores

logger = setup_logger(__name__)

def mark_stage_complete(session_id: str, stage_name: str):
    
    try:
        from src.backend.utils.supabase_client import supabase
        
        session = SessionService.get_session(session_id)
        stages = session.get("stages_completed", []) if session else []
        
        if stage_name not in stages:
            stages.append(stage_name)
            
            supabase.table("sessions").update({
                "stages_completed": stages,
                "last_successful_stage": stage_name
            }).eq("id", session_id).execute()
            
            logger.info(f"[TRACKING] Marked stage '{stage_name}' as complete")
    except Exception as e:
        logger.warning(f"[TRACKING] Failed to mark stage complete: {str(e)}")

def process_session(session_id: str) -> Dict[str, Any]:
    
    pipeline_start_time = time.time()
    stage_times = {}
    
    try:
        logger.info(f"=" * 80)
        logger.info(f"STARTING MENTORMETRICS PIPELINE FOR SESSION: {session_id}")
        logger.info(f"=" * 80)
        
        stage_start = time.time()
        logger.info("STAGE 1: Prepare - Loading session data")
        
        session = SessionService.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        SessionService.update_session_status(session_id, "processing")
        logger.info(f"Session loaded: {session.get('filename')}")
        
        stage_times["prepare"] = time.time() - stage_start
        
        stage_start = time.time()
        
        existing_transcript = TranscriptService.get_transcript(session_id)
        
        if existing_transcript:
            logger.info("STAGE 2: STT - Skipping: transcript already exists")
            logger.info(f"  Existing transcript: {len(existing_transcript.get('full_text', ''))} chars")
        else:
            logger.info("STAGE 2: STT - Running speech-to-text pipeline")
            
            stt_result = stt_pipeline(session_id)
            
            if stt_result.get("status") != "success":
                raise Exception(f"STT pipeline failed: {stt_result.get('error', 'Unknown error')}")
            
            logger.info("STT completed - Transcript saved")
            mark_stage_complete(session_id, "stt")
        
        stage_times["stt"] = time.time() - stage_start

        stage_start = time.time()
        
        existing_audio = AudioFeatureService.get_audio_features(session_id)
        
        if existing_audio:
            logger.info("STAGE 3: Audio Analysis - Skipping: audio evaluation already exists")
        else:
            logger.info("STAGE 3: Audio Analysis - Extracting audio features")
            
            try:
                video_path = os.path.join(Config.UPLOAD_DIR, session.get("filename"))
                
                if not os.path.exists(video_path):
                    logger.info(f"Video not found locally, downloading from Supabase: {session.get('filename')}")
                    try:
                        from src.backend.utils.supabase_client import supabase
                        os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
                        
                        data = supabase.storage.from_("videos").download(session.get("filename"))
                        
                        with open(video_path, "wb") as f:
                            f.write(data)
                        logger.info(f"Video downloaded to {video_path}")
                    except Exception as download_error:
                        logger.error(f"Failed to download video: {str(download_error)}")
                        raise FileNotFoundError(f"Video file not found locally or in storage: {video_path}")

                if not os.path.exists(video_path):
                    raise FileNotFoundError(f"Video file not found: {video_path}")
                
                audio_path = video_path.rsplit('.', 1)[0] + "_temp.wav"
                extract_audio_from_video(video_path, audio_path)
                logger.info(f"Audio extracted to {audio_path}")
                
                transcript_data = TranscriptService.get_transcript(session_id)
                wpm = calculate_wpm(transcript_data.get('segments', [])) if transcript_data else None
                logger.info(f"WPM calculated: {wpm}")
                
                silence_data = detect_silence_intervals(audio_path)
                logger.info(f"Silence detected: {silence_data.get('silence_ratio', 0):.2%}")
                
                clarity_data = analyze_audio_clarity(audio_path)
                logger.info(f"Clarity analyzed: {clarity_data.get('clarity_score', 0)}")
                
                audio_scores = compute_audio_scores(wpm, silence_data, clarity_data)
                
                AudioFeatureService.save_audio_features(session_id, audio_scores)
                
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    
                mark_stage_complete(session_id, "audio")
                
            except Exception as e:
                logger.error(f"Audio analysis failed: {str(e)}")
                raise e
        
        stage_times["audio"] = time.time() - stage_start
        
        stage_start = time.time()
        
        existing_visual = VisualEvaluationService.get_visual_evaluation(session_id)
        
        if existing_visual:
            logger.info("STAGE 4: Visual Analysis - Skipping: visual evaluation already exists")
            logger.info(f"  Existing visual score: {existing_visual.get('visual_overall', 'N/A')}")
        else:
            logger.info("STAGE 4: Visual Analysis - Processing video frames")
            
            try:
                video_path = os.path.join(Config.UPLOAD_DIR, session.get("filename"))
                
                frames = extract_frames(video_path, fps=1, max_frames=60)
                logger.info(f"Extracted {len(frames)} frames for analysis")
                
                frame_results = batch_analyze_frames(frames)
                
                engagement_metrics = compute_engagement_metrics(frame_results)
                
                visual_scores = compute_visual_scores(engagement_metrics)
                
                VisualEvaluationService.save_visual_evaluation(session_id, visual_scores)
                
                cleanup_detectors()
                
                mark_stage_complete(session_id, "visual")
                
            except Exception as e:
                logger.error(f"Visual analysis failed: {str(e)}")
                cleanup_detectors()
                raise e
        
        stage_times["visual"] = time.time() - stage_start
        
        stage_start = time.time()
        
        existing_text = TextEvaluationService.get_text_evaluation(session_id)
        
        if existing_text:
            logger.info("STAGE 5: Text Analysis - Skipping: text evaluation already exists")
            logger.info(f"  Existing clarity score: {existing_text.get('clarity_score', 'N/A')}")
        else:
            logger.info("STAGE 5: Text Analysis - Already completed in STT pipeline")
        
        stage_times["text"] = time.time() - stage_start
        
        stage_start = time.time()
        
        existing_scores = FinalScoreService.get_final_scores(session_id)
        
        if existing_scores:
            logger.info("STAGE 6: Fusion - Skipping: final scores already exist")
            logger.info(f"  Existing mentor score: {existing_scores.get('mentor_score', 'N/A')}/10")
            mentor_score = existing_scores.get("mentor_score", 7.5)
        else:
            logger.info("STAGE 6: Fusion - Computing multimodal scores")
            
            audio_eval = AudioFeatureService.get_audio_features(session_id)
            audio_scores = {}
            if audio_eval:
                audio_scores = {
                    "wpm_score": float(audio_eval.get("wpm_score", 0)),
                    "silence_score": float(audio_eval.get("silence_score", 0)),
                    "clarity_score": float(audio_eval.get("clarity_score", 0)),
                    "audio_overall": float(audio_eval.get("audio_overall", 0))
                }
            
            text_eval = TextEvaluationService.get_text_evaluation(session_id)
            text_scores = {}
            if text_eval:
                text_scores = {
                    "clarity_score": float(text_eval.get("clarity_score", 0)),
                    "structure_score": float(text_eval.get("structure_score", 0)),
                    "technical_correctness_score": float(text_eval.get("technical_correctness_score", 0)),
                    "explanation_quality_score": float(text_eval.get("explanation_quality_score", 0))
                }
            
            visual_eval = VisualEvaluationService.get_visual_evaluation(session_id)
            visual_scores = {}
            if visual_eval:
                visual_scores = {
                    "face_visibility_score": float(visual_eval.get("face_visibility_score", 0)),
                    "gaze_forward_score": float(visual_eval.get("gaze_forward_score", 0)),
                    "gesture_score": float(visual_eval.get("gesture_score", 0)),
                    "movement_score": float(visual_eval.get("movement_score", 0)),
                    "visual_overall": float(visual_eval.get("visual_overall", 0))
                }
            
            fusion_result = compute_fusion_scores(audio_scores, text_scores, visual_scores)
            
            mentor_score = fusion_result.get("mentor_score", fusion_result.get("overall_score", 0.0))
            
            FinalScoreService.save_final_scores(
                session_id,
                fusion_result["final_scores"],
                mentor_score,
                fusion_result["metadata"]
            )
            
            mark_stage_complete(session_id, "fusion")
        
        stage_times["fusion"] = time.time() - stage_start
        
        stage_start = time.time()
        
        existing_report = ReportService.get_report(session_id)
        
        if existing_report:
            logger.info("STAGE 7: Report - Skipping: report already exists")
            logger.info(f"  Existing report summary: {len(existing_report.get('summary', ''))} chars")
        else:
            logger.info("STAGE 7: Report - Generating improvement report")
            
            report = generate_report(session_id)
            
            if report and not report.get("raw_response", {}).get("fallback"):
                logger.info("Report generation successful")
            else:
                logger.warning("Report generation used fallback or failed")
                
            mark_stage_complete(session_id, "report")
        
        stage_times["report"] = time.time() - stage_start
        
        stage_start = time.time()
        logger.info("STAGE 8: Complete - Finalizing session")
        
        pipeline_duration = time.time() - pipeline_start_time
        
        completion_metadata = {
            "mentor_score": mentor_score,
            "finished_at": datetime.utcnow().isoformat(),
            "pipeline_stages": {
                "prepare_time_sec": round(stage_times.get("prepare", 0), 2),
                "stt_time_sec": round(stage_times.get("stt", 0), 2),
                "audio_time_sec": round(stage_times.get("audio", 0), 2),
                "visual_time_sec": round(stage_times.get("visual", 0), 2),
                "text_time_sec": round(stage_times.get("text", 0), 2),
                "fusion_time_sec": round(stage_times.get("fusion", 0), 2),
                "report_time_sec": round(stage_times.get("report", 0), 2),
                "total_time_sec": round(pipeline_duration, 2)
            },
            "model_versions": {
                "whisper": Config.WHISPER_MODEL,
                "llm": Config.LLM_MODEL
            },
            "runtime_diagnostics": {
                "total_duration_sec": round(pipeline_duration, 2),
                "video_filename": session.get("filename", ""),
                "completed_successfully": True
            }
        }
        
        SessionService.mark_session_completed(session_id, completion_metadata)
        mark_stage_complete(session_id, "complete")
        
        stage_times["complete"] = time.time() - stage_start
        
        logger.info(f"=" * 80)
        logger.info(f"PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"Session ID: {session_id}")
        logger.info(f"Mentor Score: {mentor_score:.2f}/10")
        logger.info(f"Total Duration: {pipeline_duration:.2f}s")
        logger.info(f"Stage Breakdown:")
        for stage, duration in stage_times.items():
            logger.info(f"  - {stage.capitalize()}: {duration:.2f}s")
        logger.info(f"=" * 80)
        
        return {
            "status": "complete",
            "session_id": session_id,
            "mentor_score": mentor_score,
            "duration_sec": pipeline_duration
        }
    
    except Exception as e:
        logger.error(f"=" * 80)
        logger.error(f"PIPELINE FAILED FOR SESSION: {session_id}")
        logger.error(f"Error: {str(e)}")
        logger.error(f"=" * 80)
        
        try:
            SessionService.update_session_status(session_id, "failed")
            
            error_metadata = {
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat(),
                "pipeline_stages": stage_times,
                "partial_completion": True
            }
            
            SessionService.mark_session_completed(session_id, error_metadata)
        except Exception as meta_error:
            logger.error(f"Failed to save error metadata: {str(meta_error)}")
        
        return {
            "status": "failed",
            "session_id": session_id,
            "error": str(e)
        }

__all__ = ['process_session']
