#!/bin/bash

# SEO Agent Platform - Google Cloud Run Deployment Script
# Usage: ./deploy-cloudrun.sh [setup|deploy|update]

set -e

# Configuration
PROJECT_ID="geminiapiproject-457306"
REGION="us-west1"
SERVICE_BACKEND="scrib-ai-writing-superpowers"
SERVICE_FRONTEND="scrib-ai-writing-superpowers-frontend"
REPOSITORY="gemini-fullstack-langgraph-quickstart"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 SEO Agent Platform - Cloud Run Deployment${NC}"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if gcloud is installed and authenticated
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI not found. Please install Google Cloud SDK.${NC}"
        exit 1
    fi
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null; then
        echo -e "${RED}❌ Not authenticated with gcloud. Run: gcloud auth login${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ gcloud CLI is ready${NC}"
}

# Setup initial configuration
setup() {
    echo -e "${YELLOW}🔧 Setting up Google Cloud resources...${NC}"
    
    # Set project
    gcloud config set project $PROJECT_ID
    
    # Enable required APIs
    echo "Enabling required APIs..."
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    gcloud services enable secretmanager.googleapis.com
    
    # Create secrets if they don't exist
    echo "Setting up secrets..."
    
    # Check and create GEMINI_API_KEY secret
    if ! gcloud secrets describe gemini-api-key --project=$PROJECT_ID &>/dev/null; then
        echo "Creating GEMINI_API_KEY secret..."
        echo -n "AIzaSyB1Ac8KV8aRdvZ2uEVaTRQZ59adfBp8k-M" | gcloud secrets create gemini-api-key --data-file=-
    fi
    
    # Check and create SECRET_KEY secret
    if ! gcloud secrets describe secret-key --project=$PROJECT_ID &>/dev/null; then
        echo "Creating SECRET_KEY secret..."
        echo -n "production-super-secure-secret-key-32-chars-minimum" | gcloud secrets create secret-key --data-file=-
    fi
    
    # Check and create DATABASE_URL secret (for Cloud SQL)
    if ! gcloud secrets describe database-url --project=$PROJECT_ID &>/dev/null; then
        echo "Creating DATABASE_URL secret (you may need to update this)..."
        echo -n "sqlite:///./app.db" | gcloud secrets create database-url --data-file=-
    fi
    
    echo -e "${GREEN}✅ Setup completed!${NC}"
}

# Build and deploy services
deploy() {
    echo -e "${YELLOW}🏗️ Building and deploying services...${NC}"
    
    # Submit build to Cloud Build
    echo "Starting Cloud Build..."
    gcloud builds submit --config cloudbuild.yaml \
        --substitutions=COMMIT_SHA=$(git rev-parse --short HEAD) \
        --project=$PROJECT_ID
    
    echo -e "${GREEN}✅ Deployment completed!${NC}"
    
    # Get service URLs
    echo -e "${BLUE}📋 Service URLs:${NC}"
    BACKEND_URL=$(gcloud run services describe $SERVICE_BACKEND --region=$REGION --format="value(status.url)" --project=$PROJECT_ID)
    FRONTEND_URL=$(gcloud run services describe $SERVICE_FRONTEND --region=$REGION --format="value(status.url)" --project=$PROJECT_ID)
    
    echo "Backend:  $BACKEND_URL"
    echo "Frontend: $FRONTEND_URL"
    echo "API Docs: $BACKEND_URL/docs"
}

# Quick update deployment (build only changed services)
update() {
    echo -e "${YELLOW}🔄 Updating services...${NC}"
    
    # Build backend
    echo "Building backend..."
    gcloud builds submit ./backend \
        --tag gcr.io/$PROJECT_ID/scrib-ai-writing-superpowers:$(git rev-parse --short HEAD) \
        --project=$PROJECT_ID
    
    # Deploy backend
    echo "Deploying backend..."
    gcloud run deploy $SERVICE_BACKEND \
        --image gcr.io/$PROJECT_ID/scrib-ai-writing-superpowers:$(git rev-parse --short HEAD) \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --port 8080 \
        --memory 2Gi \
        --cpu 2 \
        --min-instances 0 \
        --max-instances 10 \
        --set-env-vars "ENVIRONMENT=production,DEBUG=false,BACKEND_CORS_ORIGINS=https://scrib-ai-writing-superpowers-frontend-263183603168.us-west1.run.app" \
        --set-secrets "GEMINI_API_KEY=gemini-api-key:latest,SECRET_KEY=secret-key:latest,DATABASE_URL=database-url:latest" \
        --project=$PROJECT_ID
    
    # Build frontend
    echo "Building frontend..."
    cd frontend
    gcloud builds submit . \
        --tag gcr.io/$PROJECT_ID/scrib-ai-writing-superpowers-frontend:$(git rev-parse --short HEAD) \
        --file Dockerfile.cloudrun \
        --project=$PROJECT_ID
    cd ..
    
    # Deploy frontend
    echo "Deploying frontend..."
    BACKEND_URL=$(gcloud run services describe $SERVICE_BACKEND --region=$REGION --format="value(status.url)" --project=$PROJECT_ID)
    
    gcloud run deploy $SERVICE_FRONTEND \
        --image gcr.io/$PROJECT_ID/scrib-ai-writing-superpowers-frontend:$(git rev-parse --short HEAD) \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --port 8080 \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 5 \
        --set-env-vars "BACKEND_URL=$BACKEND_URL" \
        --project=$PROJECT_ID
    
    echo -e "${GREEN}✅ Update completed!${NC}"
}

# Health check
health_check() {
    echo -e "${YELLOW}🔍 Performing health checks...${NC}"
    
    BACKEND_URL=$(gcloud run services describe $SERVICE_BACKEND --region=$REGION --format="value(status.url)" --project=$PROJECT_ID 2>/dev/null)
    FRONTEND_URL=$(gcloud run services describe $SERVICE_FRONTEND --region=$REGION --format="value(status.url)" --project=$PROJECT_ID 2>/dev/null)
    
    if [ -n "$BACKEND_URL" ]; then
        echo "Checking backend health..."
        if curl -f "$BACKEND_URL/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend is healthy: $BACKEND_URL${NC}"
        else
            echo -e "${RED}❌ Backend health check failed${NC}"
        fi
    fi
    
    if [ -n "$FRONTEND_URL" ]; then
        echo "Checking frontend health..."
        if curl -f "$FRONTEND_URL/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Frontend is healthy: $FRONTEND_URL${NC}"
        else
            echo -e "${RED}❌ Frontend health check failed${NC}"
        fi
    fi
}

# Main script logic
case "$1" in
    "setup")
        check_gcloud
        setup
        ;;
    "deploy")
        check_gcloud
        deploy
        health_check
        ;;
    "update")
        check_gcloud
        update
        health_check
        ;;
    "health")
        health_check
        ;;
    *)
        echo "Usage: $0 {setup|deploy|update|health}"
        echo ""
        echo "Commands:"
        echo "  setup   - Initial setup of Google Cloud resources"
        echo "  deploy  - Full deployment using Cloud Build"
        echo "  update  - Quick update deployment"
        echo "  health  - Check service health"
        echo ""
        echo "Example workflow:"
        echo "  1. ./deploy-cloudrun.sh setup"
        echo "  2. ./deploy-cloudrun.sh deploy"
        echo "  3. ./deploy-cloudrun.sh health"
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 Operation completed successfully!${NC}"