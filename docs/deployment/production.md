# Production Deployment

Production-ready deployment with security hardening.

## Security Checklist

- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY (32+ characters)
- [ ] Enable HTTPS with valid certificates
- [ ] Restrict CORS origins
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure backups
- [ ] Use non-root users in containers

---

## Environment Configuration

### Production `.env`

```env
# Database - USE STRONG PASSWORD
POSTGRES_PASSWORD=SuperStr0ng!P@ssw0rd#2024

# Security - CHANGE THIS
SECRET_KEY=your-production-secret-key-at-least-32-characters-long

# JWT
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com

# Optional: Google OAuth
GOOGLE_CLIENT_ID=your-production-client-id
GOOGLE_CLIENT_SECRET=your-production-client-secret
```

---

## HTTPS with Nginx

### Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    upstream web {
        server web:3000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com api.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # Web frontend
    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;

        location / {
            proxy_pass http://web;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }
    }

    # API backend
    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;

        location / {
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket
        location /api/v1/ws {
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

### SSL Certificates

Use Let's Encrypt with Certbot:

```bash
# Install certbot
apt install certbot

# Get certificates
certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com

# Copy to project
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./certs/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./certs/
```

---

## Database Security

### Strong Passwords

Generate a secure password:

```bash
openssl rand -base64 32
```

### Connection Limits

In `postgresql.conf`:

```conf
max_connections = 100
```

### Backup Schedule

Create `backup.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U postgres trading_simulator | gzip > backup_$DATE.sql.gz

# Keep only last 7 days
find . -name "backup_*.sql.gz" -mtime +7 -delete
```

Add to crontab:

```bash
0 2 * * * /path/to/backup.sh
```

---

## Monitoring

### Health Checks

Add to monitoring system:

```bash
# API health
curl -f https://api.yourdomain.com/ || alert

# Web health
curl -f https://yourdomain.com/ || alert

# Database
docker exec trading-db pg_isready -U postgres || alert
```

### Prometheus Metrics

Add to API for metrics collection:

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Log Aggregation

Configure centralized logging:

```yaml
# docker-compose.prod.yml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## Performance Tuning

### Uvicorn Workers

```yaml
api:
  command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Rule of thumb: `workers = (2 × CPU cores) + 1`

### Redis Configuration

```yaml
redis:
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### PostgreSQL Tuning

```conf
shared_buffers = 256MB
effective_cache_size = 768MB
work_mem = 4MB
```

---

## Deployment Checklist

1. [ ] Update all environment variables
2. [ ] Generate SSL certificates
3. [ ] Configure Nginx
4. [ ] Set up database backups
5. [ ] Configure monitoring
6. [ ] Test health checks
7. [ ] Load test the application
8. [ ] Document runbooks
