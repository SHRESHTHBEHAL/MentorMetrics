from src.backend.utils.supabase_client import supabase
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class FinalScoreService:
    @staticmethod
    def save_final_scores(
        session_id: str,
        fusion_scores_dict: dict,
        mentor_score: float,
        raw_data: dict = None
    ):
        
        if not session_id or not fusion_scores_dict:
            logger.error("Invalid input for save_final_scores")
            return None

        try:
            if not FinalScoreService.validate_session_exists(session_id):
                logger.error(f"Session {session_id} does not exist")
                return None
            
            logger.info(f"Saving final scores for session {session_id}")
            
            data = {
                "session_id": session_id,
                "engagement": float(fusion_scores_dict.get("engagement", 0.0)),
                "communication_clarity": float(fusion_scores_dict.get("communication_clarity", 0.0)),
                "technical_correctness": float(fusion_scores_dict.get("technical_correctness", 0.0)),
                "pacing_structure": float(fusion_scores_dict.get("pacing_structure", 0.0)),
                "interactive_quality": float(fusion_scores_dict.get("interactive_quality", 0.0)),
                "mentor_score": float(mentor_score),
                "raw_fusion_data": raw_data or {}
            }
            
            for key in ["engagement", "communication_clarity", "technical_correctness", 
                       "pacing_structure", "interactive_quality", "mentor_score"]:
                score = data[key]
                if not (0 <= score <= 10):
                    logger.warning(f"Score {key} out of range (0-10): {score}")
            
            response = supabase.table("final_scores").insert(data).execute()
            
            if response.data:
                logger.info(f"Final scores saved successfully for session {session_id}")
                logger.info(f"  Mentor Score: {mentor_score:.2f}/10")
                return response.data[0]['id']
            else:
                logger.warning(f"No rows inserted for final scores session {session_id}")
                return None
                
        except ValueError as e:
            logger.error(f"Value conversion error saving final scores for session {session_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"DB failure saving final scores for session {session_id}: {str(e)}")
            return None

    @staticmethod
    def get_final_scores(session_id: str):
        
        if not session_id:
            return None
            
        try:
            response = supabase.table("final_scores").select("*").eq("session_id", session_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                logger.info(f"Final scores not found for session {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching final scores for session {session_id}: {str(e)}")
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
    def get_mentor_score_only(session_id: str) -> float:
        
        scores = FinalScoreService.get_final_scores(session_id)
        
        if not scores:
            return None
        
        try:
            return float(scores.get("mentor_score", 0.0))
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def get_all_parameter_scores(session_id: str) -> dict:
        
        scores = FinalScoreService.get_final_scores(session_id)
        
        if not scores:
            return None
        
        return {
            "engagement": float(scores.get("engagement", 0.0)),
            "communication_clarity": float(scores.get("communication_clarity", 0.0)),
            "technical_correctness": float(scores.get("technical_correctness", 0.0)),
            "pacing_structure": float(scores.get("pacing_structure", 0.0)),
            "interactive_quality": float(scores.get("interactive_quality", 0.0)),
            "mentor_score": float(scores.get("mentor_score", 0.0))
        }
