# Deployment Guide

This guide describes how to deploy MentorMetrics to production.

## Prerequisites

- **GitHub Repository**: Ensure your code is pushed to GitHub.
- **Supabase Project**: You need your Supabase URL and Anon Key.
- **OpenAI/Gemini Keys**: API keys for AI services.

## 1. Backend Deployment (Render/Railway)

We recommend using **Render** or **Railway** as they support Docker and Python easily.

### Option A: Render (Recommended)

1.  Create a new **Web Service** on [Render](https://render.com).
2.  Connect your GitHub repository.
3.  Select **Docker** as the Runtime.
4.  Render will automatically detect the `Dockerfile` in the root.
5.  **Environment Variables**: Add the following in the Render dashboard:
    - `SUPABASE_URL`: Your Supabase Project URL
    - `SUPABASE_KEY`: Your Supabase Anon Key
    - `OPENAI_API_KEY`: Your OpenAI Key (if used)
    - `GEMINI_API_KEY`: Your Google Gemini Key
    - `CORS_ORIGINS`: The URL of your deployed frontend (e.g., `https://your-frontend.vercel.app`). You can use `*` temporarily.
6.  Deploy!

### Option B: Railway

1.  New Project -> Deploy from GitHub repo.
2.  Railway will detect the Dockerfile.
3.  Add variables in the "Variables" tab.

## 2. Frontend Deployment (Vercel)

1.  Go to [Vercel](https://vercel.com) and "Add New Project".
2.  Import your GitHub repository.
3.  **Build Settings**:
    - Framework Preset: **Vite**
    - Build Command: `npm run build`
    - Output Directory: `dist`
4.  **Environment Variables**:
    - `VITE_API_BASE_URL`: The URL of your deployed backend (e.g., `https://mentormetrics-backend.onrender.com`). **Important**: Do not add a trailing slash.
    - `VITE_SUPABASE_URL`: Your Supabase URL.
    - `VITE_SUPABASE_ANON_KEY`: Your Supabase Anon Key.
5.  Deploy!

## 3. Post-Deployment Configuration

1.  **CORS**: Update the `CORS_ORIGINS` variable in your Backend service to match your final Frontend URL (e.g., `https://mentormetrics.vercel.app`).
2.  **Supabase Auth**: Go to your Supabase Dashboard -> Authentication -> URL Configuration. Add your Frontend URL to "Site URL" and "Redirect URLs".

## Troubleshooting

- **Health Check**: Visit `https://your-backend.onrender.com/health` to verify the backend is running.
- **Logs**: Check the deployment logs on Render/Vercel for any build or runtime errors.
