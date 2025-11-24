from supabase import create_client, Client
from src.backend.utils.config import Config

def get_supabase_client() -> Client:
    Config.validate()
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

supabase = get_supabase_client()
