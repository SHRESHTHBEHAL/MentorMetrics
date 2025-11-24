from fastapi import APIRouter, HTTPException
from src.backend.models.api_models import ProcessResponse
from uuid import UUID

router = APIRouter()

@router.post("/{session_id}", response_model=ProcessResponse)
async def start_processing(session_id: UUID):
    return ProcessResponse(
        session_id=session_id,
        status="processing_started",
        message="Processing started successfully"
    )
