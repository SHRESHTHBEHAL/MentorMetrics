from src.backend.utils.supabase_client import supabase
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class TextEvaluationService:
    @staticmethod
    def save_text_evaluation(session_id: str, scores_dict: dict, raw_response: dict, summary: str):
        if not session_id or not scores_dict:
            logger.error("Invalid input for save_text_evaluation")
            return None

        try:
            logger.info(f"Saving text evaluation for session {session_id}")
            
            data = {
                "session_id": session_id,
                "clarity_score": scores_dict.get("clarity_score"),
                "structure_score": scores_dict.get("structure_score"),
                "technical_correctness_score": scores_dict.get("technical_correctness_score"),
                "explanation_quality_score": scores_dict.get("explanation_quality_score"),
                "raw_llm_response": raw_response,
                "summary_feedback": summary
            }
            
            for key, value in scores_dict.items():
                if not isinstance(value, (int, float)):
                    logger.warning(f"Invalid score type for {key}: {value}")
            
            response = supabase.table("text_evaluations").insert(data).execute()
            
            if response.data:
                logger.info(f"Text evaluation saved successfully for session {session_id}")
                return response.data[0]['id']
            else:
                logger.warning(f"No rows inserted for text evaluation session {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"DB failure saving text evaluation for session {session_id}: {str(e)}")
            return None

    @staticmethod
    def get_text_evaluation(session_id: str):
        if not session_id:
            return None
            
        try:
            response = supabase.table("text_evaluations").select("*").eq("session_id", session_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                logger.info(f"Text evaluation not found for session {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching text evaluation for session {session_id}: {str(e)}")
            return None
