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

# Subject-specific rubric adjustments
SUBJECT_RUBRICS = {
    "general": SCORING_RUBRIC,
    
    "math": {
        "engagement": {"audio": 0.10, "text": 0.15, "visual": 0.75},
        "communication_clarity": {"audio": 0.20, "text": 0.60, "visual": 0.20},
        "technical_correctness": {"audio": 0.05, "text": 0.90, "visual": 0.05},
        "pacing_structure": {"audio": 0.50, "text": 0.50, "visual": 0.00},  # More structured
        "interactive_quality": {"audio": 0.15, "text": 0.25, "visual": 0.60}  # Visual demonstrations matter
    },
    
    "programming": {
        "engagement": {"audio": 0.10, "text": 0.20, "visual": 0.70},
        "communication_clarity": {"audio": 0.25, "text": 0.55, "visual": 0.20},
        "technical_correctness": {"audio": 0.02, "text": 0.95, "visual": 0.03},  # Code accuracy critical
        "pacing_structure": {"audio": 0.40, "text": 0.60, "visual": 0.00},  # Step-by-step structure
        "interactive_quality": {"audio": 0.20, "text": 0.30, "visual": 0.50}
    },
    
    "english": {
        "engagement": {"audio": 0.25, "text": 0.15, "visual": 0.60},  # Voice expression matters
        "communication_clarity": {"audio": 0.40, "text": 0.40, "visual": 0.20},  # Pronunciation key
        "technical_correctness": {"audio": 0.10, "text": 0.80, "visual": 0.10},  # Grammar/vocab
        "pacing_structure": {"audio": 0.80, "text": 0.20, "visual": 0.00},  # Rhythm and flow
        "interactive_quality": {"audio": 0.30, "text": 0.20, "visual": 0.50}  # Discussion-based
    },
    
    "science": {
        "engagement": {"audio": 0.15, "text": 0.15, "visual": 0.70},
        "communication_clarity": {"audio": 0.30, "text": 0.50, "visual": 0.20},
        "technical_correctness": {"audio": 0.05, "text": 0.85, "visual": 0.10},  # Accuracy + demos
        "pacing_structure": {"audio": 0.60, "text": 0.40, "visual": 0.00},
        "interactive_quality": {"audio": 0.20, "text": 0.20, "visual": 0.60}  # Demonstrations
    },
    
    "business": {
        "engagement": {"audio": 0.20, "text": 0.15, "visual": 0.65},  # Presentation skills
        "communication_clarity": {"audio": 0.35, "text": 0.45, "visual": 0.20},
        "technical_correctness": {"audio": 0.05, "text": 0.85, "visual": 0.10},
        "pacing_structure": {"audio": 0.60, "text": 0.40, "visual": 0.00},
        "interactive_quality": {"audio": 0.25, "text": 0.25, "visual": 0.50}
    }
}

# Subject metadata for UI
SUBJECT_METADATA = {
    "general": {"label": "General Teaching", "icon": "📚", "description": "Balanced evaluation for all subjects"},
    "math": {"label": "Mathematics", "icon": "🔢", "description": "Focus on step-by-step explanations and visual demonstrations"},
    "programming": {"label": "Programming/CS", "icon": "💻", "description": "Emphasis on code accuracy and structured explanations"},
    "english": {"label": "English/Language", "icon": "📖", "description": "Focus on pronunciation, rhythm, and expression"},
    "science": {"label": "Science", "icon": "🔬", "description": "Balance of accuracy and visual demonstrations"},
    "business": {"label": "Business/Presentation", "icon": "💼", "description": "Emphasis on presentation skills and persuasion"}
}

def validate_rubric(rubric: Dict[str, Dict[str, float]]) -> bool:
    
    for category, weights in rubric.items():
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            print(f"Warning: Weights for '{category}' sum to {total}, not 1.0")
            return False
    return True

assert validate_rubric(SCORING_RUBRIC), "Default SCORING_RUBRIC weights do not sum to 1.0"

# Validate all subject rubrics
for subject, rubric in SUBJECT_RUBRICS.items():
    if subject != "general":
        assert validate_rubric(rubric), f"Subject rubric '{subject}' weights do not sum to 1.0"

def get_rubric(custom_weights: Dict[str, Dict[str, float]] = None, subject: str = None) -> Dict[str, Dict[str, float]]:
    """Get scoring rubric, optionally for a specific subject."""
    
    # Start with subject-specific or default rubric
    if subject and subject in SUBJECT_RUBRICS:
        base_rubric = deepcopy(SUBJECT_RUBRICS[subject])
    else:
        base_rubric = deepcopy(SCORING_RUBRIC)
    
    # Apply custom overrides if any
    if custom_weights:
        for category, weights in custom_weights.items():
            if category in base_rubric:
                base_rubric[category].update(weights)
        
        if not validate_rubric(base_rubric):
            raise ValueError("Custom weights result in invalid rubric (weights must sum to 1.0 per category)")
    
    return base_rubric

def get_rubric_for_subject(subject: str) -> Dict[str, Dict[str, float]]:
    """Get the rubric for a specific subject."""
    return get_rubric(subject=subject)

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
        "subjects": list(SUBJECT_RUBRICS.keys()),
        "subject_metadata": SUBJECT_METADATA,
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
    'SUBJECT_RUBRICS',
    'SUBJECT_METADATA',
    'get_rubric',
    'get_rubric_for_subject',
    'get_category_weight',
    'validate_rubric',
    'get_rubric_summary'
]

