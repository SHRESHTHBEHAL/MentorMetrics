import json
import time
import google.generativeai as genai
from src.backend.utils.logger import setup_logger
from src.backend.utils.config import Config
from src.backend.pipelines.text.text_prompt_template import build_text_evaluation_prompt

logger = setup_logger(__name__)

def run_text_evaluation(transcript: str) -> dict:
    if not transcript:
        logger.warning("Empty transcript provided for text evaluation")
        return _get_fallback_response("Empty transcript")

    api_key = Config.GEMINI_API_KEY
    if not api_key:
        logger.warning("GEMINI_API_KEY not found. Skipping text evaluation.")
        return _get_fallback_response("Missing API Key")

    try:
        genai.configure(api_key=api_key)
        model_name = Config.LLM_MODEL # e.g., "gemini-1.5-flash"
        model = genai.GenerativeModel(model_name)
        
        prompt = build_text_evaluation_prompt(transcript)
        
        logger.info(f"Starting text evaluation with Gemini model {model_name}")
        start_time = time.time()
        
        generation_config = genai.types.GenerationConfig(
            temperature=0.0,
            max_output_tokens=1000,
        )
        
        response = model.generate_content(prompt, generation_config=generation_config)
        
        duration = time.time() - start_time
        content = response.text
        
        logger.info(f"Gemini response received in {duration:.2f}s. Parsing JSON...")
        
        cleaned_content = content.replace("```json", "").replace("```", "").strip()
        
        try:
            result = json.loads(cleaned_content)
            
            required_keys = ["clarity_score", "structure_score", "technical_correctness_score", "explanation_quality_score", "summary"]
            missing_keys = [key for key in required_keys if key not in result]
            
            if missing_keys:
                raise ValueError(f"Missing keys in JSON response: {missing_keys}")
            
            result["raw_llm_response"] = content
            
            logger.info("Text evaluation successfully parsed.")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            return _get_fallback_response(f"JSON Parse Error: {str(e)}")
        except ValueError as e:
            logger.error(f"Validation failed: {str(e)}")
            return _get_fallback_response(f"Validation Error: {str(e)}")

    except Exception as e:
        logger.error(f"Text evaluation failed: {str(e)}")
        return _get_fallback_response(str(e))

def _get_fallback_response(error_message: str) -> dict:
    return {
        "clarity_score": 0.0,
        "structure_score": 0.0,
        "technical_correctness_score": 0.0,
        "explanation_quality_score": 0.0,
        "summary": f"Evaluation failed due to error: {error_message}",
        "raw_llm_response": "{}"
    }
