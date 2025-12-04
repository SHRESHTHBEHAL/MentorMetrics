import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    DATABASE_URL = os.getenv("DATABASE_URL")
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.getcwd(), "uploads"))

    @staticmethod
    def validate():
        if not Config.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is not set")
        if not Config.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is not set")
