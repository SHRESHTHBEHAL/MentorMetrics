import whisper
import time
import os
from src.backend.utils.logger import setup_logger
from src.backend.utils.config import Config

logger = setup_logger(__name__)

def run_whisper(audio_path: str) -> dict:
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        model_name = Config.WHISPER_MODEL
        logger.info(f"Loading Whisper model: {model_name}")
        
        start_time = time.time()
        model = whisper.load_model(model_name)
        load_time = time.time() - start_time
        logger.info(f"Model loaded in {load_time:.2f}s")

        logger.info(f"Starting transcription for {audio_path}")
        transcription_start = time.time()
        
        result = model.transcribe(audio_path)
        
        transcription_time = time.time() - transcription_start
        logger.info(f"Transcription completed in {transcription_time:.2f}s")

        return {
            "text": result["text"],
            "segments": [
                {
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"]
                }
                for segment in result["segments"]
            ]
        }

    except Exception as e:
        logger.error(f"Whisper transcription failed: {str(e)}")
        raise RuntimeError(f"Whisper transcription failed: {str(e)}")
