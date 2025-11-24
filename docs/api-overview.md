# API Overview

## Base URL

`http://localhost:8000/api`

## Endpoints

### Upload Video

- **URL**: `/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
    - `file`: Video file (binary)

**Response**:

```json
{
  "session_id": "uuid-string",
  "file_url": "https://supabase-url/storage/v1/object/public/videos/filename.mp4",
  "message": "Video uploaded successfully"
}
```

### Start Processing (Stub)

- **URL**: `/process/{session_id}`
- **Method**: `POST`

**Response**:

```json
{
  "session_id": "uuid-string",
  "status": "processing_started",
  "message": "Processing started successfully (Stub)"
}
```
