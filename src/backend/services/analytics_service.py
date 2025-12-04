import json
from datetime import datetime
from src.backend.utils.supabase_client import supabase
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class AnalyticsService:
    
    @staticmethod
    def record_event(event_name: str, session_id: str = None, user_id: str = None, metadata: dict = None):
        
        try:
            data = {
                "event_name": event_name,
                "session_id": session_id,
                "user_id": user_id,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = supabase.table("analytics_events").insert(data).execute()
            
            logger.info(f"[Analytics] Recorded event: {event_name} (User: {user_id}, Session: {session_id})")
            return True
            
        except Exception as e:
            logger.error(f"[Analytics] Failed to record event {event_name}: {str(e)}")
            return False
