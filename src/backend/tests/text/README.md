# Text Evaluation Tests

This directory contains unit tests for text evaluation and parsing modules.

## Test Files

- `test_text_parser.py` - Tests for LLM JSON response parsing and validation

## Running Tests

```bash
# Run all text tests
pytest src/backend/tests/text/ -v

# Run specific test file
pytest src/backend/tests/text/test_text_parser.py -v

# Run with coverage
pytest src/backend/tests/text/ --cov=src.backend.pipelines.text
```

## Test Coverage

### JSON Parser Tests
- ✅ Valid JSON with all keys
- ✅ Missing fields filled with defaults
- ✅ String numbers converted to floats
- ✅ Out-of-range values clamped (0-10)
- ✅ Malformed JSON returns safe fallback
- ✅ Extra fields ignored gracefully
- ✅ Markdown code blocks stripped
- ✅ Empty/null values handled
- ✅ Whitespace cleanup in text fields
- ✅ Boundary values (0.0, 10.0)
- ✅ Decimal precision preserved

## Note

These tests use **placeholder implementations** for the JSON parser. Once the actual text evaluation modules are implemented, update the imports accordingly.
