from src.backend.pipelines.base import BaseProcessor

class STTProcessor(BaseProcessor):
    def process(self, audio_path):
        print(f"STT Processing: {audio_path}")
        return {"text": "Placeholder transcript"}
