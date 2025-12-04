import time
import os
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
UPLOAD_RATE_LIMIT = int(os.getenv("UPLOAD_RATE_LIMIT", "5"))
PROCESS_RATE_LIMIT = int(os.getenv("PROCESS_RATE_LIMIT", "10"))

_rate_limit_store = {}

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not RATE_LIMIT_ENABLED:
            return await call_next(request)

        client_id = request.client.host if request.client else "unknown"
        path = request.url.path

        limit = None
        window_seconds = 60
        endpoint_key = None

        if "/api/upload" in path and request.method == "POST":
            limit = UPLOAD_RATE_LIMIT
            endpoint_key = "upload"
        elif "/api/process" in path and request.method == "POST":
            limit = PROCESS_RATE_LIMIT
            endpoint_key = "process"
        
        if limit is None:
            return await call_next(request)

        current_time = time.time()
        
        if client_id not in _rate_limit_store:
            _rate_limit_store[client_id] = {}
        
        if endpoint_key not in _rate_limit_store[client_id]:
            _rate_limit_store[client_id][endpoint_key] = {
                "count": 0,
                "reset_time": current_time + window_seconds
            }
        
        bucket = _rate_limit_store[client_id][endpoint_key]
        
        if current_time > bucket["reset_time"]:
            bucket["count"] = 0
            bucket["reset_time"] = current_time + window_seconds
            
        if bucket["count"] >= limit:
            logger.warning(f"[RateLimit] Limit exceeded for {client_id} on {endpoint_key}")
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded. Try again later."}
            )
            
        bucket["count"] += 1
        
        response = await call_next(request)
        return response
