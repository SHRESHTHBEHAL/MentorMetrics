import pytest
from unittest.mock import Mock

def calculate_wpm_mock(segments, total_duration):
    
    if not segments or total_duration <= 0:
        return None
    
    total_words = sum(len(seg.get("text", "").split()) for seg in segments)
    duration_minutes = total_duration / 60.0
    
    if duration_minutes == 0:
        return None
    
    return total_words / duration_minutes

class TestWPMCalculator:
    
    def test_wpm_calculation_with_normal_speech(self):
        
        segments = [
            {"text": "Hello world this is a test", "start": 0.0, "end": 2.0},
            {"text": "We are testing the WPM calculator", "start": 2.0, "end": 4.0}
        ]
        total_duration = 4.0  # 4 seconds
        
        wpm = calculate_wpm_mock(segments, total_duration)
        
        assert wpm is not None
        assert abs(wpm - 180.0) < 0.1
    
    def test_wpm_calculation_with_slow_speech(self):
        
        segments = [
            {"text": "One two three four five", "start": 0.0, "end": 10.0}
        ]
        total_duration = 10.0  # 10 seconds
        
        wpm = calculate_wpm_mock(segments, total_duration)
        
        assert wpm is not None
        assert abs(wpm - 30.0) < 0.1
    
    def test_wpm_calculation_with_fast_speech(self):
        
        segments = [
            {"text": " ".join(["word"] * 50), "start": 0.0, "end": 10.0}
        ]
        total_duration = 10.0
        
        wpm = calculate_wpm_mock(segments, total_duration)
        
        assert wpm is not None
        assert abs(wpm - 300.0) < 0.1
    
    def test_extremely_short_duration(self):
        
        segments = [
            {"text": "Quick", "start": 0.0, "end": 0.1}
        ]
        total_duration = 0.1  # 100ms
        
        wpm = calculate_wpm_mock(segments, total_duration)
        
        assert wpm is not None
        assert wpm > 0
    
    def test_empty_segments_returns_none(self):
        
        wpm = calculate_wpm_mock([], 10.0)
        assert wpm is None
    
    def test_zero_duration_returns_none(self):
        
        segments = [{"text": "Hello world", "start": 0.0, "end": 0.0}]
        wpm = calculate_wpm_mock(segments, 0.0)
        assert wpm is None
    
    def test_negative_duration_returns_none(self):
        
        segments = [{"text": "Hello world", "start": 0.0, "end": 2.0}]
        wpm = calculate_wpm_mock(segments, -5.0)
        assert wpm is None
    
    def test_segments_with_empty_text(self):
        
        segments = [
            {"text": "", "start": 0.0, "end": 2.0},
            {"text": "   ", "start": 2.0, "end": 4.0}
        ]
        total_duration = 4.0
        
        wpm = calculate_wpm_mock(segments, total_duration)
        
        assert wpm is not None
        assert wpm == 0.0
    
    def test_segments_with_punctuation(self):
        
        segments = [
            {"text": "Hello, world! How are you?", "start": 0.0, "end": 3.0}
        ]
        total_duration = 3.0
        
        wpm = calculate_wpm_mock(segments, total_duration)
        
        assert wpm is not None
        assert abs(wpm - 100.0) < 0.1
    
    def test_multiple_spaces_in_text(self):
        
        segments = [
            {"text": "Word    with    spaces", "start": 0.0, "end": 2.0}
        ]
        total_duration = 2.0
        
        wpm = calculate_wpm_mock(segments, total_duration)
        
        assert wpm is not None
        assert wpm > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
