import pytest
import numpy as np

def detect_silence_mock(audio_data, sample_rate, silence_threshold=-40):
    
    if audio_data is None or len(audio_data) == 0:
        return []
    
    frame_size = int(sample_rate * 0.1)  # 100ms frames
    silence_segments = []
    
    for i in range(0, len(audio_data), frame_size):
        frame = audio_data[i:i + frame_size]
        if len(frame) == 0:
            continue
        
        rms = np.sqrt(np.mean(frame ** 2))
        rms_db = 20 * np.log10(rms + 1e-10)
        
        if rms_db < silence_threshold:
            start_time = i / sample_rate
            end_time = (i + len(frame)) / sample_rate
            silence_segments.append((start_time, end_time))
    
    return silence_segments

def calculate_silence_ratio_mock(silence_segments, total_duration):
    
    if not silence_segments or total_duration <= 0:
        return 0.0
    
    total_silence = sum(end - start for start, end in silence_segments)
    return min(total_silence / total_duration, 1.0)

class TestSilenceDetector:
    
    def test_completely_silent_audio(self):
        
        sample_rate = 16000
        duration = 2.0
        audio_data = np.zeros(int(sample_rate * duration))
        
        silence_segments = detect_silence_mock(audio_data, sample_rate)
        
        assert len(silence_segments) > 0
        assert silence_segments[0][0] >= 0  # Start time
        assert silence_segments[-1][1] <= duration  # End time
    
    def test_completely_active_audio(self):
        
        sample_rate = 16000
        duration = 2.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440Hz sine wave
        
        silence_segments = detect_silence_mock(audio_data, sample_rate)
        
        assert len(silence_segments) < 5  # Allow some due to frame boundaries
    
    def test_alternating_silence_and_sound(self):
        
        sample_rate = 16000
        duration = 4.0
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.zeros_like(t)
        
        audio_data[0:sample_rate] = 0.5 * np.sin(2 * np.pi * 440 * t[0:sample_rate])
        audio_data[2*sample_rate:3*sample_rate] = 0.5 * np.sin(2 * np.pi * 440 * t[0:sample_rate])
        
        silence_segments = detect_silence_mock(audio_data, sample_rate)
        
        assert len(silence_segments) > 0
    
    def test_silence_ratio_calculation(self):
        
        silence_segments = [
            (0.0, 1.0),   # 1 second
            (3.0, 4.5)    # 1.5 seconds
        ]
        total_duration = 10.0
        
        ratio = calculate_silence_ratio_mock(silence_segments, total_duration)
        
        assert abs(ratio - 0.25) < 0.01
    
    def test_silence_ratio_with_no_silence(self):
        
        silence_segments = []
        total_duration = 10.0
        
        ratio = calculate_silence_ratio_mock(silence_segments, total_duration)
        
        assert ratio == 0.0
    
    def test_silence_ratio_with_full_silence(self):
        
        silence_segments = [(0.0, 10.0)]
        total_duration = 10.0
        
        ratio = calculate_silence_ratio_mock(silence_segments, total_duration)
        
        assert abs(ratio - 1.0) < 0.01
    
    def test_silence_timestamp_boundaries(self):
        
        sample_rate = 16000
        duration = 5.0
        audio_data = np.zeros(int(sample_rate * duration))
        
        silence_segments = detect_silence_mock(audio_data, sample_rate)
        
        for start, end in silence_segments:
            assert start >= 0.0
            assert end <= duration
            assert end > start
    
    def test_empty_audio_returns_empty_segments(self):
        
        audio_data = np.array([])
        sample_rate = 16000
        
        silence_segments = detect_silence_mock(audio_data, sample_rate)
        
        assert silence_segments == []
    
    def test_none_audio_returns_empty_segments(self):
        
        silence_segments = detect_silence_mock(None, 16000)
        
        assert silence_segments == []
    
    def test_silence_with_different_thresholds(self):
        
        sample_rate = 16000
        duration = 2.0
        
        audio_data = 0.01 * np.random.randn(int(sample_rate * duration))
        
        strict_segments = detect_silence_mock(audio_data, sample_rate, silence_threshold=-30)
        
        lenient_segments = detect_silence_mock(audio_data, sample_rate, silence_threshold=-50)
        
        assert len(strict_segments) >= len(lenient_segments)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
