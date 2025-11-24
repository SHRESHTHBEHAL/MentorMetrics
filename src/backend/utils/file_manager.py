import shutil
from pathlib import Path
from fastapi import UploadFile
import uuid

class FileManager:
    @staticmethod
    async def validate_video_file(file: UploadFile):
        if not file.content_type.startswith("video/"):
            raise ValueError("File must be a video.")
        return True

    @staticmethod
    def generate_filename(original_filename: str) -> str:
        ext = Path(original_filename).suffix
        return f"{uuid.uuid4()}{ext}"
