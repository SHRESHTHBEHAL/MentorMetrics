import pytest
import numpy as np

def analyze_clarity_mock(audio_file_path=None, audio_data=None, sample_rate=16000):
    
    if audio_data is None:
        if audio_file_path is None:
            raise ValueError("Either audio_file_path or audio_data must be provided")
        
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    if len(audio_data) == 0:
        return {
            "rms_energy": 0.0,
            "clarity_score": 0.0,
            "is_valid": False
        }
    
    rms = np.sqrt(np.mean(audio_data ** 2))
    
    rms_db = 20 * np.log10(rms + 1e-10)
    
    clarity_score = np.clip((rms_db + 30) / 2, 0, 10)
    
    return {
        "rms_energy": float(rms),
        "rms_db": float(rms_db),
        "clarity_score": float(clarity_score),
        "is_valid": True
    }

class TestClarityAnalyzer:
    
    def test_clarity_with_clear_sine_wave(self):
        
        sample_rate = 16000
        duration = 2.0
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        result = analyze_clarity_mock(audio_data=audio_data, sample_rate=sample_rate)
        
        assert result["is_valid"] is True
        assert result["rms_energy"] > 0
        assert isinstance(result["clarity_score"], (int, float))
        assert 0 <= result["clarity_score"] <= 10
    
    def test_clarity_with_loud_audio(self):
        
        sample_rate = 16000
        duration = 1.0
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = 0.8 * np.sin(2 * np.pi * 440 * t)
        
        result = analyze_clarity_mock(audio_data=audio_data, sample_rate=sample_rate)
        
        assert result["clarity_score"] > 5  # Should be high for clear, loud audio
        assert result["rms_energy"] > 0.5  # High energy
    
    def test_clarity_with_quiet_audio(self):
        
        sample_rate = 16000
        duration = 1.0
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = 0.01 * np.sin(2 * np.pi * 440 * t)
        
        result = analyze_clarity_mock(audio_data=audio_data, sample_rate=sample_rate)
        
        assert result["clarity_score"] < 5  # Should be low for very quiet audio
        assert result["rms_energy"] < 0.1  # Low energy
    
    def test_clarity_with_noisy_audio(self):
        
        sample_rate = 16000
        duration = 1.0
        
        audio_data = 0.1 * np.random.randn(int(sample_rate * duration))
        
        result = analyze_clarity_mock(audio_data=audio_data, sample_rate=sample_rate)
        
        assert result["is_valid"] is True
        assert result["rms_energy"] > 0
        assert 0 <= result["clarity_score"] <= 10
    
    def test_rms_energy_values_are_numeric(self):
        
        sample_rate = 16000
        duration = 0.5
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = 0.5 * np.sin(2 * np.pi * 220 * t)
        
        result = analyze_clarity_mock(audio_data=audio_data, sample_rate=sample_rate)
        
        assert isinstance(result["rms_energy"], (int, float))
        assert not np.isnan(result["rms_energy"])
        assert not np.isinf(result["rms_energy"])
    
    def test_clarity_score_is_bounded(self):
        
        sample_rate = 16000
        
        for amplitude in [0.01, 0.1, 0.5, 0.9, 1.0]:
            duration = 1.0
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio_data = amplitude * np.sin(2 * np.pi * 440 * t)
            
            result = analyze_clarity_mock(audio_data=audio_data, sample_rate=sample_rate)
            
            assert 0 <= result["clarity_score"] <= 10
    
    def test_empty_audio_returns_invalid(self):
        
        audio_data = np.array([])
        
        result = analyze_clarity_mock(audio_data=audio_data, sample_rate=16000)
        
        assert result["is_valid"] is False
        assert result["rms_energy"] == 0.0
        assert result["clarity_score"] == 0.0
    
    def test_silent_audio_low_clarity(self):
        
        sample_rate = 16000
        duration = 2.0
        audio_data = np.zeros(int(sample_rate * duration))
        
        result = analyze_clarity_mock(audio_data=audio_data, sample_rate=sample_rate)
        
        assert result["clarity_score"] == 0.0
        assert result["rms_energy"] == 0.0
    
    def test_missing_audio_file_raises_error(self):
        
        with pytest.raises(FileNotFoundError):
            analyze_clarity_mock(audio_file_path="/path/to/nonexistent/file.wav")
    
    def test_no_audio_data_raises_error(self):
        
        with pytest.raises(ValueError):
            analyze_clarity_mock()
    
    def test_clarity_with_multiple_frequencies(self):
        
        sample_rate = 16000
        duration = 1.0
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = (
            0.2 * np.sin(2 * np.pi * 262 * t) +  # C
            0.2 * np.sin(2 * np.pi * 330 * t) +  # E
            0.2 * np.sin(2 * np.pi * 392 * t)    # G
        )
        
        result = analyze_clarity_mock(audio_data=audio_data, sample_rate=sample_rate)
        
        assert result["is_valid"] is True
        assert result["rms_energy"] > 0
        assert 0 <= result["clarity_score"] <= 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
