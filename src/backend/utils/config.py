import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")

    @staticmethod
    def validate():
        if not Config.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is not set")
        if not Config.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is not set")
