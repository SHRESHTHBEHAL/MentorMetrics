import json
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def parse_text_evaluation_output(raw_output: str) -> dict:
    
    default_response = {
        "clarity_score": 0.0,
        "structure_score": 0.0,
        "technical_correctness_score": 0.0,
        "explanation_quality_score": 0.0,
        "summary": "Evaluation failed due to model error.",
        "raw": {}
    }

    if not raw_output:
        logger.error("Text Parser: Empty raw output received")
        return default_response

    try:
        cleaned_output = raw_output.strip()
        if cleaned_output.startswith("```json"):
            cleaned_output = cleaned_output[7:]
        elif cleaned_output.startswith("```"):
            cleaned_output = cleaned_output[3:]
        
        if cleaned_output.endswith("```"):
            cleaned_output = cleaned_output[:-3]
            
        cleaned_output = cleaned_output.strip()

        parsed = json.loads(cleaned_output)
        
        required_keys = [
            "clarity_score", 
            "structure_score", 
            "technical_correctness_score", 
            "explanation_quality_score", 
            "summary"
        ]
        
        missing_keys = [key for key in required_keys if key not in parsed]
        if missing_keys:
            logger.error(f"Text Parser: Missing keys in JSON: {missing_keys}")
            default_response["raw"] = parsed
            return default_response

        validated = {}
        for key in required_keys:
            if key == "summary":
                summary = str(parsed[key]).strip()
                validated[key] = summary
            else:
                try:
                    score = float(parsed[key])
                    score = max(0.0, min(10.0, score))
                    validated[key] = round(score, 2)
                except (ValueError, TypeError):
                    logger.error(f"Text Parser: Invalid score format for {key}: {parsed[key]}")
                    validated[key] = 0.0
        
        validated["raw"] = parsed
        return validated

    except json.JSONDecodeError as e:
        logger.error(f"Text Parser: Malformed JSON: {str(e)}")
        default_response["raw"] = {"error": "Malformed JSON", "content": raw_output}
        return default_response
    except Exception as e:
        logger.error(f"Text Parser: Unexpected error: {str(e)}")
        default_response["raw"] = {"error": str(e), "content": raw_output}
        return default_response
