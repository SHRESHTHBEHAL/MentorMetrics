# Deployment Guide

This guide describes how to deploy MentorMetrics to production using **AWS App Runner** (Backend) and **Vercel** (Frontend).

## Prerequisites

- **GitHub Repository**: Ensure your code is pushed to GitHub.
- **AWS Account**: With access to App Runner and ECR.
- **AWS CLI**: Installed and configured (`aws configure`).
- **Docker**: Installed locally for building images.
- **Vercel Account**: For frontend hosting.
- **Supabase Project**: You need your Supabase URL and Anon Key.
- **Gemini API Key**: For AI analysis.

---

## 1. Backend Deployment (AWS App Runner via ECR)

Since App Runner's source code option doesn't support custom Dockerfiles directly, we'll push our Docker image to **Amazon ECR** (Elastic Container Registry) and connect App Runner to it.

### Step 1: Create an ECR Repository

```bash
# Create the repository (run once)
aws ecr create-repository --repository-name mentormetrics-backend --region ap-south-1
```

Note the `repositoryUri` from the output. It will look like:
```
123456789012.dkr.ecr.ap-south-1.amazonaws.com/mentormetrics-backend
```

### Step 2: Build and Push Docker Image

Run these commands from your project root (`/Users/shreshthbehal/MentorMetrics`):

```bash
# 1. Authenticate Docker with ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.ap-south-1.amazonaws.com

# 2. Build the Docker image
docker build -t mentormetrics-backend .

# 3. Tag the image for ECR
docker tag mentormetrics-backend:latest 123456789012.dkr.ecr.ap-south-1.amazonaws.com/mentormetrics-backend:latest

# 4. Push to ECR
docker push 123456789012.dkr.ecr.ap-south-1.amazonaws.com/mentormetrics-backend:latest
```

> **Replace** `123456789012` with your actual AWS account ID and `ap-south-1` with your preferred region.

### Step 3: Create App Runner Service

1.  Go to the [AWS App Runner Console](https://console.aws.amazon.com/apprunner/).
2.  Click **Create service**.
3.  **Source**:
    - Select **Container registry**.
    - Provider: **Amazon ECR**.
    - Browse and select your `mentormetrics-backend` repository.
    - Select the `latest` tag.
4.  **Deployment settings**:
    - Select **Automatic** for continuous deployment when new images are pushed.
    - App Runner will create an IAM role to access ECR (allow it).
5.  Click **Next**.

### Step 4: Configure Service Settings

1.  **Service name**: `mentormetrics-backend`
2.  **CPU**: `1 vCPU` (or `2 vCPU` for better performance)
3.  **Memory**: `2 GB` (or `4 GB` – Whisper can be memory-intensive)
4.  **Port**: `8000`
5.  **Environment Variables**: Add the following:

    | Variable Name       | Value                                      |
    |---------------------|--------------------------------------------|
    | `SUPABASE_URL`      | `https://your-project.supabase.co`         |
    | `SUPABASE_KEY`      | `your-supabase-anon-key`                   |
    | `GEMINI_API_KEY`    | `your-google-gemini-api-key`               |
    | `FRONTEND_URL`      | `https://your-frontend.vercel.app` (add after frontend deploy) |

6.  **Health check**:
    - **Path**: `/health`
    - **Protocol**: `HTTP`
7.  Click **Next**, review, and **Create & deploy**.

### Step 5: Wait for Deployment

App Runner will deploy your container. This takes **2-5 minutes**. Once complete, you'll get a **Default domain** like:
```
https://xxxxxxxx.ap-south-1.awsapprunner.com
```

### Step 6: Verify Backend

Visit your backend health endpoint:
```
https://xxxxxxxx.ap-south-1.awsapprunner.com/health
```
You should see:
```json
{"status": "healthy", "service": "MentorMetrics Backend"}
```

---

## 2. Updating the Backend

When you make code changes:

```bash
# 1. Rebuild the image
docker build -t mentormetrics-backend .

# 2. Tag and push
docker tag mentormetrics-backend:latest 123456789012.dkr.ecr.ap-south-1.amazonaws.com/mentormetrics-backend:latest
docker push 123456789012.dkr.ecr.ap-south-1.amazonaws.com/mentormetrics-backend:latest
```

App Runner will automatically detect the new image and redeploy (if automatic deployment is enabled).

---

## 3. Frontend Deployment (Vercel)

Vercel is the recommended platform for deploying React/Vite applications.

### Step 1: Connect Repository

1.  Go to [Vercel](https://vercel.com) and log in.
2.  Click **Add New Project**.
3.  **Import** your `MentorMetrics` GitHub repository.

### Step 2: Configure Build Settings

Vercel should auto-detect Vite. Verify/update these settings:

| Setting            | Value           |
|--------------------|-----------------|
| **Framework Preset** | `Vite`          |
| **Build Command**    | `npm run build` |
| **Output Directory** | `dist`          |
| **Install Command**  | `npm install`   |

### Step 3: Set Environment Variables

Add the following environment variables in the Vercel project settings:

| Variable Name            | Value                                                |
|--------------------------|------------------------------------------------------|
| `VITE_API_BASE_URL`      | `https://xxxxxxxx.ap-south-1.awsapprunner.com` (Your App Runner URL, **no trailing slash**) |
| `VITE_SUPABASE_URL`      | `https://your-project.supabase.co`                   |
| `VITE_SUPABASE_ANON_KEY` | `your-supabase-anon-key`                             |

### Step 4: Deploy

Click **Deploy**. Vercel will build and deploy your frontend. You'll get a URL like:
```
https://mentormetrics.vercel.app
```

---

## 4. Post-Deployment: Connect Frontend to Backend

### Step 1: Update Backend CORS

Go back to your **AWS App Runner** service:
1.  Navigate to **Configuration** → **Service settings**.
2.  Add/Update the `FRONTEND_URL` environment variable:
    ```
    FRONTEND_URL=https://mentormetrics.vercel.app
    ```
3.  Save changes (App Runner will redeploy automatically).

### Step 2: Update Supabase Auth

1.  Go to your [Supabase Dashboard](https://supabase.com/dashboard).
2.  Navigate to **Authentication** → **URL Configuration**.
3.  Add your **Frontend URL** to:
    - **Site URL**: `https://mentormetrics.vercel.app`
    - **Redirect URLs**: `https://mentormetrics.vercel.app/**`

---

## 5. Troubleshooting

### Backend Issues

| Problem                     | Solution                                                                 |
|-----------------------------|--------------------------------------------------------------------------|
| ECR push fails              | Run `aws ecr get-login-password` again to refresh credentials.          |
| App Runner shows "unhealthy"| Check logs. Common issues: missing env vars, port mismatch.             |
| CORS errors on frontend     | Verify `FRONTEND_URL` is set correctly in App Runner env vars.          |
| Whisper/Audio fails         | Increase memory to 4GB. Check `ffmpeg` is in the image.                  |

### Frontend Issues

| Problem                     | Solution                                                                 |
|-----------------------------|--------------------------------------------------------------------------|
| API calls fail              | Check `VITE_API_BASE_URL` is correct and has no trailing slash.         |
| Auth redirects fail         | Verify Supabase URL Configuration includes your Vercel domain.          |

### Viewing Logs

- **App Runner**: AWS Console → App Runner → Your Service → Logs.
- **Vercel**: Vercel Dashboard → Your Project → Deployments → Logs.

---

## Quick Reference

| Service     | URL Example                                      | Purpose         |
|-------------|--------------------------------------------------|-----------------|
| Backend     | `https://xxxxxxxx.ap-south-1.awsapprunner.com`   | API Server      |
| Frontend    | `https://mentormetrics.vercel.app`               | Web Application |
| Health Check| `https://xxxxxxxx.ap-south-1.awsapprunner.com/health` | Verify Backend  |
| ECR Repo    | `123456789012.dkr.ecr.ap-south-1.amazonaws.com/mentormetrics-backend` | Docker Images |
