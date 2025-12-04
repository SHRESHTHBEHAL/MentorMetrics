import pytest
import json

def parse_llm_response_mock(llm_response: str, expected_fields: list = None):
    
    if expected_fields is None:
        expected_fields = [
            "clarity_score",
            "structure_score",
            "technical_correctness_score",
            "explanation_quality_score",
            "summary_feedback"
        ]
    
    try:
        cleaned = llm_response.replace("```json", "").replace("```", "").strip()
        
        data = json.loads(cleaned)
        
    except json.JSONDecodeError:
        return {
            field: 5.0 if "score" in field else "Unable to parse response"
            for field in expected_fields
        }
    
    result = {}
    
    for field in expected_fields:
        if field in data:
            value = data[field]
            
            if "score" in field:
                try:
                    score = float(value)
                except (ValueError, TypeError):
                    score = 5.0  # Default
                
                score = max(0.0, min(10.0, score))
                result[field] = score
            else:
                result[field] = str(value).strip() if value else ""
        else:
            if "score" in field:
                result[field] = 5.0
            else:
                result[field] = ""
    
    return result

class TestLLMJSONParser:
    
    def test_valid_json_with_all_keys(self):
        
        llm_response = json.dumps({
            "clarity_score": 8.5,
            "structure_score": 7.2,
            "technical_correctness_score": 9.0,
            "explanation_quality_score": 8.0,
            "summary_feedback": "Well structured explanation"
        })
        
        result = parse_llm_response_mock(llm_response)
        
        assert result["clarity_score"] == 8.5
        assert result["structure_score"] == 7.2
        assert result["technical_correctness_score"] == 9.0
        assert result["explanation_quality_score"] == 8.0
        assert result["summary_feedback"] == "Well structured explanation"
    
    def test_missing_fields_use_defaults(self):
        
        llm_response = json.dumps({
            "clarity_score": 7.0,
            "summary_feedback": "Good work"
        })
        
        result = parse_llm_response_mock(llm_response)
        
        assert result["clarity_score"] == 7.0
        assert result["structure_score"] == 5.0  # Default
        assert result["technical_correctness_score"] == 5.0  # Default
        assert result["explanation_quality_score"] == 5.0  # Default
        assert result["summary_feedback"] == "Good work"
    
    def test_numerical_fields_as_strings_converted(self):
        
        llm_response = json.dumps({
            "clarity_score": "8.5",
            "structure_score": "7",
            "technical_correctness_score": "9.0",
            "explanation_quality_score": "6.5",
            "summary_feedback": "Good"
        })
        
        result = parse_llm_response_mock(llm_response)
        
        assert isinstance(result["clarity_score"], float)
        assert result["clarity_score"] == 8.5
        assert isinstance(result["structure_score"], float)
        assert result["structure_score"] == 7.0
    
    def test_out_of_range_values_clamped(self):
        
        llm_response = json.dumps({
            "clarity_score": 15.0,  # Too high
            "structure_score": -3.0,  # Too low
            "technical_correctness_score": 100.0,  # Way too high
            "explanation_quality_score": -50.0,  # Way too low
            "summary_feedback": "Test"
        })
        
        result = parse_llm_response_mock(llm_response)
        
        assert result["clarity_score"] == 10.0  # Clamped
        assert result["structure_score"] == 0.0  # Clamped
        assert result["technical_correctness_score"] == 10.0  # Clamped
        assert result["explanation_quality_score"] == 0.0  # Clamped
    
    def test_malformed_json_returns_fallback(self):
        
        llm_response = "This is not valid JSON at all {broken"
        
        result = parse_llm_response_mock(llm_response)
        
        assert result["clarity_score"] == 5.0
        assert result["structure_score"] == 5.0
        assert result["technical_correctness_score"] == 5.0
        assert result["explanation_quality_score"] == 5.0
        assert result["summary_feedback"] == "Unable to parse response"
    
    def test_extra_fields_ignored_gracefully(self):
        
        llm_response = json.dumps({
            "clarity_score": 8.0,
            "structure_score": 7.0,
            "technical_correctness_score": 9.0,
            "explanation_quality_score": 8.5,
            "summary_feedback": "Good",
            "extra_field_1": "Should be ignored",
            "extra_field_2": 999,
            "random_key": {"nested": "data"}
        })
        
        result = parse_llm_response_mock(llm_response)
        
        assert "extra_field_1" not in result
        assert "extra_field_2" not in result
        assert "random_key" not in result
        
        assert "clarity_score" in result
        assert result["clarity_score"] == 8.0
    
    def test_json_wrapped_in_markdown_code_block(self):
        
        llm_response = 
        
        result = parse_llm_response_mock(llm_response)
        
        assert result["clarity_score"] == 8.0
        assert result["structure_score"] == 7.5
        assert result["summary_feedback"] == "Excellent"
    
    def test_empty_string_response(self):
        
        llm_response = ""
        
        result = parse_llm_response_mock(llm_response)
        
        assert result["clarity_score"] == 5.0
        assert result["summary_feedback"] == "Unable to parse response"
    
    def test_invalid_score_types_use_default(self):
        
        llm_response = json.dumps({
            "clarity_score": "not a number",
            "structure_score": None,
            "technical_correctness_score": {"invalid": "object"},
            "explanation_quality_score": [1, 2, 3],
            "summary_feedback": "Test"
        })
        
        result = parse_llm_response_mock(llm_response)
        
        assert result["clarity_score"] == 5.0
        assert result["structure_score"] == 5.0
        assert result["technical_correctness_score"] == 5.0
        assert result["explanation_quality_score"] == 5.0
    
    def test_summary_cleanup_whitespace(self):
        
        llm_response = json.dumps({
            "clarity_score": 8.0,
            "structure_score": 7.0,
            "technical_correctness_score": 9.0,
            "explanation_quality_score": 8.0,
            "summary_feedback": "   Extra   whitespace   everywhere   "
        })
        
        result = parse_llm_response_mock(llm_response)
        
        assert result["summary_feedback"].startswith("Extra")
        assert result["summary_feedback"].endswith("everywhere")
        assert not result["summary_feedback"].startswith(" ")
    
    def test_empty_summary_field(self):
        
        llm_response = json.dumps({
            "clarity_score": 8.0,
            "structure_score": 7.0,
            "technical_correctness_score": 9.0,
            "explanation_quality_score": 8.0,
            "summary_feedback": ""
        })
        
        result = parse_llm_response_mock(llm_response)
        
        assert result["summary_feedback"] == ""
    
    def test_null_values_handled(self):
        
        llm_response = json.dumps({
            "clarity_score": None,
            "structure_score": 7.0,
            "technical_correctness_score": None,
            "explanation_quality_score": 8.0,
            "summary_feedback": None
        })
        
        result = parse_llm_response_mock(llm_response)
        
        assert result["clarity_score"] == 5.0
        assert result["technical_correctness_score"] == 5.0
        
        assert result["structure_score"] == 7.0
        assert result["explanation_quality_score"] == 8.0
        
        assert result["summary_feedback"] == ""
    
    def test_boundary_values(self):
        
        llm_response = json.dumps({
            "clarity_score": 0.0,
            "structure_score": 10.0,
            "technical_correctness_score": 0,
            "explanation_quality_score": 10,
            "summary_feedback": "Boundary test"
        })
        
        result = parse_llm_response_mock(llm_response)
        
        assert result["clarity_score"] == 0.0
        assert result["structure_score"] == 10.0
        assert result["technical_correctness_score"] == 0.0
        assert result["explanation_quality_score"] == 10.0
    
    def test_decimal_precision_preserved(self):
        
        llm_response = json.dumps({
            "clarity_score": 8.123456,
            "structure_score": 7.999,
            "technical_correctness_score": 9.001,
            "explanation_quality_score": 6.5,
            "summary_feedback": "Precision test"
        })
        
        result = parse_llm_response_mock(llm_response)
        
        assert abs(result["clarity_score"] - 8.123456) < 0.0001
        assert abs(result["structure_score"] - 7.999) < 0.0001
        assert abs(result["technical_correctness_score"] - 9.001) < 0.0001

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
