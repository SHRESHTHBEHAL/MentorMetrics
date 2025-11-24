# System Architecture

## High-Level Diagram

```mermaid
graph TD
    User[User] -->|Uploads Video| Frontend[React Frontend]
    Frontend -->|POST /upload| API[FastAPI Backend]
    API -->|Store Video| Storage[Supabase Storage]
    API -->|Create Session| DB[(Supabase DB)]
    
    subgraph "Week 2: Processing Pipeline"
        API -->|Trigger| Pipeline[Analysis Pipeline]
        Pipeline -->|Extract| Audio[Audio Analysis]
        Pipeline -->|Extract| Text[Text Analysis]
        Pipeline -->|Extract| Visual[Visual Analysis]
        Audio --> Fusion[Multimodal Fusion]
        Text --> Fusion
        Visual --> Fusion
        Fusion --> Scoring[Scoring Engine]
        Scoring -->|Update| DB
    end
```

## Data Flow

1. **Upload**: User uploads a video via the frontend.
2. **Storage**: Video is stored in Supabase Storage.
3. **Session Creation**: A session record is created in the database with status `uploaded`.
4. **Processing (Week 2)**: The backend triggers the analysis pipeline.
5. **Analysis (Week 2)**: Audio, text, and visual features are extracted and analyzed.
6. **Fusion & Scoring (Week 2)**: Multimodal data is fused to generate a teaching quality score.
7. **Reporting (Week 3)**: Results are stored and displayed on the dashboard.

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS
- **Backend**: FastAPI, Python
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage
- **ML/AI**: PyTorch, Transformers (Week 2)
