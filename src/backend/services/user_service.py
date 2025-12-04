from fastapi import Request, HTTPException, status
from src.backend.utils.supabase_client import supabase
from src.backend.utils.logger import setup_logger
import os

logger = setup_logger(__name__)

DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"

class UserService:
    @staticmethod
    def get_user_id(request: Request) -> str:
        
        auth_header = request.headers.get("Authorization")
        
        if DEV_MODE:
            user_id_header = request.headers.get("X-User-ID")
            if user_id_header and user_id_header.strip():
                logger.info(f"Using X-User-ID header in dev mode: {user_id_header}")
                return user_id_header
        
        if not auth_header:
            if DEV_MODE:
                logger.warning("Missing Authorization header - using dev mode mock user")
                return "00000000-0000-0000-0000-000000000001"
            else:
                logger.warning("Missing Authorization header")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing authentication token"
                )
        
        try:
            if " " in auth_header:
                token = auth_header.split(" ")[1]
            else:
                token = auth_header
                
            user_response = supabase.auth.get_user(token)
            
            if not user_response or not user_response.user:
                if DEV_MODE:
                    logger.warning("Invalid token - using dev mode mock user")
                    return "00000000-0000-0000-0000-000000000001"
                raise ValueError("Invalid user token")
                
            return user_response.user.id
            
        except Exception as e:
            if DEV_MODE:
                logger.warning(f"Authentication failed - using dev mode mock user: {str(e)}")
                return "00000000-0000-0000-0000-000000000001"
            logger.error(f"Authentication failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token"
            )
