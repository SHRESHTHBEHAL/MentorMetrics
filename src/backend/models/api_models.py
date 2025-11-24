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
    file_url: str
    message: str
