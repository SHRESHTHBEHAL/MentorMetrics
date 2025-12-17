"""
Bias Mitigation Module for fair AI scoring.
Applies confidence intervals and quality-adjusted scoring.
"""

from typing import Dict, Any, Tuple, Optional
from src.backend.utils.logger import setup_logger
import math

logger = setup_logger(__name__)

# Quality thresholds
QUALITY_THRESHOLDS = {
    "video_resolution": {"high": 720, "medium": 480, "low": 360},
    "audio_snr": {"high": 20, "medium": 10, "low": 5},
    "face_detection_rate": {"high": 0.9, "medium": 0.7, "low": 0.5}
}

def calculate_confidence_score(
    audio_data: Optional[Dict] = None,
    visual_data: Optional[Dict] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Calculate confidence score based on data quality.
    
    Returns:
        Dictionary with confidence level and quality breakdown
    """
    audio_data = audio_data or {}
    visual_data = visual_data or {}
    metadata = metadata or {}
    
    quality_scores = []
    quality_breakdown = {}
    
    # Video quality assessment
    resolution = metadata.get("video_height", 720)
    if resolution >= QUALITY_THRESHOLDS["video_resolution"]["high"]:
        video_quality = 1.0
    elif resolution >= QUALITY_THRESHOLDS["video_resolution"]["medium"]:
        video_quality = 0.8
    else:
        video_quality = 0.6
    quality_scores.append(video_quality)
    quality_breakdown["video_quality"] = round(video_quality, 2)
    
    # Audio quality assessment
    clarity_score = audio_data.get("clarity_score", 7)
    audio_quality = min(clarity_score / 10, 1.0)
    quality_scores.append(audio_quality)
    quality_breakdown["audio_quality"] = round(audio_quality, 2)
    
    # Face detection consistency
    face_visible_ratio = visual_data.get("face_visible_ratio", 0.8)
    if face_visible_ratio >= QUALITY_THRESHOLDS["face_detection_rate"]["high"]:
        detection_quality = 1.0
    elif face_visible_ratio >= QUALITY_THRESHOLDS["face_detection_rate"]["medium"]:
        detection_quality = 0.85
    else:
        detection_quality = 0.7
    quality_scores.append(detection_quality)
    quality_breakdown["detection_quality"] = round(detection_quality, 2)
    
    # Calculate overall confidence
    overall_confidence = sum(quality_scores) / len(quality_scores)
    
    return {
        "confidence_score": round(overall_confidence, 3),
        "confidence_level": _get_confidence_level(overall_confidence),
        "quality_breakdown": quality_breakdown
    }


def _get_confidence_level(confidence: float) -> str:
    """Convert confidence score to human-readable level."""
    if confidence >= 0.9:
        return "Very High"
    elif confidence >= 0.8:
        return "High"
    elif confidence >= 0.7:
        return "Moderate"
    elif confidence >= 0.6:
        return "Low"
    else:
        return "Very Low"


def calculate_confidence_interval(
    score: float,
    confidence: float,
    sample_size: int = 1
) -> Tuple[float, float]:
    """
    Calculate confidence interval for a score.
    
    Args:
        score: The raw score (0-10)
        confidence: Data quality confidence (0-1)
        sample_size: Number of sessions (more = narrower interval)
    
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    # Base margin of error inversely related to confidence
    base_margin = 0.5 * (1 - confidence)
    
    # Adjust for sample size (more samples = narrower interval)
    sample_factor = 1 / math.sqrt(max(sample_size, 1))
    
    margin = base_margin * sample_factor * 2  # Scale to reasonable range
    margin = max(0.1, min(margin, 1.0))  # Clamp between 0.1 and 1.0
    
    lower = max(0, score - margin)
    upper = min(10, score + margin)
    
    return (round(lower, 2), round(upper, 2))


def apply_bias_mitigation(
    scores: Dict[str, float],
    audio_data: Optional[Dict] = None,
    visual_data: Optional[Dict] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Apply bias mitigation to scores.
    
    Returns:
        Scores with confidence intervals and bias mitigation flags
    """
    confidence_info = calculate_confidence_score(audio_data, visual_data, metadata)
    confidence = confidence_info["confidence_score"]
    
    mitigated_scores = {}
    
    for param, score in scores.items():
        if not isinstance(score, (int, float)):
            continue
            
        interval = calculate_confidence_interval(score, confidence)
        
        mitigated_scores[param] = {
            "score": round(score, 2),
            "confidence_interval": interval,
            "margin": round((interval[1] - interval[0]) / 2, 2)
        }
    
    return {
        "scores": mitigated_scores,
        "confidence": confidence_info,
        "bias_mitigation_applied": True,
        "mitigation_version": "1.0"
    }


def normalize_for_accent(
    audio_scores: Dict[str, Any],
    detected_accent: Optional[str] = None
) -> Dict[str, Any]:
    """
    Reduce penalty for non-native accents.
    Focuses on content clarity over pronunciation.
    
    Note: This is a placeholder for more sophisticated accent normalization.
    """
    # For now, we don't penalize for accent differences
    # In production, this would use a more sophisticated model
    adjusted_scores = audio_scores.copy()
    
    # If clarity is low but WPM is normal, give benefit of doubt
    if audio_scores.get("clarity_score", 7) < 6:
        wpm = audio_scores.get("wpm", 130)
        if 100 <= wpm <= 180:  # Normal speaking pace
            # Boost clarity score slightly
            adjusted_scores["clarity_score"] = min(
                audio_scores.get("clarity_score", 7) + 0.5,
                10
            )
            adjusted_scores["accent_normalization_applied"] = True
    
    return adjusted_scores


def normalize_for_lighting(
    visual_scores: Dict[str, Any],
    lighting_quality: Optional[float] = None
) -> Dict[str, Any]:
    """
    Adjust visual scores based on lighting conditions.
    Don't penalize for suboptimal lighting.
    """
    adjusted_scores = visual_scores.copy()
    lighting = lighting_quality or 0.8
    
    if lighting < 0.6:  # Poor lighting
        # Increase margin of error for visual metrics
        if "eye_contact_ratio" in adjusted_scores:
            # Give benefit of doubt for eye contact detection in poor lighting
            adjusted_scores["eye_contact_confidence_reduced"] = True
            adjusted_scores["lighting_quality"] = lighting
    
    return adjusted_scores


__all__ = [
    'calculate_confidence_score',
    'calculate_confidence_interval',
    'apply_bias_mitigation',
    'normalize_for_accent',
    'normalize_for_lighting'
]
