import time
import json
from fastapi import Request
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

SENSITIVE_FIELDS = ["password", "token", "api_key", "secret", "authorization"]

def sanitize_data(data: dict) -> dict:
    
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in SENSITIVE_FIELDS):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_data(value)
        else:
            sanitized[key] = value
    
    return sanitized

async def log_requests(request: Request, call_next):
    
    start_time = time.time()
    
    logger.info(f"[REQUEST] {request.method} {request.url.path}")
    
    if request.query_params:
        sanitized_params = sanitize_data(dict(request.query_params))
        logger.info(f"[REQUEST] Query params: {sanitized_params}")
    
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            content_type = request.headers.get("content-type", "")
            
            if "application/json" in content_type:
                body = await request.body()
                
                if body:
                    try:
                        body_json = json.loads(body)
                        sanitized_body = sanitize_data(body_json)
                        logger.info(f"[REQUEST] Body: {json.dumps(sanitized_body, indent=2)}")
                    except json.JSONDecodeError:
                        logger.info(f"[REQUEST] Body: <non-JSON content>")
            elif "multipart/form-data" in content_type:
                logger.info(f"[REQUEST] Body: <file upload, not logged>")
            
        except Exception as e:
            logger.warning(f"[REQUEST] Could not log body: {str(e)}")
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    logger.info(f"[RESPONSE] {request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration:.3f}s")
    
    return response

__all__ = ['log_requests']
