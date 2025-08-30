# Deployment Guide

## Quick Start

### Option 1: One-Click Windows Setup
```cmd
run.bat
```

### Option 2: Python Direct
```cmd
python run.py
```

### Option 3: Docker
```cmd
docker-compose up --build -d
```

## Production Deployment

### Prerequisites
- Python 3.8+
- FFmpeg
- 2 vCPUs, 4GB RAM minimum
- 10GB storage

### Environment Setup
1. Copy `.env.example` to `.env`
2. Update configuration values
3. Set secure JWT secret and admin password

### Database Migration
```bash
python -c "from backend.server import init_db; init_db()"
```

### SSL/HTTPS Setup
Configure reverse proxy (nginx/Apache) for HTTPS in production.

### Monitoring
- Health: `/health`
- Metrics: `/metrics`
- Logs: `bucket/logs/`

## Scaling Considerations
- Use PostgreSQL for production database
- Configure S3 for file storage
- Add load balancer for multiple instances
- Monitor FFmpeg concurrency limits