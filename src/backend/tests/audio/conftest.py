import pytest
import numpy as np

@pytest.fixture
def sample_rate():
    
    return 16000

@pytest.fixture
def short_duration():
    
    return 1.0

@pytest.fixture
def medium_duration():
    
    return 3.0

@pytest.fixture
def generate_sine_wave():
    
    def _generate(frequency=440, amplitude=0.5, duration=1.0, sample_rate=16000):
        t = np.linspace(0, duration, int(sample_rate * duration))
        return amplitude * np.sin(2 * np.pi * frequency * t)
    
    return _generate

@pytest.fixture
def generate_silence():
    
    def _generate(duration=1.0, sample_rate=16000):
        return np.zeros(int(sample_rate * duration))
    
    return _generate

@pytest.fixture
def generate_white_noise():
    
    def _generate(amplitude=0.1, duration=1.0, sample_rate=16000):
        return amplitude * np.random.randn(int(sample_rate * duration))
    
    return _generate

@pytest.fixture
def mock_transcript_segments():
    
    return [
        {"text": "Hello world", "start": 0.0, "end": 1.0},
        {"text": "This is a test", "start": 1.0, "end": 3.0},
        {"text": "Of the WPM calculator", "start": 3.0, "end": 5.0}
    ]
