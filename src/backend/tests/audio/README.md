# Audio Tests

This directory contains unit tests for audio analysis modules.

## Test Files

- `test_wpm_calculator.py` - Tests for Words Per Minute calculation
- `test_silence_detector.py` - Tests for silence detection and ratio calculation  
- `test_clarity_analyzer.py` - Tests for audio clarity scoring
- `conftest.py` - Shared pytest fixtures and configuration

## Running Tests

```bash
# Run all audio tests
pytest src/backend/tests/audio/ -v

# Run specific test file
pytest src/backend/tests/audio/test_wpm_calculator.py -v

# Run with coverage
pytest src/backend/tests/audio/ --cov=src.backend.pipelines.audio
```

## Note

These tests use **placeholder implementations** since the actual audio analysis modules haven't been built yet. Once the modules are implemented:

1. Update imports to use actual modules instead of mock functions
2. Tests should pass with minimal modifications
3. Add additional integration tests as needed

## Test Coverage

- ✅ WPM calculation with various speech patterns
- ✅ Silence detection with synthetic audio
- ✅ Clarity analysis with sine waves and noise
- ✅ Edge cases (empty audio, invalid files, zero duration)
- ✅ Boundary validation (scores 0-10, timestamps within range)
