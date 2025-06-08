# SEO Agent Platform - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- Domain name (for production)

### 1. Clone & Setup
```bash
git clone <repository-url>
cd gemini-fullstack-langgraph-quickstart
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.production .env

# Edit configuration
nano .env
```

### 3. Deploy

#### Development Environment
```bash
./deploy.sh dev
```

#### Production Environment
```bash
./deploy.sh prod
```

## 🔧 Configuration

### Required Environment Variables

```bash
# AI Service API Keys (Required)
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here

# Security (Required)
SECRET_KEY=your_super_secure_secret_key_minimum_32_characters
POSTGRES_PASSWORD=your_secure_postgres_password
REDIS_PASSWORD=your_secure_redis_password
```

### Optional Configuration

```bash
# Additional AI Services
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LangGraph/LangSmith
LANGSMITH_API_KEY=your_langsmith_api_key_here

# Domain & SSL (Production only)
DOMAIN=yourdomain.com
SSL_EMAIL=admin@yourdomain.com

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
```

## 🏗️ Architecture

### Services Overview

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 80/443 | React + Nginx |
| Backend | 8000 | FastAPI + LangGraph |
| LangGraph API | 8123 | LangGraph API Server |
| PostgreSQL | 5432 | Primary Database |
| Redis | 6379 | Cache & Sessions |

### Development Ports

| Service | Port | Description |
|---------|------|-------------|
| SEO Backend | 8001 | Development API |
| LangGraph API | 8123 | Research API |
| Frontend | 5173 | Vite Dev Server |
| PostgreSQL | 5434 | Dev Database |
| Redis | 6380 | Dev Cache |

## 📊 Monitoring & Health Checks

### Health Endpoints
- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost/`
- API Docs: `http://localhost:8000/docs`

### Logs
```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs

# View specific service logs
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend

# Follow logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Service Status
```bash
# Check running containers
docker ps

# Check service health
curl http://localhost:8000/health
curl http://localhost/
```

## 🔄 Updates & Maintenance

### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and redeploy
./deploy.sh prod
```

### Database Migrations
```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create new migration
docker-compose -f docker-compose.prod.yml exec backend alembic revision --autogenerate -m "description"
```

### Backup Database
```bash
# Create backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U seo_agent_user -d seo_agent_db > backup.sql

# Restore backup
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U seo_agent_user -d seo_agent_db < backup.sql
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Service Not Starting
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs service-name

# Restart service
docker-compose -f docker-compose.prod.yml restart service-name
```

#### 2. Database Connection Issues
```bash
# Check database status
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Reset database
docker-compose -f docker-compose.prod.yml down
docker volume rm seo-agent_postgres_data
./deploy.sh prod
```

#### 3. API Key Issues
```bash
# Verify environment variables
docker-compose -f docker-compose.prod.yml exec backend env | grep API_KEY
```

### Performance Optimization

#### 1. Resource Limits
Edit `docker-compose.prod.yml` to add resource limits:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      memory: 2G
```

#### 2. Redis Configuration
```bash
# Monitor Redis usage
docker-compose -f docker-compose.prod.yml exec redis redis-cli info memory
```

## 🔒 Security

### SSL/TLS Setup (Production)
1. Obtain SSL certificates (Let's Encrypt recommended)
2. Place certificates in `./ssl/` directory
3. Update nginx configuration
4. Restart frontend service

### Firewall Configuration
```bash
# Allow only necessary ports
ufw allow 80
ufw allow 443
ufw allow 22
ufw enable
```

### Environment Security
- Use strong passwords (>16 characters)
- Rotate API keys regularly
- Enable database encryption
- Use secrets management for production

## 📈 Scaling

### Horizontal Scaling
- Use Docker Swarm or Kubernetes
- Add load balancer (nginx/HAProxy)
- Scale backend instances
- Use managed database services

### Vertical Scaling
- Increase container resources
- Optimize database queries
- Enable Redis clustering
- Use CDN for static assets

## 🆘 Support

### Logs Collection
```bash
# Collect all logs for debugging
mkdir debug-logs
docker-compose -f docker-compose.prod.yml logs > debug-logs/all-services.log
docker ps > debug-logs/containers.log
docker images > debug-logs/images.log
```

### Performance Metrics
```bash
# Container stats
docker stats

# Disk usage
docker system df

# Network usage
docker network ls
```

For additional support, check the troubleshooting section or create an issue in the repository.