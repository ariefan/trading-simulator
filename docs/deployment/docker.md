# Docker Deployment

Deploy the Trading Simulator using Docker.

## Prerequisites

- Docker 24+
- Docker Compose 2.0+
- 2GB+ RAM
- 10GB+ disk space

---

## Quick Start

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Configuration

### Environment File

Create `.env` in the project root:

```env
# Database
POSTGRES_PASSWORD=your-secure-password

# Security
SECRET_KEY=your-super-secret-key-at-least-32-chars

# API URL for frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

### Docker Compose Override

Create `docker-compose.override.yml` for local customizations:

```yaml
version: "3.8"
services:
  api:
    environment:
      - LOG_LEVEL=DEBUG
    volumes:
      - ./apps/api/src:/app/src:ro  # Hot reload
```

---

## Services

### API Service

```yaml
api:
  build: ./apps/api
  ports:
    - "8000:8000"
  environment:
    - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/trading_simulator
    - SECRET_KEY=${SECRET_KEY}
  depends_on:
    - db
    - redis
```

### Web Service

```yaml
web:
  build:
    context: .
    dockerfile: ./apps/web/Dockerfile
    args:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
  ports:
    - "3000:3000"
```

### Database

```yaml
db:
  image: timescale/timescaledb:latest-pg15
  volumes:
    - postgres_data:/var/lib/postgresql/data
  environment:
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    - POSTGRES_DB=trading_simulator
```

---

## Build Options

### Build All Images

```bash
docker-compose -f docker-compose.prod.yml build
```

### Build Specific Service

```bash
docker-compose -f docker-compose.prod.yml build api
```

### No Cache Build

```bash
docker-compose -f docker-compose.prod.yml build --no-cache
```

---

## Database Management

### Run Migrations

```bash
docker-compose -f docker-compose.prod.yml exec api \
  alembic upgrade head
```

### Seed Database

```bash
docker-compose -f docker-compose.prod.yml exec api \
  python scripts/seed_database.py
```

### Backup Database

```bash
docker-compose -f docker-compose.prod.yml exec db \
  pg_dump -U postgres trading_simulator > backup.sql
```

### Restore Database

```bash
docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U postgres trading_simulator < backup.sql
```

---

## Scaling

### Scale Celery Workers

```bash
docker-compose -f docker-compose.prod.yml up -d --scale celery=3
```

### Scale API (with load balancer)

```bash
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

!!! note
    When scaling API, use Nginx or Traefik for load balancing.

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs api

# Check container status
docker-compose -f docker-compose.prod.yml ps

# Restart specific service
docker-compose -f docker-compose.prod.yml restart api
```

### Database Connection Failed

```bash
# Check database is running
docker-compose -f docker-compose.prod.yml ps db

# Check database logs
docker-compose -f docker-compose.prod.yml logs db

# Test connection
docker-compose -f docker-compose.prod.yml exec db \
  psql -U postgres -c "SELECT 1"
```

### Out of Memory

```bash
# Check resource usage
docker stats

# Increase limits in docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 1G
```
