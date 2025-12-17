import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
from src.backend.utils.logger import setup_logger
from src.backend.middleware.rate_limiter import RateLimitMiddleware
from src.backend.api import upload, process, results_api, sessions_api, download_api, analytics_api, admin_api, debug_api

load_dotenv()

logger = setup_logger(__name__)

app = FastAPI(
    title="MentorMetrics API",
    description="Backend API for MentorMetrics AI Coaching Platform",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    os.getenv("FRONTEND_URL", "")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in origins if origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)

app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(process.router, prefix="/api/process", tags=["Process"])
app.include_router(results_api.router, prefix="/api/results", tags=["Results"])
app.include_router(sessions_api.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(sessions_api.router, prefix="/api/status", tags=["Status"])  # Status endpoint uses sessions router
app.include_router(download_api.router, prefix="/api/download", tags=["Download"])
app.include_router(analytics_api.router, prefix="/api", tags=["Analytics"])
app.include_router(admin_api.router, prefix="/api/admin", tags=["Admin"])
app.include_router(debug_api.router, prefix="/api/debug", tags=["Debug"])
from src.backend.api import live_analysis
app.include_router(live_analysis.router, prefix="/api/live", tags=["Live"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "MentorMetrics Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.backend.main:app", host="0.0.0.0", port=8000, reload=True)
