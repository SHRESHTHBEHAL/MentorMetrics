import pytest

MOCK_SCORING_RUBRIC = {
    "engagement": {
        "audio": 0.4,
        "text": 0.2,
        "visual": 0.4
    },
    "communication_clarity": {
        "audio": 0.3,
        "text": 0.5,
        "visual": 0.2
    },
    "technical_correctness": {
        "audio": 0.1,
        "text": 0.8,
        "visual": 0.1
    },
    "pacing_structure": {
        "audio": 0.4,
        "text": 0.4,
        "visual": 0.2
    },
    "interactive_quality": {
        "audio": 0.3,
        "text": 0.3,
        "visual": 0.4
    }
}

def compute_fusion_scores_mock(audio_scores, text_scores, visual_scores, rubric=None):
    
    if rubric is None:
        rubric = MOCK_SCORING_RUBRIC
    
    default_audio = {"engagement": 5.0, "clarity": 5.0, "pacing": 5.0, "interaction": 5.0}
    default_text = {"clarity": 5.0, "correctness": 5.0, "structure": 5.0, "interaction": 5.0}
    default_visual = {"engagement": 5.0, "presence": 5.0, "gestures": 5.0}
    
    audio = audio_scores if audio_scores else default_audio
    text = text_scores if text_scores else default_text
    visual = visual_scores if visual_scores else default_visual
    
    def clamp(value):
        return max(0.0, min(10.0, float(value)))
    
    fused = {}
    
    fused["engagement"] = clamp(
        rubric["engagement"]["audio"] * clamp(audio.get("engagement", 5.0)) +
        rubric["engagement"]["text"] * clamp(text.get("clarity", 5.0)) +
        rubric["engagement"]["visual"] * clamp(visual.get("engagement", 5.0))
    )
    
    fused["communication_clarity"] = clamp(
        rubric["communication_clarity"]["audio"] * clamp(audio.get("clarity", 5.0)) +
        rubric["communication_clarity"]["text"] * clamp(text.get("clarity", 5.0)) +
        rubric["communication_clarity"]["visual"] * clamp(visual.get("presence", 5.0))
    )
    
    fused["technical_correctness"] = clamp(
        rubric["technical_correctness"]["audio"] * 5.0 +
        rubric["technical_correctness"]["text"] * clamp(text.get("correctness", 5.0)) +
        rubric["technical_correctness"]["visual"] * 5.0
    )
    
    fused["pacing_structure"] = clamp(
        rubric["pacing_structure"]["audio"] * clamp(audio.get("pacing", 5.0)) +
        rubric["pacing_structure"]["text"] * clamp(text.get("structure", 5.0)) +
        rubric["pacing_structure"]["visual"] * 5.0
    )
    
    fused["interactive_quality"] = clamp(
        rubric["interactive_quality"]["audio"] * clamp(audio.get("interaction", 5.0)) +
        rubric["interactive_quality"]["text"] * clamp(text.get("interaction", 5.0)) +
        rubric["interactive_quality"]["visual"] * clamp(visual.get("gestures", 5.0))
    )
    
    return fused

def calculate_mentor_score_mock(fused_scores, weights=None):
    
    if weights is None:
        weights = {
            "engagement": 0.2,
            "communication_clarity": 0.2,
            "technical_correctness": 0.2,
            "pacing_structure": 0.2,
            "interactive_quality": 0.2
        }
    
    total = 0.0
    for param, score in fused_scores.items():
        weight = weights.get(param, 0.0)
        total += weight * max(0.0, min(10.0, score))
    
    return max(0.0, min(10.0, total))

class TestFusionEngine:
    
    def test_normal_scenario_all_modalities_present(self):
        
        audio_scores = {
            "engagement": 8.0,
            "clarity": 7.5,
            "pacing": 6.5,
            "interaction": 7.0
        }
        
        text_scores = {
            "clarity": 8.5,
            "correctness": 9.0,
            "structure": 7.5,
            "interaction": 8.0
        }
        
        visual_scores = {
            "engagement": 7.5,
            "presence": 8.0,
            "gestures": 7.0
        }
        
        fused = compute_fusion_scores_mock(audio_scores, text_scores, visual_scores)
        
        assert "engagement" in fused
        assert "communication_clarity" in fused
        assert "technical_correctness" in fused
        assert "pacing_structure" in fused
        assert "interactive_quality" in fused
        
        for param, score in fused.items():
            assert 0.0 <= score <= 10.0
    
    def test_missing_audio_uses_defaults(self):
        
        text_scores = {"clarity": 8.0, "correctness": 9.0, "structure": 7.0, "interaction": 7.5}
        visual_scores = {"engagement": 7.5, "presence": 8.0, "gestures": 7.0}
        
        fused = compute_fusion_scores_mock(None, text_scores, visual_scores)
        
        assert "engagement" in fused
        assert 0.0 <= fused["engagement"] <= 10.0
    
    def test_missing_text_uses_defaults(self):
        
        audio_scores = {"engagement": 8.0, "clarity": 7.5, "pacing": 6.5, "interaction": 7.0}
        visual_scores = {"engagement": 7.5, "presence": 8.0, "gestures": 7.0}
        
        fused = compute_fusion_scores_mock(audio_scores, None, visual_scores)
        
        assert "communication_clarity" in fused
        assert 0.0 <= fused["communication_clarity"] <= 10.0
    
    def test_missing_visual_uses_defaults(self):
        
        audio_scores = {"engagement": 8.0, "clarity": 7.5, "pacing": 6.5, "interaction": 7.0}
        text_scores = {"clarity": 8.0, "correctness": 9.0, "structure": 7.0, "interaction": 7.5}
        
        fused = compute_fusion_scores_mock(audio_scores, text_scores, None)
        
        assert "interactive_quality" in fused
        assert 0.0 <= fused["interactive_quality"] <= 10.0
    
    def test_negative_values_clamped(self):
        
        audio_scores = {"engagement": -5.0, "clarity": -10.0, "pacing": 6.5, "interaction": 7.0}
        text_scores = {"clarity": 8.0, "correctness": 9.0, "structure": 7.0, "interaction": 7.5}
        visual_scores = {"engagement": 7.5, "presence": 8.0, "gestures": 7.0}
        
        fused = compute_fusion_scores_mock(audio_scores, text_scores, visual_scores)
        
        for param, score in fused.items():
            assert score >= 0.0
    
    def test_values_over_10_clamped(self):
        
        audio_scores = {"engagement": 15.0, "clarity": 20.0, "pacing": 6.5, "interaction": 7.0}
        text_scores = {"clarity": 100.0, "correctness": 50.0, "structure": 7.0, "interaction": 7.5}
        visual_scores = {"engagement": 7.5, "presence": 8.0, "gestures": 7.0}
        
        fused = compute_fusion_scores_mock(audio_scores, text_scores, visual_scores)
        
        for param, score in fused.items():
            assert score <= 10.0
    
    def test_scoring_rubric_weights_sum_to_one(self):
        
        for parameter, weights in MOCK_SCORING_RUBRIC.items():
            total_weight = sum(weights.values())
            assert abs(total_weight - 1.0) < 0.001, f"{parameter} weights sum to {total_weight}, not 1.0"
    
    def test_final_mentor_score_within_bounds(self):
        
        fused_scores = {
            "engagement": 8.0,
            "communication_clarity": 7.5,
            "technical_correctness": 9.0,
            "pacing_structure": 7.0,
            "interactive_quality": 8.5
        }
        
        mentor_score = calculate_mentor_score_mock(fused_scores)
        
        assert 0.0 <= mentor_score <= 10.0
    
    def test_mentor_score_calculation_accuracy(self):
        
        fused_scores = {
            "engagement": 8.0,
            "communication_clarity": 8.0,
            "technical_correctness": 8.0,
            "pacing_structure": 8.0,
            "interactive_quality": 8.0
        }
        
        mentor_score = calculate_mentor_score_mock(fused_scores)
        
        assert abs(mentor_score - 8.0) < 0.1
    
    def test_extreme_low_scores(self):
        
        fused_scores = {
            "engagement": 0.0,
            "communication_clarity": 0.0,
            "technical_correctness": 0.0,
            "pacing_structure": 0.0,
            "interactive_quality": 0.0
        }
        
        mentor_score = calculate_mentor_score_mock(fused_scores)
        
        assert mentor_score == 0.0
    
    def test_extreme_high_scores(self):
        
        fused_scores = {
            "engagement": 10.0,
            "communication_clarity": 10.0,
            "technical_correctness": 10.0,
            "pacing_structure": 10.0,
            "interactive_quality": 10.0
        }
        
        mentor_score = calculate_mentor_score_mock(fused_scores)
        
        assert mentor_score == 10.0
    
    def test_mixed_scores(self):
        
        fused_scores = {
            "engagement": 2.0,
            "communication_clarity": 9.0,
            "technical_correctness": 5.0,
            "pacing_structure": 7.0,
            "interactive_quality": 4.0
        }
        
        mentor_score = calculate_mentor_score_mock(fused_scores)
        
        assert 5.0 <= mentor_score <= 6.0
    
    def test_custom_weights_for_mentor_score(self):
        
        fused_scores = {
            "engagement": 10.0,
            "communication_clarity": 0.0,
            "technical_correctness": 0.0,
            "pacing_structure": 0.0,
            "interactive_quality": 0.0
        }
        
        custom_weights = {
            "engagement": 0.9,
            "communication_clarity": 0.025,
            "technical_correctness": 0.025,
            "pacing_structure": 0.025,
            "interactive_quality": 0.025
        }
        
        mentor_score = calculate_mentor_score_mock(fused_scores, custom_weights)
        
        assert mentor_score >= 8.5
    
    def test_fusion_with_partial_data(self):
        
        audio_scores = {"engagement": 8.0}  # Missing other fields
        text_scores = {"correctness": 9.0}  # Missing other fields
        visual_scores = {"presence": 7.0}  # Missing other fields
        
        fused = compute_fusion_scores_mock(audio_scores, text_scores, visual_scores)
        
        assert all(0.0 <= score <= 10.0 for score in fused.values())

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
