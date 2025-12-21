from typing import Dict, Any, Optional
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

MENTOR_SCORE_WEIGHTS = {
    "engagement": 0.20,                  # 20% - Important for student attention
    "communication_clarity": 0.25,       # 25% - Critical for understanding
    "technical_correctness": 0.30,       # 30% - Most important (content quality)
    "pacing_structure": 0.15,            # 15% - Important for learning flow
    "interactive_quality": 0.10          # 10% - Nice to have
}

# Score boost to make results more encouraging (adds 1.5 points, capped at 10)
BASE_SCORE_BOOST = 1.5

DEFAULT_PARAMETER_SCORE = 6.0  # Slightly above average default

def compute_overall_score(
    fusion_scores: Dict[str, Any],
    custom_weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    
    if not fusion_scores or not isinstance(fusion_scores, dict):
        logger.error("Invalid fusion_scores provided to compute_overall_score")
        return _get_fallback_result()
    
    weights = custom_weights if custom_weights else MENTOR_SCORE_WEIGHTS
    
    weight_sum = sum(weights.values())
    if not (0.99 <= weight_sum <= 1.01):
        logger.warning(f"Weights sum to {weight_sum}, not 1.0. Normalizing...")
        weights = {k: v / weight_sum for k, v in weights.items()}
    
    logger.info("Computing overall Mentor Score")
    
    engagement = _get_parameter_score(fusion_scores, "engagement")
    communication_clarity = _get_parameter_score(fusion_scores, "communication_clarity")
    technical_correctness = _get_parameter_score(fusion_scores, "technical_correctness")
    pacing_structure = _get_parameter_score(fusion_scores, "pacing_structure")
    interactive_quality = _get_parameter_score(fusion_scores, "interactive_quality")
    
    logger.info("Parameter scores:")
    logger.info(f"  Engagement: {engagement:.2f}/10 (weight: {weights['engagement']:.0%})")
    logger.info(f"  Communication Clarity: {communication_clarity:.2f}/10 (weight: {weights['communication_clarity']:.0%})")
    logger.info(f"  Technical Correctness: {technical_correctness:.2f}/10 (weight: {weights['technical_correctness']:.0%})")
    logger.info(f"  Pacing/Structure: {pacing_structure:.2f}/10 (weight: {weights['pacing_structure']:.0%})")
    logger.info(f"  Interactive Quality: {interactive_quality:.2f}/10 (weight: {weights['interactive_quality']:.0%})")
    
    mentor_score = (
        engagement * weights["engagement"] +
        communication_clarity * weights["communication_clarity"] +
        technical_correctness * weights["technical_correctness"] +
        pacing_structure * weights["pacing_structure"] +
        interactive_quality * weights["interactive_quality"]
    )
    
    # Apply base score boost to make results more encouraging
    mentor_score = mentor_score + BASE_SCORE_BOOST
    
    mentor_score = _normalize_score(mentor_score)
    
    contributions = {
        "engagement": round(engagement * weights["engagement"], 2),
        "communication_clarity": round(communication_clarity * weights["communication_clarity"], 2),
        "technical_correctness": round(technical_correctness * weights["technical_correctness"], 2),
        "pacing_structure": round(pacing_structure * weights["pacing_structure"], 2),
        "interactive_quality": round(interactive_quality * weights["interactive_quality"], 2)
    }
    
    grade = _score_to_grade(mentor_score)
    
    logger.info(f"Final Mentor Score: {mentor_score:.2f}/10 (Grade: {grade})")
    
    result = {
        "mentor_score": round(mentor_score, 2),
        "grade": grade,
        "breakdown": {
            "engagement": round(engagement, 2),
            "communication_clarity": round(communication_clarity, 2),
            "technical_correctness": round(technical_correctness, 2),
            "pacing_structure": round(pacing_structure, 2),
            "interactive_quality": round(interactive_quality, 2)
        },
        "weights_applied": weights,
        "contributions": contributions
    }
    
    return result

def _get_parameter_score(fusion_scores: Dict, parameter: str) -> float:
    
    if parameter in fusion_scores:
        return _normalize_score(fusion_scores[parameter])
    
    if "final_scores" in fusion_scores and parameter in fusion_scores["final_scores"]:
        return _normalize_score(fusion_scores["final_scores"][parameter])
    
    logger.warning(f"Missing parameter '{parameter}', using default: {DEFAULT_PARAMETER_SCORE}")
    return DEFAULT_PARAMETER_SCORE

def _normalize_score(score: Any) -> float:
    
    try:
        score_float = float(score)
        return max(0.0, min(10.0, score_float))
    except (ValueError, TypeError):
        logger.warning(f"Invalid score value: {score}, using default {DEFAULT_PARAMETER_SCORE}")
        return DEFAULT_PARAMETER_SCORE

def _score_to_grade(score: float) -> str:
    # More lenient grading scale
    if score >= 9.0:
        return "A+"
    elif score >= 8.5:
        return "A"
    elif score >= 8.0:
        return "A-"
    elif score >= 7.5:
        return "B+"
    elif score >= 7.0:
        return "B"
    elif score >= 6.5:
        return "B-"
    elif score >= 6.0:
        return "C+"
    elif score >= 5.5:
        return "C"
    elif score >= 5.0:
        return "C-"
    elif score >= 4.0:
        return "D"
    else:
        return "F"

def _get_fallback_result() -> Dict[str, Any]:
    
    return {
        "mentor_score": 5.0,
        "grade": "C",
        "breakdown": {
            "engagement": 5.0,
            "communication_clarity": 5.0,
            "technical_correctness": 5.0,
            "pacing_structure": 5.0,
            "interactive_quality": 5.0
        },
        "weights_applied": MENTOR_SCORE_WEIGHTS,
        "contributions": {
            "engagement": 1.0,
            "communication_clarity": 1.25,
            "technical_correctness": 1.5,
            "pacing_structure": 0.75,
            "interactive_quality": 0.5
        }
    }

def get_score_interpretation(mentor_score: float) -> Dict[str, str]:
    
    if mentor_score >= 9.0:
        level = "Exceptional"
        description = "Outstanding teaching performance across all parameters"
        recommendations = "Continue excellence, consider mentoring other teachers"
    elif mentor_score >= 8.0:
        level = "Excellent"
        description = "Strong teaching performance with minor areas for improvement"
        recommendations = "Fine-tune pacing and interactive elements"
    elif mentor_score >= 7.0:
        level = "Good"
        description = "Solid teaching performance with room for growth"
        recommendations = "Focus on engagement and communication clarity"
    elif mentor_score >= 6.0:
        level = "Satisfactory"
        description = "Adequate teaching performance, needs improvement"
        recommendations = "Work on technical correctness and structure"
    elif mentor_score >= 5.0:
        level = "Needs Improvement"
        description = "Below average teaching performance"
        recommendations = "Seek feedback and focus on core teaching fundamentals"
    else:
        level = "Poor"
        description = "Significant improvement needed"
        recommendations = "Consider additional training and mentorship"
    
    return {
        "level": level,
        "description": description,
        "recommendations": recommendations,
        "grade": _score_to_grade(mentor_score)
    }

__all__ = [
    'compute_overall_score',
    'get_score_interpretation',
    'MENTOR_SCORE_WEIGHTS'
]
