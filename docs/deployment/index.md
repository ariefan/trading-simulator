# Deployment Guide

Deploy the Trading Simulator to production.

## Deployment Options

<div class="grid cards" markdown>

-   :material-docker:{ .lg .middle } __Docker__

    ---

    Deploy with Docker Compose for easy container orchestration.

    [:octicons-arrow-right-24: Docker Deployment](docker.md)

-   :material-server:{ .lg .middle } __Production__

    ---

    Production-ready configuration with security hardening.

    [:octicons-arrow-right-24: Production Guide](production.md)

</div>

---

## Quick Docker Deployment

```bash
# Clone the repository
git clone https://github.com/ariefan/trading-simulator.git
cd trading-simulator

# Create environment file
cp .env.example .env
# Edit .env with your settings

# Build and start
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

---

## Services Overview

| Service | Port | Description |
|---------|------|-------------|
| Web | 3000 | Next.js frontend |
| API | 8000 | FastAPI backend |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache & queues |
| Celery | - | Background workers |
| Nginx | 80/443 | Reverse proxy (optional) |

---

## Environment Variables

### Required

```env
# Security
SECRET_KEY=your-super-secret-key-change-me

# Database
POSTGRES_PASSWORD=strong-password-here

# API URL (for frontend)
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Optional

```env
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# Redis
REDIS_URL=redis://redis:6379/0

# Logging
LOG_LEVEL=INFO
```

---

## Health Checks

All services include health checks:

```bash
# API health
curl http://localhost:8000/

# Web health
curl http://localhost:3000/

# Database
docker exec trading-db pg_isready -U postgres
```

---

## Monitoring

### Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f api
```

### Resource Usage

```bash
docker stats
```
