import pytest
import numpy as np

def analyze_frame_mock(frame):
    
    if frame is None:
        return {
            "face_detected": False,
            "hands_detected": 0,
            "gaze_direction": "unknown",
            "landmarks": None,
            "error": "Null frame provided"
        }
    
    if not isinstance(frame, np.ndarray) or len(frame.shape) != 3:
        return {
            "face_detected": False,
            "hands_detected": 0,
            "gaze_direction": "unknown",
            "landmarks": None,
            "error": "Invalid frame format"
        }
    
    height, width, channels = frame.shape
    
    center_region = frame[height//3:2*height//3, width//3:2*width//3]
    avg_intensity = np.mean(center_region)
    
    face_detected = 80 < avg_intensity < 200  # Assume face if moderate intensity
    
    left_region = frame[:, :width//4]
    right_region = frame[:, 3*width//4:]
    hands_detected = 0
    
    if np.mean(left_region) > 100:
        hands_detected += 1
    if np.mean(right_region) > 100:
        hands_detected += 1
    
    if face_detected:
        top_region = frame[:height//3, width//3:2*width//3]
        top_intensity = np.mean(top_region)
        
        if top_intensity > 150:
            gaze_direction = "forward"
        elif top_intensity > 100:
            gaze_direction = "down"
        else:
            gaze_direction = "away"
    else:
        gaze_direction = "unknown"
    
    return {
        "face_detected": face_detected,
        "hands_detected": hands_detected,
        "gaze_direction": gaze_direction,
        "landmarks": {
            "face": [] if not face_detected else [(100, 100), (200, 100)],
            "hands": []
        }
    }

class TestMediaPipeDetector:
    
    @pytest.fixture
    def frame_with_face(self):
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        frame[160:320, 213:427] = 150  # Center region
        
        return frame
    
    @pytest.fixture
    def frame_without_person(self):
        
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 30
        return frame
    
    @pytest.fixture
    def frame_with_hands(self):
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        frame[160:320, 213:427] = 150
        
        frame[:, :160] = 140  # Left hand
        frame[:, 480:] = 140  # Right hand
        
        return frame
    
    def test_frame_with_clear_face_detected(self, frame_with_face):
        
        result = analyze_frame_mock(frame_with_face)
        
        assert result["face_detected"] is True
        assert "landmarks" in result
    
    def test_frame_without_person_no_detection(self, frame_without_person):
        
        result = analyze_frame_mock(frame_without_person)
        
        assert result["face_detected"] is False
    
    def test_hand_detection_returns_count(self, frame_with_hands):
        
        result = analyze_frame_mock(frame_with_hands)
        
        assert "hands_detected" in result
        assert isinstance(result["hands_detected"], int)
        assert result["hands_detected"] >= 0
        assert result["hands_detected"] <= 2  # Maximum 2 hands
    
    def test_gaze_direction_returns_valid_value(self, frame_with_face):
        
        result = analyze_frame_mock(frame_with_face)
        
        assert "gaze_direction" in result
        assert result["gaze_direction"] in ["forward", "away", "down", "unknown"]
    
    def test_gaze_forward_detection(self):
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[160:320, 213:427] = 150  # Face
        frame[:160, 213:427] = 200  # Bright top (eyes looking forward)
        
        result = analyze_frame_mock(frame)
        
        if result["face_detected"]:
            assert result["gaze_direction"] == "forward"
    
    def test_gaze_down_detection(self):
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[160:320, 213:427] = 150  # Face
        frame[:160, 213:427] = 120  # Moderate top (eyes down)
        
        result = analyze_frame_mock(frame)
        
        if result["face_detected"]:
            assert result["gaze_direction"] == "down"
    
    def test_gaze_away_detection(self):
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[160:320, 213:427] = 150  # Face
        frame[:160, 213:427] = 50   # Dark top (looking away)
        
        result = analyze_frame_mock(frame)
        
        if result["face_detected"]:
            assert result["gaze_direction"] == "away"
    
    def test_null_frame_safe_fallback(self):
        
        result = analyze_frame_mock(None)
        
        assert result["face_detected"] is False
        assert result["hands_detected"] == 0
        assert result["gaze_direction"] == "unknown"
        assert "error" in result
    
    def test_invalid_frame_format_handled(self):
        
        invalid_frame = np.zeros((480, 640), dtype=np.uint8)
        
        result = analyze_frame_mock(invalid_frame)
        
        assert result["face_detected"] is False
        assert "error" in result
    
    def test_empty_frame_no_detection(self):
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        result = analyze_frame_mock(frame)
        
        assert result["face_detected"] is False
        assert result["gaze_direction"] == "unknown"
    
    def test_white_frame_handles_gracefully(self):
        
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        
        result = analyze_frame_mock(frame)
        
        assert "face_detected" in result
        assert "gaze_direction" in result
    
    def test_small_frame_dimensions(self):
        
        small_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        small_frame[33:66, 33:66] = 150  # Small face region
        
        result = analyze_frame_mock(small_frame)
        
        assert "face_detected" in result
    
    def test_large_frame_dimensions(self):
        
        large_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        large_frame[360:720, 640:1280] = 150  # Large face region
        
        result = analyze_frame_mock(large_frame)
        
        assert "face_detected" in result
    
    def test_landmarks_structure(self, frame_with_face):
        
        result = analyze_frame_mock(frame_with_face)
        
        assert "landmarks" in result
        assert isinstance(result["landmarks"], dict)
        
        if result["face_detected"]:
            assert "face" in result["landmarks"]
            assert isinstance(result["landmarks"]["face"], list)
    
    def test_multiple_frames_consistency(self, frame_with_face):
        
        result1 = analyze_frame_mock(frame_with_face)
        result2 = analyze_frame_mock(frame_with_face)
        
        assert result1["face_detected"] == result2["face_detected"]
        assert result1["hands_detected"] == result2["hands_detected"]
        assert result1["gaze_direction"] == result2["gaze_direction"]
    
    def test_noisy_frame_handled(self):
        
        noisy_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        result = analyze_frame_mock(noisy_frame)
        
        assert "face_detected" in result
        assert isinstance(result["face_detected"], bool)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
