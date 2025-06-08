# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Scriv is a comprehensive SEO content creation platform with a **complete 7-step automated workflow**: Research → Planning → Writing → Editing → Publishing → Analysis → Improvement. Built with LangGraph for workflow orchestration and multi-AI integration (Gemini 2.0 Flash Exp primary, OpenAI/Anthropic fallback).

**Main Implementation**: `gemini-fullstack-langgraph-quickstart/` - Production-ready AI-powered SEO platform

**Live URLs**:
- Frontend: https://scrib-ai-frontend-263183603168.us-west1.run.app
- Backend: https://scrib-ai-backend-new-263183603168.us-west1.run.app/docs

## Development Commands

### Quick Start
```bash
cd gemini-fullstack-langgraph-quickstart

# Full development environment
make dev                  # Both servers (backend port 8123, frontend port 5174)

# Individual services
make dev-backend          # LangGraph API server
make dev-frontend         # React frontend
langgraph dev             # Alternative LangGraph development

# Database
cd backend && alembic upgrade head        # Apply migrations
cd backend && alembic revision --autogenerate -m "description"  # Create migration
```

### Testing & Quality
```bash
# Backend
cd backend && make test                    # Unit tests with pytest
cd backend && make test_watch             # Watch mode testing
cd backend && make extended_tests         # Integration tests with AI services
cd backend && make format                 # Format with ruff
cd backend && make lint                   # Lint with ruff and mypy

# Frontend  
cd frontend && npm run test               # Vitest unit tests
cd frontend && npm run test:ui            # Visual test runner
cd frontend && npm run coverage           # Test coverage reports
cd frontend && npm run lint               # ESLint
```

## Architecture

### 7-Step SEO Workflow System
```
React 19 + shadcn/ui ↔ LangGraph FastAPI (port 8123) ↔ Gemini 2.0 Flash Exp
        ↓                          ↓                              ↓
  Workflow UI            7-Step Orchestrator              Multi-AI Fallback
        ↓                          ↓                              ↓
   Progress Tracking ↔ PostgreSQL + Redis + Background Tasks ↔ OpenAI/Anthropic
```

**Production-Ready Features:**
- ✅ **Complete 7-Step Workflow**: リサーチ→企画→執筆→修正→出稿→分析→改善
- ✅ **LangGraph Orchestration**: Full workflow engine with state management
- ✅ **Multi-AI Integration**: Gemini primary + OpenAI/Anthropic fallback
- ✅ **Real-time Progress**: Background tasks with session tracking
- ✅ **Notion-style Editing**: 12 AI editing commands with range selection
- ✅ **Deep Research**: AI-powered content generation with fact-checking
- ✅ **4-Pattern Planning**: Beginner/Expert/How-to/Comparison strategies

## 7-Step SEO Workflow API

### Main Workflow Orchestrator
```bash
# Complete 7-step workflow
POST /api/v1/seo-workflow/start              # Start automated workflow
GET  /api/v1/seo-workflow/status/{id}        # Real-time progress
GET  /api/v1/seo-workflow/results/{id}       # Final results
POST /api/v1/seo-workflow/demo/birth-flowers # Demo workflow

# Individual workflow steps
POST /api/v1/planning/generate-patterns      # Step 2: Planning (4 patterns)
POST /api/v1/writing/generate-content        # Step 3: Content generation
POST /api/v1/editing/suggest                 # Step 4: Notion-style editing
```

### Core API Endpoints
```bash
# Authentication
POST /api/v1/auth/login           # JWT authentication
POST /api/v1/auth/register        # User registration

# Keyword Research (Step 1)
POST /api/v1/keywords/analyze          # Single keyword analysis
POST /api/v1/keywords/analyze/bulk     # Bulk analysis
POST /api/v1/keywords/competitors      # Competitor analysis

# Content & Analytics (Steps 5-7)
POST /api/v1/content/articles         # Create article
GET  /api/v1/analytics/articles/{id}  # Article analytics

# API Key Management
GET    /api/v1/api-keys           # Multi-AI provider management
POST   /api/v1/api-keys           # Add new AI service
```

## Development Environment

### Development URLs
```bash
# Local Development
Frontend:  http://localhost:5174    # Vite React
Backend:   http://localhost:8123    # LangGraph API
Database:  localhost:5433           # PostgreSQL
Redis:     localhost:6379           # Redis
API Docs:  http://localhost:8123/docs
```

### Required Environment Variables
```bash
# Essential for AI features
GEMINI_API_KEY="your_gemini_key"              # Required for AI features
LANGSMITH_API_KEY="your_langsmith_key"        # Optional monitoring
OPENAI_API_KEY="your_openai_key"              # Optional fallback
ANTHROPIC_API_KEY="your_anthropic_key"        # Optional fallback

# Database
POSTGRES_URI="postgres://postgres:postgres@localhost:5433/postgres"
REDIS_URI="redis://localhost:6379"

# Authentication
SECRET_KEY="your_jwt_secret"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Technology Stack

### Core Technologies
- **Frontend**: React 19, TypeScript, Vite, TailwindCSS 4, shadcn/ui
- **Backend**: Python 3.11+, FastAPI, LangGraph 0.2.6+, SQLAlchemy
- **AI Integration**: Google Gemini 2.0 Flash Exp (primary), OpenAI, Anthropic
- **Database**: PostgreSQL 16, Redis 6
- **Testing**: Pytest, Vitest
- **Package Management**: Backend uses `uv`, Frontend uses `npm`
- **Code Quality**: Ruff, MyPy, ESLint

## Implementation Status

### ✅ Completed Implementation (90%)
- **Backend API**: Complete 7-step workflow with all endpoints
- **Database Models**: Full schema with analytics and versioning
- **AI Integration**: Gemini 2.0 Flash Exp + multi-provider fallback
- **Authentication**: OAuth2 JWT with skip login for demos

### 🚚 Remaining Work (10%)
- **Frontend Integration**: Connect workflow UI to backend APIs
- **Real-time Streaming**: LangGraph SDK integration for live updates
- **Database Persistence**: Migrate from in-memory to PostgreSQL sessions

## Development Best Practices

### 7-Step Workflow Implementation
- **Graph Configuration**: `backend/langgraph.json` + `seo_workflow_graph.py`
- **API Modules**: Dedicated endpoints for each step (planning.py, writing.py, editing.py)
- **Session Management**: Real-time progress tracking with in-memory state
- **AI Integration**: Gemini 2.0 Flash Exp with structured prompts per step
- **Development Port**: LangGraph API on port 8123, Frontend on port 5174

### Key Development Points
- Always use `langgraph dev` or `make dev-backend` for development (not uvicorn directly)
- Backend uses `uv` for Python package management (`uv run pytest`, `uv run alembic`)
- Frontend uses LangGraph SDK (`@langchain/langgraph-sdk`) for real-time monitoring
- Database migrations via Alembic are required for schema changes
- Environment variables are crucial - GEMINI_API_KEY is required for AI features

### Project Structure
```
gemini-fullstack-langgraph-quickstart/
├── backend/src/
│   ├── agent/              # LangGraph workflows (seo_workflow_graph.py)
│   ├── api/v1/             # REST API endpoints
│   │   ├── seo_workflow.py # Main 7-step orchestrator
│   │   ├── planning.py     # Step 2: Planning API
│   │   ├── writing.py      # Step 3: Writing API
│   │   └── editing.py      # Step 4: Editing API
│   ├── models/             # Database models
│   └── services/ai/        # Multi-AI provider integration
└── frontend/src/
    ├── components/         # React components
    │   ├── SEOWorkflowDashboard.tsx  # 7-step workflow UI
    │   └── ui/             # shadcn/ui components
    └── lib/api.ts          # API client
```

### Package Management & Execution
- **Backend**: All Python commands use `uv run` (e.g., `uv run pytest`, `uv run alembic`)
- **Frontend**: Standard npm commands (e.g., `npm run dev`, `npm run build`)
- **Dependencies**: Backend deps in `pyproject.toml`, frontend deps in `package.json`
- **Development**: Use Makefiles for common tasks

## Docker Development Environment

### Docker Compose Services
```bash
# Start database services
docker-compose up -d langgraph-postgres langgraph-redis

# Service access
# PostgreSQL: localhost:5433 (user: postgres, password: postgres, db: postgres)
# Redis: localhost:6379
# LangGraph API: localhost:8123
```

## Deployment & Production

### Google Cloud Run Configuration
- **Project**: `geminiapiproject-457306` (Project Number: 263183603168)
- **Region**: `us-west1`
- **Production URLs**:
  - Frontend: https://scrib-ai-frontend-263183603168.us-west1.run.app
  - Backend: https://scrib-ai-backend-new-263183603168.us-west1.run.app

### API Keys & Authentication

#### AI Service API Keys
- **Google Gemini API**: `[CONFIGURED_IN_CLOUD_SECRETS]`
- **Custom Search API**: `[CONFIGURED_IN_CLOUD_SECRETS]`
- **Search Engine ID**: `[CONFIGURED_IN_CLOUD_SECRETS]`

#### Google OAuth2 Authentication (Production)
- **OAuth Client Name**: SEO Agent Platform OAuth
- **Client ID**: `[CONFIGURED_IN_CLOUD_SECRETS]`
- **Client Secret**: `[CONFIGURED_IN_CLOUD_SECRETS]`
- **Authorized Redirect URIs**:
  - `https://scrib-ai-backend-new-263183603168.us-west1.run.app/api/v1/auth/google/callback`
  - `http://localhost:8123/api/v1/auth/google/callback` (development)
- **Authorized JavaScript Origins**:
  - `https://scrib-ai-frontend-263183603168.us-west1.run.app`
  - `http://localhost:5174` (development)

### Deployment Script
```bash
cd gemini-fullstack-langgraph-quickstart
chmod +x deploy-cloudrun.sh
./deploy-cloudrun.sh setup    # Initial setup (enable APIs, create secrets)
./deploy-cloudrun.sh deploy   # Full deployment using Cloud Build
./deploy-cloudrun.sh update   # Quick update deployment
./deploy-cloudrun.sh health   # Health check
```

## Key Features

### 7-Step SEO Workflow Details
1. **Research (リサーチ)**: Keyword analysis, competitor research, user intent analysis
2. **Planning (企画)**: 4-pattern strategy generation (beginner/expert/how-to/comparison)
3. **Writing (執筆)**: Deep Research integration, SEO-optimized content generation
4. **Editing (修正)**: Notion-style command palette with 12 editing commands
5. **Publishing (出稿)**: Optimal timing analysis, CMS integration strategy
6. **Analysis (分析)**: Performance prediction, KPI setting, A/B test design
7. **Improvement (改善)**: Process optimization, learning loop design

### Demo Workflow
```bash
# Test the complete 7-step workflow with birth flowers example
curl -X POST http://localhost:8123/api/v1/seo-workflow/demo/birth-flowers
```

### Advanced Analytics Engine
- Causal inference methods (Difference-in-Differences, CausalImpact, RDD)
- Performance prediction modeling with statistical significance
- Content clustering and pattern analysis
- A/B testing framework with automated insights

### Multi-AI Integration
- **Primary**: Google Gemini 2.0 Flash Exp for optimal performance
- **Fallback**: OpenAI GPT-4 and Anthropic Claude for reliability
- **Features**: Encrypted API key storage, usage tracking, rate limiting
- **Management**: Real-time provider switching and quota monitoring