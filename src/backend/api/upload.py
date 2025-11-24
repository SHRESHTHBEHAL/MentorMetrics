from fastapi import APIRouter, UploadFile, File, HTTPException, status
from src.backend.utils.supabase_client import supabase
from src.backend.utils.file_manager import FileManager
from src.backend.models.api_models import UploadResponse
from src.backend.utils.logger import setup_logger
import os

router = APIRouter()
logger = setup_logger(__name__)

@router.post("/", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    try:
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
            "file_url": public_url,
            "filename": filename,
            "status": "uploaded"
        }
        
        data, count = supabase.table("sessions").insert(session_data).execute()
        
        if not data or len(data[1]) == 0:
             raise HTTPException(status_code=500, detail="Failed to create session record")
             
        session = data[1][0]
        
        logger.info(f"Video uploaded successfully: {session['id']}")
        
        return UploadResponse(
            session_id=session['id'],
            file_url=public_url,
            message="Video uploaded successfully"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
