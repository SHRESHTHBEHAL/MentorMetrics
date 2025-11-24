# Database Schema

## Tables

### `users`
- `id`: UUID (PK, FK to auth.users)
- `email`: Text
- `full_name`: Text
- `created_at`: Timestamp

### `sessions`
- `id`: UUID (PK)
- `user_id`: UUID (FK to users)
- `file_url`: Text
- `filename`: Text
- `status`: Text (uploaded, processing, completed, failed)
- `created_at`: Timestamp
- `updated_at`: Timestamp

### `evaluations`
- `id`: UUID (PK)
- `session_id`: UUID (FK to sessions)
- `type`: Text (audio, text, visual, fusion)
- `data`: JSONB
- `created_at`: Timestamp

### `scores`
- `id`: UUID (PK)
- `session_id`: UUID (FK to sessions)
- `category`: Text
- `score`: Float
- `confidence`: Float
- `created_at`: Timestamp

### `reports`
- `id`: UUID (PK)
- `session_id`: UUID (FK to sessions)
- `summary`: Text
- `recommendations`: JSONB
- `generated_at`: Timestamp
