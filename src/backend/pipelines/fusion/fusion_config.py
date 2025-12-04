from typing import Dict, Any
from copy import deepcopy

SCORING_RUBRIC = {
    "engagement": {
        "audio": 0.15,   # Voice energy, tone variation
        "text": 0.10,    # Engaging language, questions
        "visual": 0.75   # Face visibility, gestures, movement
    },
    
    "communication_clarity": {
        "audio": 0.30,   # Voice clarity, volume, silence management
        "text": 0.50,    # Clear explanations, structure
        "visual": 0.20   # Eye contact, forward gaze
    },
    
    "technical_correctness": {
        "audio": 0.05,   # Voice confidence (minor indicator)
        "text": 0.90,    # Content accuracy, explanations
        "visual": 0.05   # Confident body language (minor indicator)
    },
    
    "pacing_structure": {
        "audio": 0.70,   # WPM, silence ratio, pauses
        "text": 0.30,    # Lesson structure, organization
        "visual": 0.00   # Not relevant to pacing
    },
    
    "interactive_quality": {
        "audio": 0.20,   # Conversational tone, questioning
        "text": 0.20,    # Questions, student engagement cues
        "visual": 0.60   # Hand gestures, body movement, interaction
    }
}

def validate_rubric(rubric: Dict[str, Dict[str, float]]) -> bool:
    
    for category, weights in rubric.items():
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            print(f"Warning: Weights for '{category}' sum to {total}, not 1.0")
            return False
    return True

assert validate_rubric(SCORING_RUBRIC), "Default SCORING_RUBRIC weights do not sum to 1.0"

def get_rubric(custom_weights: Dict[str, Dict[str, float]] = None) -> Dict[str, Dict[str, float]]:
    
    if custom_weights is None:
        return deepcopy(SCORING_RUBRIC)
    
    rubric = deepcopy(SCORING_RUBRIC)
    
    for category, weights in custom_weights.items():
        if category in rubric:
            rubric[category].update(weights)
    
    if not validate_rubric(rubric):
        raise ValueError("Custom weights result in invalid rubric (weights must sum to 1.0 per category)")
    
    return rubric

def get_category_weight(category: str, modality: str, custom_rubric: Dict = None) -> float:
    
    rubric = custom_rubric if custom_rubric else SCORING_RUBRIC
    
    if category not in rubric:
        raise ValueError(f"Unknown category: {category}")
    
    if modality not in rubric[category]:
        raise ValueError(f"Unknown modality: {modality}")
    
    return rubric[category][modality]

def get_rubric_summary() -> Dict[str, Any]:
    
    summary = {
        "categories": list(SCORING_RUBRIC.keys()),
        "modalities": ["audio", "text", "visual"],
        "category_details": {}
    }
    
    for category, weights in SCORING_RUBRIC.items():
        summary["category_details"][category] = {
            "weights": weights,
            "total": sum(weights.values()),
            "dominant_modality": max(weights.items(), key=lambda x: x[1])[0]
        }
    
    return summary

__all__ = [
    'SCORING_RUBRIC',
    'get_rubric',
    'get_category_weight',
    'validate_rubric',
    'get_rubric_summary'
]
