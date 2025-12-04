from fastapi import APIRouter, HTTPException, Request, Depends, Query
from typing import Optional, List
from src.backend.services.user_service import UserService
from src.backend.utils.supabase_client import supabase
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.get("/logs")
def get_admin_logs(
    request: Request,
    event_type: Optional[str] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    
    logger.info(f"[Admin] GET /logs requested")
    
    current_user_id = UserService.get_user_id(request)
    
    try:
        query = supabase.table("analytics_events").select("*").order("timestamp", desc=True)
        
        if event_type:
            query = query.eq("event_name", event_type)
        
        if session_id:
            query = query.eq("session_id", session_id)
            
        if user_id:
            query = query.eq("user_id", user_id)
            
        query = query.range(offset, offset + limit - 1)
        
        result = query.execute()
        
        return {
            "data": result.data,
            "count": len(result.data), # Approximate count of fetched items
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"[Admin] Error fetching logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch logs: {str(e)}")
