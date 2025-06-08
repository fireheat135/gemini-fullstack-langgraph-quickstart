#!/bin/bash

# SEO Agent Deployment Script
# Usage: ./deploy.sh [dev|prod]

set -e  # Exit on any error

ENVIRONMENT=${1:-dev}
PROJECT_NAME="seo-agent"

echo "🚀 Starting deployment for environment: $ENVIRONMENT"

# Check if required files exist
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.production to .env and configure your settings."
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
required_vars=("GEMINI_API_KEY" "SECRET_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Development deployment
if [ "$ENVIRONMENT" = "dev" ]; then
    echo "🔧 Starting development environment..."
    
    # Build and start services
    docker-compose -f docker-compose.dev.yml down
    docker-compose -f docker-compose.dev.yml build
    docker-compose -f docker-compose.dev.yml up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    echo "🔍 Checking service health..."
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ SEO Agent Backend is healthy"
    else
        echo "❌ SEO Agent Backend health check failed"
    fi
    
    if curl -f http://localhost:8123/health > /dev/null 2>&1; then
        echo "✅ LangGraph API is healthy"
    else
        echo "❌ LangGraph API health check failed"
    fi
    
    echo "🌐 Development environment is ready:"
    echo "   - SEO Agent Backend: http://localhost:8001"
    echo "   - LangGraph API: http://localhost:8123"
    echo "   - Frontend: http://localhost:5173"
    echo "   - PostgreSQL: localhost:5434"
    echo "   - Redis: localhost:6380"

# Production deployment
elif [ "$ENVIRONMENT" = "prod" ]; then
    echo "🏭 Starting production deployment..."
    
    # Create necessary directories
    mkdir -p ssl uploads logs
    
    # Build and start services
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml build --no-cache
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 60
    
    # Run database migrations
    echo "🔄 Running database migrations..."
    docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
    
    # Check service health
    echo "🔍 Checking service health..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
    else
        echo "❌ Backend health check failed"
        docker-compose -f docker-compose.prod.yml logs backend
        exit 1
    fi
    
    if curl -f http://localhost/ > /dev/null 2>&1; then
        echo "✅ Frontend is healthy"
    else
        echo "❌ Frontend health check failed"
        docker-compose -f docker-compose.prod.yml logs frontend
        exit 1
    fi
    
    echo "🎉 Production deployment completed successfully!"
    echo "🌐 Application is available at: http://localhost"
    echo "📊 API Documentation: http://localhost/api/docs"
    
    # Show logs
    echo "📋 Recent logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=50

else
    echo "❌ Invalid environment. Use 'dev' or 'prod'"
    exit 1
fi

echo "✅ Deployment completed for $ENVIRONMENT environment"

# Show running containers
echo "🐳 Running containers:"
docker ps --filter "name=$PROJECT_NAME"