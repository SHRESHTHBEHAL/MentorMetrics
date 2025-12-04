# Test Assets Directory

This directory contains test assets for unit tests.

## Required Assets

### Test Video
- **File**: `test_video.mp4`
- **Requirements**: 2-3 seconds duration, 640x480 or similar resolution
- **Used by**: `tests/visual/test_frame_extractor.py`

### Creating Test Video

```bash
# Simple test pattern (recommended)
ffmpeg -f lavfi -i testsrc=duration=3:size=640x480:rate=30 test_video.mp4

# Color bars pattern
ffmpeg -f lavfi -i smptebars=duration=3:size=640x480:rate=30 test_video.mp4

# From existing video (trim to 3 seconds)
ffmpeg -i source_video.mp4 -t 3 -c copy test_video.mp4
```

### Test Audio (Future)
- **File**: `test_audio.wav`
- **Requirements**: 3-5 seconds, mono or stereo, 16kHz sample rate
- **Used by**: `tests/audio/test_whisper_engine.py` (when implemented)

```bash
# Create silent audio
ffmpeg -f lavfi -i anullsrc=duration=3 -ar 16000 test_audio.wav

# Create sine wave
ffmpeg -f lavfi -i "sine=frequency=440:duration=3" -ar 16000 test_audio.wav
```

## .gitignore

Large test files (>1MB) should be added to `.gitignore` and documented here for developers to create locally.
