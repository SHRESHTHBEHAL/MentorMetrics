import traceback
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.backend.utils.logger import setup_logger
from src.backend.utils.config import Config

logger = setup_logger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    
    logger.warning(
        f"[ERROR] HTTPException: {exc.status_code} - {request.method} {request.url.path}"
    )
    logger.warning(f"[ERROR] Detail: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    
    logger.warning(
        f"[ERROR] ValidationError: {request.method} {request.url.path}"
    )
    logger.warning(f"[ERROR] Validation errors: {exc.errors()}")
    
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "ValidationError",
                "message": "Request validation failed",
                "details": formatted_errors
            }
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    
    logger.error(
        f"[ERROR] Unhandled Exception: {request.method} {request.url.path}"
    )
    logger.error(f"[ERROR] Exception type: {type(exc).__name__}")
    logger.error(f"[ERROR] Exception message: {str(exc)}")
    logger.error(f"[ERROR] Stack trace:", exc_info=True)
    
    include_details = Config.ENV != "production" if hasattr(Config, "ENV") else True
    
    error_response = {
        "error": {
            "type": type(exc).__name__,
            "message": str(exc) or "An internal server error occurred"
        }
    }
    
    if include_details:
        error_response["error"]["details"] = {
            "stack_trace": traceback.format_exc().split("\n")
        }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )

__all__ = [
    'http_exception_handler',
    'validation_exception_handler',
    'global_exception_handler'
]
