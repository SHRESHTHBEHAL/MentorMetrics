# API Overview

Base URL: `http://localhost:8000/api`

## Authentication
Most endpoints require authentication via Supabase.
- **Production**: Bearer Token in `Authorization` header.
- **Development**: `X-User-ID` header can be used to bypass auth.

## Endpoints

### 1. Upload & Processing

#### Upload Video
- **URL**: `/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Body**:
    - `file`: Video file (MP4, MOV, WEBM)
- **Response**:
    ```json
    {
      "session_id": "uuid",
      "user_id": "uuid",
      "filename": "video.mp4",
      "file_url": "https://..."
    }
    ```

#### Start Processing
- **URL**: `/process/{session_id}`
- **Method**: `POST`
- **Response**:
    ```json
    {
      "status": "processing_started",
      "task_id": "uuid"
    }
    ```

#### Check Status
- **URL**: `/status/{session_id}`
- **Method**: `GET`
- **Response**:
    ```json
    {
      "status": "processing",
      "progress": 45,
      "current_stage": "audio_analysis",
      "stages": [...]
    }
    ```

### 2. Results & Analytics

#### Get Session Results
- **URL**: `/results/{session_id}`
- **Method**: `GET`
- **Response**:
    ```json
    {
      "session_id": "uuid",
      "scores": { ... },
      "report": { ... },
      "transcript": { ... },
      "audio": { ... },
      "visual": { ... }
    }
    ```

#### Dashboard Analytics
- **URL**: `/analytics/dashboard`
- **Method**: `GET`
- **Response**:
    ```json
    {
      "summary": {
        "total_sessions": 10,
        "avg_mentor_score": 7.5,
        ...
      },
      "recent_sessions": [...],
      "score_distribution": {...},
      "score_history": [...]
    }
    ```

#### List Sessions
- **URL**: `/sessions/list`
- **Method**: `GET`
- **Response**:
    ```json
    [
      {
        "id": "uuid",
        "filename": "video.mp4",
        "status": "complete",
        "created_at": "timestamp",
        "mentor_score": 8.5
      },
      ...
    ]
    ```

### 3. Live Analysis

#### Analyze Live Frame
- **URL**: `/live/analyze`
- **Method**: `POST`
- **Body**:
    ```json
    {
      "image": "base64_encoded_frame_data"
    }
    ```
- **Response**:
    ```json
    {
      "eye_contact": true,
      "gestures": 1,
      "face_detected": true,
      "pose_score": 0.8
    }
    ```

### 4. Admin & Debug

#### Admin Logs
- **URL**: `/admin/logs`
- **Method**: `GET`
- **Query Params**: `event_type`, `session_id`, `user_id`, `limit`, `offset`
- **Response**: Log entries from `analytics_events`.

#### Debug Session Data
- **URL**: `/debug/{session_id}`
- **Method**: `GET`
- **Response**: Raw data dump of all session components (transcript, scores, report, etc.) for debugging.

### 5. Download & Utilities

#### Download PDF Report
- **URL**: `/download/report/{session_id}`
- **Method**: `GET`
- **Response**: PDF file download.

#### Download Raw Data
- **URL**: `/download/raw/{session_id}`
- **Method**: `GET`
- **Response**: JSON file download.

#### Restart Processing
- **URL**: `/restart/{session_id}`
- **Method**: `POST`

#### Record Frontend Event
- **URL**: `/analytics/frontend`
- **Method**: `POST`
- **Body**:
    ```json
    {
      "event_name": "page_view",
      "session_id": "uuid",
      "metadata": {}
    }
    ```
