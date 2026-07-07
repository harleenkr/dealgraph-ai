# DealGraph AI - Deployment Guide

This document outlines how to run, build, and deploy the DealGraph AI backend to Google Cloud Run.

## 1. Local Development
To run the server locally for testing:
```bash
uvicorn main:app --reload --port 8080
```

## 2. Docker Build
To build the Docker container locally:
```bash
# Run this from the root of the project (dealgraph-ai-backend)
docker build -t dealgraph-backend -f deployment/Dockerfile .
```

To run the container locally:
```bash
docker run -p 8080:8080 --env-file .env dealgraph-backend
```

## 3. Environment Variable Setup
Ensure you have a `.env` file in the root of your project for local testing:
```bash
GEMINI_API_KEY=your_api_key_here
```

> [!WARNING]
> **Production Security**: Do not hardcode your `GEMINI_API_KEY` in the source code or Dockerfile.

## 4. Google Cloud Run Deployment

First, authenticate with Google Cloud:
```bash
gcloud auth login
gcloud config set project [YOUR_PROJECT_ID]
```

### Option A: Source Deployment (Quickest)
You can deploy directly from source without pushing a container first:
```bash
gcloud run deploy dealgraph-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

### Option B: Container Deployment
If you pushed your built Docker image to Google Artifact Registry:
```bash
gcloud run deploy dealgraph-backend \
  --image us-central1-docker.pkg.dev/[PROJECT_ID]/[REPO]/dealgraph-backend:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

## 5. Secret Manager for API Keys
> [!IMPORTANT]
> When deploying to Cloud Run, **you must use Google Cloud Secret Manager** to store the `GEMINI_API_KEY`.

Do not pass the key via `--set-env-vars` in production. Instead, grant your Cloud Run service account access to the secret, and mount it as an environment variable during deployment:

```bash
gcloud run deploy dealgraph-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-secrets="GEMINI_API_KEY=my-gemini-secret:latest"
```
