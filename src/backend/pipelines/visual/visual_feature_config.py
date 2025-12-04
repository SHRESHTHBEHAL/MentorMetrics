from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class VisualFeatureThresholds:
    
    MIN_FACE_DETECTION_CONFIDENCE: float = 0.7
    MIN_HAND_DETECTION_CONFIDENCE: float = 0.6
    MOVEMENT_SENSITIVITY: float = 0.3
    FPS_SAMPLING_RATE: int = 2

@dataclass
class FaceMetrics:
    
    face_visibility_ratio: Dict[str, Any] = field(default_factory=lambda: {
        'name': 'face_visibility_ratio',
        'description': 'Ratio of frames where teacher face is clearly visible',
        'range': (0.0, 1.0),
        'optimal_threshold': 0.7,
        'scoring_category': 'engagement',
        'weight': 0.25
    })
    
    gaze_forward_ratio: Dict[str, Any] = field(default_factory=lambda: {
        'name': 'gaze_forward_ratio',
        'description': 'Ratio of time teacher is facing forward/camera',
        'range': (0.0, 1.0),
        'optimal_threshold': 0.6,
        'scoring_category': 'communication_clarity',
        'weight': 0.2
    })
    
    eye_contact_score: Dict[str, Any] = field(default_factory=lambda: {
        'name': 'eye_contact_score',
        'description': 'Score indicating direct eye contact with camera/audience',
        'range': (0.0, 10.0),
        'optimal_threshold': 6.0,
        'scoring_category': 'interactive_quality',
        'weight': 0.3
    })

@dataclass
class GestureMetrics:
    
    hand_movement_frequency: Dict[str, Any] = field(default_factory=lambda: {
        'name': 'hand_movement_frequency',
        'description': 'Frequency of detected hand movements per minute',
        'range': (0.0, 100.0),
        'optimal_range': (10.0, 40.0),
        'scoring_category': 'interactive_quality',
        'weight': 0.25
    })
    
    body_movement_activity: Dict[str, Any] = field(default_factory=lambda: {
        'name': 'body_movement_activity',
        'description': 'Overall body movement activity level (low/medium/high)',
        'range': (0.0, 10.0),
        'optimal_range': (3.0, 7.0),
        'scoring_category': 'engagement',
        'weight': 0.15
    })

@dataclass
class EngagementIndicators:
    
    frames_with_teacher_present: Dict[str, Any] = field(default_factory=lambda: {
        'name': 'frames_with_teacher_present',
        'description': 'Total frames where teacher is detected',
        'unit': 'count',
        'scoring_category': 'engagement'
    })
    
    frames_with_gesture: Dict[str, Any] = field(default_factory=lambda: {
        'name': 'frames_with_gesture',
        'description': 'Total frames with detected hand gestures',
        'unit': 'count',
        'scoring_category': 'interactive_quality'
    })
    
    frames_with_clear_face: Dict[str, Any] = field(default_factory=lambda: {
        'name': 'frames_with_clear_face',
        'description': 'Total frames with clear, unobstructed face visible',
        'unit': 'count',
        'scoring_category': 'communication_clarity'
    })

class VisualFeaturesConfig:
    
    def __init__(self):
        self.thresholds = VisualFeatureThresholds()
        self.face_metrics = FaceMetrics()
        self.gesture_metrics = GestureMetrics()
        self.engagement_indicators = EngagementIndicators()
    
    def get_all_features(self) -> Dict[str, Any]:
        
        features = {}
        
        for metric_class in [self.face_metrics, self.gesture_metrics, self.engagement_indicators]:
            for field_name in metric_class.__dataclass_fields__:
                feature_config = getattr(metric_class, field_name)
                features[feature_config['name']] = feature_config
        
        return features
    
    def get_features_by_category(self, category: str) -> Dict[str, Any]:
        
        all_features = self.get_all_features()
        return {
            name: config for name, config in all_features.items()
            if config.get('scoring_category') == category
        }
    
    def get_category_weights(self) -> Dict[str, float]:
        
        return {
            'engagement': 0.35,
            'communication_clarity': 0.30,
            'interactive_quality': 0.35
        }

VISUAL_FEATURES_CONFIG = VisualFeaturesConfig()

THRESHOLDS = {
    'MIN_FACE_DETECTION_CONFIDENCE': VISUAL_FEATURES_CONFIG.thresholds.MIN_FACE_DETECTION_CONFIDENCE,
    'MIN_HAND_DETECTION_CONFIDENCE': VISUAL_FEATURES_CONFIG.thresholds.MIN_HAND_DETECTION_CONFIDENCE,
    'MOVEMENT_SENSITIVITY': VISUAL_FEATURES_CONFIG.thresholds.MOVEMENT_SENSITIVITY,
    'FPS_SAMPLING_RATE': VISUAL_FEATURES_CONFIG.thresholds.FPS_SAMPLING_RATE
}
