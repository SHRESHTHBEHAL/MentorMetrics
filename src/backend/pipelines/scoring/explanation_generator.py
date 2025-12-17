"""
Explanation Generator for Explainable AI outputs.
Generates human-readable explanations for each score with evidence.
"""

from typing import Dict, Any, List, Optional
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

# Thresholds for generating evidence
THRESHOLDS = {
    "eye_contact": {"good": 0.7, "poor": 0.4},
    "wpm": {"good_min": 120, "good_max": 160, "too_fast": 180, "too_slow": 100},
    "silence_ratio": {"good": 0.15, "too_much": 0.3},
    "hand_gestures": {"good": 0.3, "poor": 0.1},
    "clarity": {"good": 7, "poor": 5}
}

def generate_score_explanations(
    scores: Dict[str, float],
    audio_data: Optional[Dict] = None,
    visual_data: Optional[Dict] = None,
    text_data: Optional[Dict] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Generate explanations for each score with evidence and tips.
    
    Returns:
        Dictionary with explanations for each scoring category
    """
    explanations = {}
    
    audio_data = audio_data or {}
    visual_data = visual_data or {}
    text_data = text_data or {}
    
    # Engagement explanation
    explanations["engagement"] = _explain_engagement(
        scores.get("engagement", 5.0),
        visual_data
    )
    
    # Communication clarity explanation
    explanations["communication_clarity"] = _explain_communication(
        scores.get("communication_clarity", 5.0),
        audio_data
    )
    
    # Technical correctness explanation
    explanations["technical_correctness"] = _explain_technical(
        scores.get("technical_correctness", 5.0),
        text_data
    )
    
    # Pacing explanation
    explanations["pacing_structure"] = _explain_pacing(
        scores.get("pacing_structure", 5.0),
        audio_data
    )
    
    # Interactive quality explanation
    explanations["interactive_quality"] = _explain_interactive(
        scores.get("interactive_quality", 5.0),
        visual_data,
        audio_data
    )
    
    return explanations


def _explain_engagement(score: float, visual_data: Dict) -> Dict[str, Any]:
    """Generate engagement explanation based on visual data."""
    evidence = []
    tips = []
    
    eye_contact_ratio = visual_data.get("eye_contact_ratio", 0.5)
    face_visible_ratio = visual_data.get("face_visible_ratio", 0.8)
    
    # Eye contact evidence
    if eye_contact_ratio >= THRESHOLDS["eye_contact"]["good"]:
        evidence.append({
            "type": "positive",
            "text": f"Excellent eye contact maintained ({int(eye_contact_ratio * 100)}% of session)"
        })
    elif eye_contact_ratio < THRESHOLDS["eye_contact"]["poor"]:
        evidence.append({
            "type": "negative",
            "text": f"Limited eye contact detected ({int(eye_contact_ratio * 100)}% of session)"
        })
        tips.append("Look directly at the camera lens to simulate eye contact with viewers")
    else:
        evidence.append({
            "type": "positive",
            "text": f"Good eye contact maintained ({int(eye_contact_ratio * 100)}% of session)"
        })
    
    # Face visibility
    if face_visible_ratio < 0.7:
        evidence.append({
            "type": "negative",
            "text": "Face was not visible for significant portions"
        })
        tips.append("Ensure your face is well-lit and centered in frame")
    
    # Generate summary explanation
    if score >= 8:
        explanation = "Excellent engagement with strong eye contact and presence"
    elif score >= 6:
        explanation = "Good engagement with room for improvement in eye contact"
    else:
        explanation = "Engagement needs improvement - focus on maintaining eye contact"
    
    if not tips:
        tips.append("Keep up the great work maintaining audience connection!")
    
    return {
        "score": round(score, 2),
        "explanation": explanation,
        "evidence": evidence,
        "tips": tips
    }


def _explain_communication(score: float, audio_data: Dict) -> Dict[str, Any]:
    """Generate communication clarity explanation based on audio data."""
    evidence = []
    tips = []
    
    wpm = audio_data.get("wpm", 130)
    clarity_score = audio_data.get("clarity_score", 5)
    silence_ratio = audio_data.get("silence_ratio", 0.15)
    
    # WPM evidence
    if THRESHOLDS["wpm"]["good_min"] <= wpm <= THRESHOLDS["wpm"]["good_max"]:
        evidence.append({
            "type": "positive",
            "text": f"Optimal speaking pace at {int(wpm)} words per minute"
        })
    elif wpm > THRESHOLDS["wpm"]["too_fast"]:
        evidence.append({
            "type": "negative",
            "text": f"Speaking too fast at {int(wpm)} WPM (target: 120-160)"
        })
        tips.append("Slow down your speech to improve comprehension")
    elif wpm < THRESHOLDS["wpm"]["too_slow"]:
        evidence.append({
            "type": "negative",
            "text": f"Speaking pace slow at {int(wpm)} WPM (target: 120-160)"
        })
        tips.append("Try to maintain a more dynamic speaking pace")
    else:
        evidence.append({
            "type": "positive",
            "text": f"Good speaking pace at {int(wpm)} words per minute"
        })
    
    # Clarity
    if clarity_score >= THRESHOLDS["clarity"]["good"]:
        evidence.append({
            "type": "positive",
            "text": "Speech was clear and easy to understand"
        })
    elif clarity_score < THRESHOLDS["clarity"]["poor"]:
        evidence.append({
            "type": "negative",
            "text": "Audio clarity could be improved"
        })
        tips.append("Use a better microphone or reduce background noise")
    
    # Silence ratio
    if silence_ratio > THRESHOLDS["silence_ratio"]["too_much"]:
        evidence.append({
            "type": "negative",
            "text": f"Too many long pauses ({int(silence_ratio * 100)}% silence)"
        })
        tips.append("Reduce long pauses to maintain audience attention")
    
    if score >= 8:
        explanation = "Excellent communication with clear, well-paced speech"
    elif score >= 6:
        explanation = "Good communication with minor areas for improvement"
    else:
        explanation = "Communication clarity needs work - focus on pace and enunciation"
    
    if not tips:
        tips.append("Your communication skills are strong!")
    
    return {
        "score": round(score, 2),
        "explanation": explanation,
        "evidence": evidence,
        "tips": tips
    }


def _explain_technical(score: float, text_data: Dict) -> Dict[str, Any]:
    """Generate technical correctness explanation based on text analysis."""
    evidence = []
    tips = []
    
    content_score = text_data.get("content_relevance", 7)
    structure_score = text_data.get("structure_score", 7)
    
    if content_score >= 8:
        evidence.append({
            "type": "positive",
            "text": "Content is accurate and well-researched"
        })
    elif content_score < 5:
        evidence.append({
            "type": "negative",
            "text": "Content accuracy could be improved"
        })
        tips.append("Double-check facts and include more specific examples")
    else:
        evidence.append({
            "type": "positive",
            "text": "Content is generally accurate"
        })
    
    if structure_score >= 8:
        evidence.append({
            "type": "positive",
            "text": "Well-structured presentation with clear flow"
        })
    elif structure_score < 5:
        evidence.append({
            "type": "negative",
            "text": "Presentation structure could be clearer"
        })
        tips.append("Use a clear introduction, main points, and conclusion")
    
    if score >= 8:
        explanation = "Excellent technical content with accurate information"
    elif score >= 6:
        explanation = "Good technical accuracy with room for deeper coverage"
    else:
        explanation = "Technical content needs improvement - verify facts and add examples"
    
    if not tips:
        tips.append("Consider adding real-world examples to reinforce concepts")
    
    return {
        "score": round(score, 2),
        "explanation": explanation,
        "evidence": evidence,
        "tips": tips
    }


def _explain_pacing(score: float, audio_data: Dict) -> Dict[str, Any]:
    """Generate pacing explanation."""
    evidence = []
    tips = []
    
    wpm = audio_data.get("wpm", 130)
    duration = audio_data.get("duration_seconds", 300)
    
    if 120 <= wpm <= 160:
        evidence.append({
            "type": "positive",
            "text": "Speaking pace allows audience to follow along easily"
        })
    else:
        evidence.append({
            "type": "negative",
            "text": "Speaking pace could be optimized for better comprehension"
        })
        tips.append("Aim for 120-160 words per minute for optimal comprehension")
    
    if duration > 600:
        evidence.append({
            "type": "positive",
            "text": "Session length allows for comprehensive coverage"
        })
    elif duration < 120:
        evidence.append({
            "type": "negative",
            "text": "Session may be too short for thorough explanation"
        })
        tips.append("Consider extending content for deeper coverage")
    
    if score >= 8:
        explanation = "Excellent pacing that keeps audience engaged"
    elif score >= 6:
        explanation = "Good pacing with minor timing adjustments suggested"
    else:
        explanation = "Pacing needs adjustment - consider varying your tempo"
    
    if not tips:
        tips.append("Use strategic pauses to emphasize key points")
    
    return {
        "score": round(score, 2),
        "explanation": explanation,
        "evidence": evidence,
        "tips": tips
    }


def _explain_interactive(score: float, visual_data: Dict, audio_data: Dict) -> Dict[str, Any]:
    """Generate interactive quality explanation."""
    evidence = []
    tips = []
    
    hand_gesture_ratio = visual_data.get("hand_gesture_ratio", 0.2)
    
    if hand_gesture_ratio >= THRESHOLDS["hand_gestures"]["good"]:
        evidence.append({
            "type": "positive",
            "text": f"Good use of hand gestures ({int(hand_gesture_ratio * 100)}% of session)"
        })
    elif hand_gesture_ratio < THRESHOLDS["hand_gestures"]["poor"]:
        evidence.append({
            "type": "negative",
            "text": "Limited hand gestures detected"
        })
        tips.append("Use natural hand gestures to emphasize points")
    else:
        evidence.append({
            "type": "positive",
            "text": "Moderate use of hand gestures"
        })
    
    if score >= 8:
        explanation = "Highly interactive and engaging presentation style"
    elif score >= 6:
        explanation = "Good interactive elements with room to engage more"
    else:
        explanation = "More interactive elements would improve engagement"
    
    if not tips:
        tips.append("Consider asking rhetorical questions to engage viewers")
    
    return {
        "score": round(score, 2),
        "explanation": explanation,
        "evidence": evidence,
        "tips": tips
    }


__all__ = ['generate_score_explanations']
