# Database Schema

The database is hosted on Supabase (PostgreSQL).

## Tables

### `users`
- `id`: UUID (PK, FK to auth.users)
- `email`: TEXT
- `full_name`: TEXT
- `created_at`: TIMESTAMP

### `sessions`
- `id`: UUID (PK)
- `user_id`: UUID (FK to users)
- `file_url`: TEXT
- `filename`: TEXT
- `status`: TEXT ('uploaded', 'processing', 'complete', 'failed')
- `has_transcript`: BOOLEAN
- `stages_completed`: JSONB (Array of completed stages)
- `last_successful_stage`: TEXT
- `completion_metadata`: JSONB (Stores summary scores for quick access)
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### `transcripts`
- `id`: UUID (PK)
- `session_id`: UUID (FK to sessions)
- `raw_text`: TEXT
- `segments`: JSONB (Array of timestamped segments)
- `word_timestamps`: JSONB
- `created_at`: TIMESTAMP

### `audio_features`
- `id`: UUID (PK)
- `session_id`: UUID (FK to sessions)
- `words_per_minute`: NUMERIC
- `silence_ratio`: NUMERIC
- `clarity_score`: NUMERIC
- `raw_features`: JSONB
- `created_at`: TIMESTAMP

### `visual_evaluations`
- `id`: UUID (PK)
- `session_id`: UUID (FK to sessions)
- `face_visibility_score`: NUMERIC
- `gaze_forward_score`: NUMERIC
- `gesture_score`: NUMERIC
- `visual_overall`: NUMERIC
- `raw_visual_data`: JSONB
- `created_at`: TIMESTAMP

### `text_evaluations`
- `id`: UUID (PK)
- `session_id`: UUID (FK to sessions)
- `clarity_score`: NUMERIC
- `structure_score`: NUMERIC
- `technical_correctness_score`: NUMERIC
- `raw_llm_response`: JSONB
- `created_at`: TIMESTAMP

### `final_scores`
- `id`: UUID (PK)
- `session_id`: UUID (FK to sessions)
- `mentor_score`: NUMERIC (0-10)
- `engagement`: NUMERIC
- `communication_clarity`: NUMERIC
- `technical_correctness`: NUMERIC
- `pacing_structure`: NUMERIC
- `raw_fusion_data`: JSONB
- `created_at`: TIMESTAMP

### `reports`
- `id`: UUID (PK)
- `session_id`: UUID (FK to sessions)
- `summary`: TEXT
- `strengths`: JSONB (Array)
- `improvements`: JSONB (Array)
- `actionable_tips`: JSONB (Array)
- `raw_llm_response`: JSONB
- `created_at`: TIMESTAMP
    
### `analytics_events`
- `id`: UUID (PK)
- `event_name`: TEXT
- `session_id`: UUID
- `user_id`: UUID
- `metadata`: JSONB
- `timestamp`: TIMESTAMP

## Security
Row Level Security (RLS) is enabled on all tables to ensure users can only access their own data.
