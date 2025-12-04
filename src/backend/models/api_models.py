from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class SessionBase(BaseModel):
    filename: str
    file_url: str
    status: str = "uploaded"

class SessionCreate(SessionBase):
    user_id: Optional[UUID] = None

class SessionResponse(SessionBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProcessResponse(BaseModel):
    session_id: UUID
    status: str
    message: str

class UploadResponse(BaseModel):
    session_id: UUID
    user_id: str
    file_url: str
    message: str

class TranscriptCreate(BaseModel):
    session_id: UUID
    raw_text: str
    segments: list[Dict[str, Any]]
    word_timestamps: Optional[list[Dict[str, Any]]] = None

class TranscriptDB(TranscriptCreate):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AudioFeaturesCreate(BaseModel):
    session_id: UUID
    words_per_minute: float
    silence_ratio: float
    avg_volume: float
    volume_variation: float
    clarity_score: float
    raw_features: Optional[Dict[str, Any]] = None

class AudioFeaturesDB(AudioFeaturesCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
