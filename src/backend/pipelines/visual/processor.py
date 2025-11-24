from src.backend.pipelines.base import BaseProcessor

class VisualProcessor(BaseProcessor):
    def process(self, video_path):
        print(f"Visual Processing: {video_path}")
        return {"visual_metrics": "Placeholder visual metrics"}
