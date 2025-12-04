import json
import time
import google.generativeai as genai
from typing import Dict, Any, Optional
from src.backend.utils.logger import setup_logger
from src.backend.utils.config import Config
from src.backend.services.final_score_service import FinalScoreService
from src.backend.services.report_service import ReportService
from src.backend.pipelines.report.report_prompt_template import (
    build_report_prompt,
    validate_report_response
)

logger = setup_logger(__name__)

DEFAULT_REPORT = {
    "summary": "Teaching evaluation completed. Detailed analysis unavailable at this time.",
    "strengths": [
        "Session successfully recorded and analyzed",
        "Teaching content delivered to students"
    ],
    "improvements": [
        "Consider reviewing the evaluation scores for specific areas of growth",
        "Focus on continuous improvement across all teaching parameters"
    ],
    "actionable_tips": [
        "Review your engagement scores and consider incorporating more interactive elements",
        "Practice clear communication techniques to improve clarity",
        "Ensure technical accuracy in all content delivery",
        "Monitor pacing to maintain optimal learning flow"
    ]
}

def generate_report(session_id: str, retry_count: int = 1) -> Dict[str, Any]:
    
    if not session_id:
        logger.error("generate_report: session_id is required")
        return _get_fallback_report("Missing session_id")
    
    try:
        logger.info(f"Starting report generation for session {session_id}")
        
        final_scores = FinalScoreService.get_all_parameter_scores(session_id)
        
        if not final_scores:
            logger.error(f"No final scores found for session {session_id}")
            return _get_fallback_report("Final scores not found")
        
        logger.info(f"Retrieved final scores for session {session_id}")
        logger.info(f"  Mentor Score: {final_scores.get('mentor_score', 0):.2f}/10")
        
        prompt = build_report_prompt(final_scores)
        prompt_size = len(prompt)
        logger.info(f"Generated prompt: {prompt_size} characters")
        
        report_json = None
        for attempt in range(retry_count + 1):
            try:
                report_json = _call_llm_api(prompt, attempt + 1)
                if report_json:
                    break
            except Exception as e:
                logger.warning(f"LLM API call attempt {attempt + 1} failed: {str(e)}")
                if attempt == retry_count:
                    logger.error("All LLM API retry attempts exhausted")
        
        if report_json and validate_report_response(report_json):
            logger.info("Report generated successfully")
            
            result = {
                "summary": report_json.get("summary", ""),
                "strengths": report_json.get("strengths", []),
                "improvements": report_json.get("improvements", []),
                "actionable_tips": report_json.get("actionable_tips", []),
                "raw_response": report_json
            }
            
            try:
                ReportService.save_report(
                    session_id=session_id,
                    summary=result["summary"],
                    strengths=result["strengths"],
                    improvements=result["improvements"],
                    actionable_tips=result["actionable_tips"],
                    raw_llm_response=result["raw_response"]
                )
            except Exception as e:
                logger.error(f"Failed to save report to database: {str(e)}")
            
            return result
        else:
            logger.error("LLM response validation failed, using fallback report")
            return _get_fallback_report("Invalid LLM response")
    
    except Exception as e:
        logger.error(f"Report generation failed for session {session_id}: {str(e)}")
        return _get_fallback_report(str(e))

def _call_llm_api(prompt: str, attempt: int) -> Optional[Dict[str, Any]]:
    
    api_key = Config.GEMINI_API_KEY
    if not api_key:
        logger.error("GEMINI_API_KEY not found. Cannot generate report.")
        return None
    
    try:
        genai.configure(api_key=api_key)
        model_name = Config.LLM_MODEL  # e.g., "gemini-1.5-flash"
        model = genai.GenerativeModel(model_name)
        
        logger.info(f"Calling Gemini API (attempt {attempt}) with model {model_name}")
        
        generation_config = genai.types.GenerationConfig(
            temperature=0.2,  # Low temperature for consistent, focused output
            max_output_tokens=2000,  # Safe limit for report
        )
        
        start_time = time.time()
        
        response = model.generate_content(prompt, generation_config=generation_config)
        
        latency = time.time() - start_time
        logger.info(f"LLM API response received in {latency:.2f}s")
        
        content = response.text
        
        cleaned_content = content.replace("```json", "").replace("```", "").strip()
        
        logger.info(f"Parsing LLM response ({len(cleaned_content)} characters)")
        
        try:
            result = json.loads(cleaned_content)
            logger.info("Parsing successful")
            
            logger.info(f"Report summary: {len(result.get('summary', ''))} chars")
            logger.info(f"Strengths: {len(result.get('strengths', []))} items")
            logger.info(f"Improvements: {len(result.get('improvements', []))} items")
            logger.info(f"Tips: {len(result.get('actionable_tips', []))} items")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            logger.debug(f"Raw response: {cleaned_content[:500]}...")
            return None
    
    except Exception as e:
        logger.error(f"LLM API call failed: {str(e)}")
        return None

def _get_fallback_report(error_message: str) -> Dict[str, Any]:
    
    logger.warning(f"Using fallback report due to: {error_message}")
    
    return {
        "summary": DEFAULT_REPORT["summary"],
        "strengths": DEFAULT_REPORT["strengths"].copy(),
        "improvements": DEFAULT_REPORT["improvements"].copy(),
        "actionable_tips": DEFAULT_REPORT["actionable_tips"].copy(),
        "raw_response": {
            "error": error_message,
            "fallback": True
        }
    }

def generate_report_with_scores(
    engagement: float,
    communication_clarity: float,
    technical_correctness: float,
    pacing_structure: float,
    interactive_quality: float,
    mentor_score: float
) -> Dict[str, Any]:
    
    scores = {
        "engagement": engagement,
        "communication_clarity": communication_clarity,
        "technical_correctness": technical_correctness,
        "pacing_structure": pacing_structure,
        "interactive_quality": interactive_quality,
        "mentor_score": mentor_score
    }
    
    prompt = build_report_prompt(scores)
    
    report_json = _call_llm_api(prompt, 1)
    
    if report_json and validate_report_response(report_json):
        return {
            "summary": report_json.get("summary", ""),
            "strengths": report_json.get("strengths", []),
            "improvements": report_json.get("improvements", []),
            "actionable_tips": report_json.get("actionable_tips", []),
            "raw_response": report_json
        }
    else:
        return _get_fallback_report("Direct score generation failed")

__all__ = [
    'generate_report',
    'generate_report_with_scores'
]
