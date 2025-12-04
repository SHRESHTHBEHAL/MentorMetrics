# Visual Analysis Tests

This directory contains unit tests for visual analysis modules.

## Test Files

- `test_frame_extractor.py` - Tests for video frame extraction
- `test_mediapipe_detector.py` - Tests for MediaPipe-based detection (face, hands, gaze)

## Test Video Requirement

The tests require a test video file at:
```
/backend/tests/assets/test_video.mp4
```

### Creating a Test Video

You can create a 3-second test video using FFmpeg:

```bash
# Navigate to assets directory
cd src/backend/tests/assets/

# Create a 3-second test video with test pattern
ffmpeg -f lavfi -i testsrc=duration=3:size=640x480:rate=30 test_video.mp4

# OR create from a real video (trim to 3 seconds)
ffmpeg -i your_video.mp4 -t 3 -c copy test_video.mp4
```

**Note:** Tests will automatically skip if the test video is not found.

## Running Tests

```bash
# Run all visual tests
pytest src/backend/tests/visual/ -v

# Run specific test file
pytest src/backend/tests/visual/test_frame_extractor.py -v
pytest src/backend/tests/visual/test_mediapipe_detector.py -v

# Run with coverage
pytest src/backend/tests/visual/ --cov=src.backend.pipelines.visual
```

## Test Coverage

### Frame Extractor Tests
- ✅ Returns list of frame objects
- ✅ Each frame contains frame data + timestamp
- ✅ FPS sampling accuracy (1 FPS, 2 FPS)
- ✅ Invalid video path raises clean error
- ✅ Large FPS values limited by max_frames
- ✅ Frame dimensions validation
- ✅ Sequential timestamp ordering
- ✅ First frame near 0 timestamp
- ✅ Video metadata extraction
- ✅ Zero/negative FPS handling

### MediaPipe Detector Tests
- ✅ Face detection with clear face frame
- ✅ No detection with empty frame
- ✅ Hand detection returns consistent count (0-2)
- ✅ Gaze direction detection (forward/away/down/unknown)
- ✅ Null frame safe fallback
- ✅ Invalid frame format handled
- ✅ Empty/white frames handled
- ✅ Small and large frame dimensions
- ✅ Landmarks structure validation
- ✅ Consistency across multiple analyses
- ✅ Noisy frame handling

## Note

These tests use **placeholder implementations** with synthetic frames. Once the actual visual analysis modules are implemented using OpenCV and MediaPipe, update the imports accordingly.
