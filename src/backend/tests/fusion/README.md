# Fusion Tests

This directory contains unit tests for multimodal fusion and score calculation.

## Test Files

- `test_fusion_engine.py` - Tests for fusion engine and mentor score calculation

## Running Tests

```bash
# Run all fusion tests
pytest src/backend/tests/fusion/ -v

# Run specific test
pytest src/backend/tests/fusion/test_fusion_engine.py -v

# Run with coverage
pytest src/backend/tests/fusion/ --cov=src.backend.pipelines.fusion
```

## Test Coverage

### Fusion Engine Tests
- ✅ Normal scenario with all modalities present
- ✅ Missing audio → defaults used
- ✅ Missing text → defaults used
- ✅ Missing visual → defaults used
- ✅ Negative values clamped to 0
- ✅ Values >10 clamped to 10
- ✅ SCORING_RUBRIC weights sum to 1.0 per parameter
- ✅ Final mentor score within 0-10 bounds
- ✅ Mentor score calculation accuracy
- ✅ Extreme low scores (all 0)
- ✅ Extreme high scores (all 10)
- ✅ Mixed good/bad scores
- ✅ Custom weight configurations
- ✅ Partial data within modalities

## Design

Tests use **mock numeric inputs** rather than depending on real pipeline output. This ensures:
- Fast test execution
- Predictable results
- Isolation from other components
- Easy verification of fusion logic

## Note

These tests use **placeholder implementations**. Once the actual fusion modules are implemented, update the imports accordingly.
