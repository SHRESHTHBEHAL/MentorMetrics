from src.backend.utils.supabase_client import supabase
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class VisualEvaluationService:
    @staticmethod
    def save_visual_evaluation(
        session_id: str,
        visual_scores_dict: dict,
        raw_data: dict = None
    ):
        
        if not session_id or not visual_scores_dict:
            logger.error("Invalid input for save_visual_evaluation")
            return None

        try:
            logger.info(f"Saving visual evaluation for session {session_id}")
            
            data = {
                "session_id": session_id,
                "face_visibility_score": float(visual_scores_dict.get("face_visibility_score", 0.0)),
                "gaze_forward_score": float(visual_scores_dict.get("gaze_forward_score", 0.0)),
                "gesture_score": float(visual_scores_dict.get("gesture_score", 0.0)),
                "movement_score": float(visual_scores_dict.get("movement_score", 0.0)),
                "visual_overall": float(visual_scores_dict.get("visual_overall", 0.0)),
                "raw_visual_data": raw_data or {}
            }
            
            for key in ["face_visibility_score", "gaze_forward_score", "gesture_score", "movement_score", "visual_overall"]:
                score = data[key]
                if not (0 <= score <= 10):
                    logger.warning(f"Score {key} out of range (0-10): {score}")
            
            response = supabase.table("visual_evaluations").insert(data).execute()
            
            if response.data:
                logger.info(f"Visual evaluation saved successfully for session {session_id}")
                return response.data[0]['id']
            else:
                logger.warning(f"No rows inserted for visual evaluation session {session_id}")
                return None
                
        except ValueError as e:
            logger.error(f"Value conversion error saving visual evaluation for session {session_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"DB failure saving visual evaluation for session {session_id}: {str(e)}")
            return None

    @staticmethod
    def get_visual_evaluation(session_id: str):
        
        if not session_id:
            return None
            
        try:
            response = supabase.table("visual_evaluations").select("*").eq("session_id", session_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                logger.info(f"Visual evaluation not found for session {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching visual evaluation for session {session_id}: {str(e)}")
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
    def get_all_visual_scores(session_id: str) -> dict:
        
        evaluation = VisualEvaluationService.get_visual_evaluation(session_id)
        
        if not evaluation:
            return None
        
        return {
            "face_visibility_score": float(evaluation.get("face_visibility_score", 0.0)),
            "gaze_forward_score": float(evaluation.get("gaze_forward_score", 0.0)),
            "gesture_score": float(evaluation.get("gesture_score", 0.0)),
            "movement_score": float(evaluation.get("movement_score", 0.0)),
            "visual_overall": float(evaluation.get("visual_overall", 0.0))
        }
