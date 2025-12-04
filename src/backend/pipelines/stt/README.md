# STT Pipeline

This directory contains the Speech-to-Text processing logic.

## Audio Extraction

The STT pipeline uses the `extract_audio_from_video` utility to convert uploaded videos into 16kHz mono WAV files suitable for Whisper.

### Usage

```python
from src.backend.utils.audio_extractor import extract_audio_from_video

video_path = "path/to/video.mp4"
audio_path = "path/to/output.wav"

try:
    final_audio_path = extract_audio_from_video(video_path, audio_path)
    print(f"Audio extracted to: {final_audio_path}")
except Exception as e:
    print(f"Error: {e}")
```

### Specifications
- **Sample Rate**: 16000 Hz
- **Channels**: Mono (1)
- **Format**: WAV (pcm_s16le)
