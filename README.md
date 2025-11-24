# MentorMetrics

MentorMetrics is an AI-powered system that evaluates teaching quality from recorded videos using multimodal analysis: audio, text, and visuals.

## Project Structure

- `/src/backend`: FastAPI backend application
- `/src/frontend`: React + Vite frontend application
- `/docs`: Project documentation
- `/models`: ML models (placeholder)

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- Supabase account

### Backend Setup

1. Navigate to the backend directory (root):
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   Copy `.env.example` to `.env` and fill in your Supabase credentials.

3. Run the backend:
   ```bash
   uvicorn src.backend.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   # Install dependencies (from root)
   npm install
   ```

2. Run the frontend:
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:5173`.

## API Overview

See [docs/api-overview.md](docs/api-overview.md) for detailed API documentation.

## Architecture

See [docs/architecture.md](docs/architecture.md) for system architecture details.
