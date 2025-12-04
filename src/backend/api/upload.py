from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from src.backend.services.session_service import SessionService
from src.backend.services.user_service import UserService
from src.backend.services.analytics_service import AnalyticsService
from src.backend.utils.logger import setup_logger
from src.backend.utils.supabase_client import supabase
from src.backend.utils.file_manager import FileManager
from src.backend.models.api_models import UploadResponse
import os

router = APIRouter()
logger = setup_logger(__name__)

@router.post("/", response_model=UploadResponse)
async def upload_video(
    request: Request,
    file: UploadFile = File(...)
):
    try:
        user_id = UserService.get_user_id(request)
        
        AnalyticsService.record_event(
            event_name="upload_start",
            user_id=user_id,
            metadata={"filename": file.filename, "content_type": file.content_type}
        )
        
        await FileManager.validate_video_file(file)
        
        filename = FileManager.generate_filename(file.filename)
        
        content = await file.read()
        
        bucket_name = "videos"
        res = supabase.storage.from_(bucket_name).upload(
            path=filename,
            file=content,
            file_options={"content-type": file.content_type}
        )
        
        public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
        
        session_data = {
            "user_id": user_id,
            "file_url": public_url,
            "filename": filename,
            "status": "uploaded"
        }
        
        response = supabase.table("sessions").insert(session_data).execute()
        data = response.data
        
        if not data or len(data) == 0:
             raise HTTPException(status_code=500, detail="Failed to create session record")
             
        session = data[0]
        
        logger.info(f"Video uploaded successfully for user {user_id}: {session['id']}")
        
        AnalyticsService.record_event(
            event_name="upload_success",
            session_id=session['id'],
            user_id=user_id,
            metadata={"filename": filename, "size": len(content)}
        )
        
        return UploadResponse(
            session_id=session['id'],
            user_id=user_id,
            file_url=public_url,
            message="Video uploaded successfully"
        )

    except HTTPException:
        AnalyticsService.record_event(
            event_name="upload_failed",
            user_id=user_id if 'user_id' in locals() else None,
            metadata={"error": "HTTPException", "filename": file.filename}
        )
        raise
    except ValueError as e:
        AnalyticsService.record_event(
            event_name="upload_failed",
            user_id=user_id if 'user_id' in locals() else None,
            metadata={"error": str(e), "filename": file.filename}
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        AnalyticsService.record_event(
            event_name="upload_failed",
            user_id=user_id if 'user_id' in locals() else None,
            metadata={"error": str(e), "filename": file.filename}
        )
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
