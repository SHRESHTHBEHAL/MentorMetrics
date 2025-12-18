# MentorMetrics

MentorMetrics is an advanced multimodal AI coaching platform designed to evaluate teaching quality from recorded videos. By analyzing audio, text, and visual cues, it provides actionable feedback to help mentors improve their teaching effectiveness.

## Key Features

- **Multimodal Analysis**:
    - **Audio**: Analyzes speech clarity, words per minute (WPM), and silence ratio.
    - **Visual**: Tracks eye contact, hand gestures, and overall engagement using computer vision.
    - **Text**: Evaluates transcript content for technical correctness, communication clarity, and pacing.
- **Interactive Dashboard**:
    - Real-time analytics and performance trends.
    - Score distribution and historical tracking.
    - Quick access to recent sessions and upload functionality.
- **Live Analysis**:
    - **Real-time Feedback**: Instant analysis of eye contact, gestures, and body movement using webcam feed.
    - **Live Scoring**: Dynamic updates to performance metrics during practice sessions.
- **Detailed Reports**:
    - Comprehensive scoring (0-10) across multiple dimensions.
    - Executive summary, strengths, and areas for improvement.
    - **Actionable Tips**: specific, AI-generated advice for growth.
- **Transcript Viewer**:
    - Full searchable transcript with timestamped segments.
    - Download capability for offline review.
- **Brutalist UI**: A distinct, high-contrast design system for clarity and impact.

## Project Structure

- `/src/backend`: FastAPI backend application (Python)
    - `/api`: REST API endpoints (`upload`, `process`, `results`, `live`, `admin`, `debug`)
    - `/pipelines`: Core AI processing logic (Audio, Visual, Text, Fusion)
    - `/services`: Business logic and database interactions
- `/src/frontend`: React + Vite frontend application
    - `/components`: Reusable UI components
    - `/pages`: Application views (Dashboard, Results, Upload, etc.)
- `/docs`: Project documentation
- `/uploads`: Temporary storage for uploaded videos (not committed)

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Supabase account (Database & Storage)
- FFmpeg (for audio processing)

### Backend Setup

1. Navigate to the root directory:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   Copy `.env.example` to `.env` and fill in your credentials (Supabase, OpenAI/Gemini API keys).

3. Run the backend:
   ```bash
   uvicorn src.backend.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### Frontend Setup

1. Navigate to the root directory (or ensure `package.json` is accessible):
   ```bash
   npm install
   ```

2. Run the frontend:
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:5173`.

## Architecture

See [docs/architecture.md](docs/architecture.md) for detailed system architecture, data flow, and component diagrams.

## API Documentation

See [docs/api-overview.md](docs/api-overview.md) for detailed API endpoint descriptions.
