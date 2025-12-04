from typing import Dict, Any

def build_report_prompt(session_scores: Dict[str, Any]) -> str:
    
    engagement = session_scores.get("engagement", 0.0)
    communication_clarity = session_scores.get("communication_clarity", 0.0)
    technical_correctness = session_scores.get("technical_correctness", 0.0)
    pacing_structure = session_scores.get("pacing_structure", 0.0)
    interactive_quality = session_scores.get("interactive_quality", 0.0)
    mentor_score = session_scores.get("mentor_score", 0.0)
    
    prompt = f
    
    return prompt

def get_score_interpretation_context(score: float) -> str:
    
    if score >= 9.0:
        return "exceptional"
    elif score >= 8.0:
        return "excellent"
    elif score >= 7.0:
        return "good"
    elif score >= 6.0:
        return "satisfactory"
    elif score >= 5.0:
        return "needs improvement"
    else:
        return "requires significant improvement"

def validate_report_response(report_json: Dict[str, Any]) -> bool:
    
    required_fields = ["summary", "strengths", "improvements", "actionable_tips"]
    
    for field in required_fields:
        if field not in report_json:
            return False
        
        if field != "summary" and not isinstance(report_json[field], list):
            return False
    
    return True

__all__ = [
    'build_report_prompt',
    'get_score_interpretation_context',
    'validate_report_response'
]
