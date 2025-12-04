from typing import Dict, Any, Optional
from src.backend.utils.logger import setup_logger
from src.backend.pipelines.fusion.fusion_config import SCORING_RUBRIC, get_rubric

logger = setup_logger(__name__)

DEFAULT_SCORES = {
    "audio": 5.0,   # Neutral/average
    "text": 5.0,    # Neutral/average
    "visual": 5.0   # Neutral/average
}

MODALITY_MAPPINGS = {
    "audio": {
        "engagement": "audio_energy_score",  # Example - would need to map actual keys
        "communication_clarity": "clarity_score",
        "technical_correctness": "confidence_score",
        "pacing_structure": "pacing_score",
        "interactive_quality": "conversational_score"
    },
    "text": {
        "engagement": "engagement_score",
        "communication_clarity": "clarity_score",
        "technical_correctness": "technical_correctness_score",
        "pacing_structure": "structure_score",
        "interactive_quality": "explanation_quality_score"
    },
    "visual": {
        "engagement": "face_visibility_score",
        "communication_clarity": "gaze_forward_score",
        "technical_correctness": "confidence_indicator_score",
        "pacing_structure": None,  # Not used
        "interactive_quality": "gesture_score"
    }
}

def compute_fusion_scores(
    audio_scores: Optional[Dict[str, float]] = None,
    text_scores: Optional[Dict[str, float]] = None,
    visual_scores: Optional[Dict[str, float]] = None,
    custom_rubric: Optional[Dict] = None
) -> Dict[str, Any]:
    
    try:
        rubric = custom_rubric if custom_rubric else SCORING_RUBRIC
    except Exception as e:
        logger.error(f"Error loading scoring rubric: {str(e)}")
        rubric = SCORING_RUBRIC
    
    audio_scores = audio_scores or {}
    text_scores = text_scores or {}
    visual_scores = visual_scores or {}
    
    logger.info("Computing fusion scores from multimodal inputs")
    logger.info(f"  Audio scores available: {len(audio_scores)} metrics")
    logger.info(f"  Text scores available: {len(text_scores)} metrics")
    logger.info(f"  Visual scores available: {len(visual_scores)} metrics")
    
    fusion_results = {}
    fusion_metadata = {
        "modality_inputs": {
            "audio": audio_scores,
            "text": text_scores,
            "visual": visual_scores
        },
        "weights_applied": rubric,
        "intermediate_calculations": {}
    }
    
    for parameter in rubric.keys():
        try:
            score = _compute_parameter_score(
                parameter,
                audio_scores,
                text_scores,
                visual_scores,
                rubric,
                fusion_metadata
            )
            fusion_results[parameter] = score
            
            logger.info(f"  {parameter}: {score:.2f}/10")
            
        except Exception as e:
            logger.error(f"Error computing {parameter} score: {str(e)}")
            fusion_results[parameter] = 5.0  # Fallback to neutral
    
    overall_score = sum(fusion_results.values()) / len(fusion_results)
    
    logger.info(f"Fusion complete. Overall score: {overall_score:.2f}/10")
    
    return {
        "engagement": fusion_results.get("engagement", 5.0),
        "communication_clarity": fusion_results.get("communication_clarity", 5.0),
        "technical_correctness": fusion_results.get("technical_correctness", 5.0),
        "pacing_structure": fusion_results.get("pacing_structure", 5.0),
        "interactive_quality": fusion_results.get("interactive_quality", 5.0),
        "overall_score": round(overall_score, 2),
        "final_scores": fusion_results,
        "metadata": fusion_metadata
    }

def _compute_parameter_score(
    parameter: str,
    audio_scores: Dict,
    text_scores: Dict,
    visual_scores: Dict,
    rubric: Dict,
    metadata: Dict
) -> float:
    
    if parameter not in rubric:
        raise ValueError(f"Unknown parameter: {parameter}")
    
    weights = rubric[parameter]
    
    audio_score = _extract_modality_score("audio", parameter, audio_scores)
    text_score = _extract_modality_score("text", parameter, text_scores)
    visual_score = _extract_modality_score("visual", parameter, visual_scores)
    
    logger.debug(f"  {parameter} inputs:")
    logger.debug(f"    Audio: {audio_score:.2f} (weight: {weights['audio']:.2f})")
    logger.debug(f"    Text: {text_score:.2f} (weight: {weights['text']:.2f})")
    logger.debug(f"    Visual: {visual_score:.2f} (weight: {weights['visual']:.2f})")
    
    fused_score = (
        audio_score * weights["audio"] +
        text_score * weights["text"] +
        visual_score * weights["visual"]
    )
    
    fused_score = _normalize_score(fused_score)
    
    metadata["intermediate_calculations"][parameter] = {
        "audio_contribution": round(audio_score * weights["audio"], 2),
        "text_contribution": round(text_score * weights["text"], 2),
        "visual_contribution": round(visual_score * weights["visual"], 2),
        "fused_score": round(fused_score, 2)
    }
    
    return round(fused_score, 2)

def _extract_modality_score(
    modality: str,
    parameter: str,
    scores: Dict
) -> float:
    
    if parameter in scores:
        return _normalize_score(scores[parameter])
    
    score_key = f"{parameter}_score"
    if score_key in scores:
        return _normalize_score(scores[score_key])
    
    if f"{modality}_overall" in scores:
        return _normalize_score(scores[f"{modality}_overall"])
    
    if "overall" in scores:
        return _normalize_score(scores["overall"])
    if "overall_score" in scores:
        return _normalize_score(scores["overall_score"])
    
    default = DEFAULT_SCORES[modality]
    logger.warning(f"Missing {modality} score for {parameter}, using default: {default}")
    return default

def _normalize_score(score: Any) -> float:
    
    try:
        score_float = float(score)
        return max(0.0, min(10.0, score_float))
    except (ValueError, TypeError):
        logger.warning(f"Invalid score value: {score}, using default 5.0")
        return 5.0

def validate_fusion_inputs(
    audio_scores: Optional[Dict],
    text_scores: Optional[Dict],
    visual_scores: Optional[Dict]
) -> Dict[str, bool]:
    
    validation = {
        "audio_valid": False,
        "text_valid": False,
        "visual_valid": False,
        "errors": []
    }
    
    if audio_scores and isinstance(audio_scores, dict) and len(audio_scores) > 0:
        validation["audio_valid"] = True
    else:
        validation["errors"].append("Audio scores missing or invalid")
    
    if text_scores and isinstance(text_scores, dict) and len(text_scores) > 0:
        validation["text_valid"] = True
    else:
        validation["errors"].append("Text scores missing or invalid")
    
    if visual_scores and isinstance(visual_scores, dict) and len(visual_scores) > 0:
        validation["visual_valid"] = True
    else:
        validation["errors"].append("Visual scores missing or invalid")
    
    return validation

__all__ = [
    'compute_fusion_scores',
    'validate_fusion_inputs'
]
