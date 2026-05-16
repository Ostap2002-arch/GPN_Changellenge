# Deployment Guide

## Quick Start with Docker Compose

### 1. Prerequisites
- Docker Desktop installed
- Docker Compose installed
- 4GB RAM available
- Ports 8000, 6379 available

### 2. Setup

```bash
# Clone or navigate to project directory
cd GPN

# Copy environment file
cp .env.example .env

# Build and start services
docker-compose up -d

# Check services
docker-compose ps
```

Expected output:
```
NAME            SERVICE           STATUS
gpn-redis       redis             Up (healthy)
gpn-api         api               Up
gpn-celery-worker  celery_worker  Up
gpn-celery-beat   celery_beat     Up (optional)
```

### 3. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# List devices (should return empty array)
curl http://localhost:8000/devices
```

### 4. Stop Services

```bash
# Stop all services (keep data)
docker-compose down

# Stop and remove data
docker-compose down -v
```

## Production Deployment

### 1. Using AWS EC2

#### Prerequisites:
- EC2 instance (t3.medium or larger)
- Ubuntu 22.04 LTS
- Security group with ports 8000, 5432 open

#### Steps:

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose -y
sudo usermod -aG docker ubuntu

# Clone repository
git clone your-repo-url
cd GPN

# Configure for production
nano .env
# Update DATABASE_URL to use PostgreSQL
# DATABASE_URL=postgresql://user:password@db-host/device_db

# Deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 2. Using Heroku

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:standard-0

# Set environment variables
heroku config:set DEBUG=false
heroku config:set CELERY_BROKER_URL=redis://...

# Deploy
git push heroku main
```

### 3. Using Kubernetes

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: device-data-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: device-data-api
  template:
    metadata:
      labels:
        app: device-data-api
    spec:
      containers:
      - name: api
        image: your-registry/device-data-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

Deploy:
```bash
kubectl apply -f k8s/
```

## Database Migrations

### Using Alembic

```bash
# Generate migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Monitoring and Logging

### Docker Logs

```bash
# API logs
docker-compose logs -f api

# Celery logs
docker-compose logs -f celery_worker

# Redis logs
docker-compose logs -f redis
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/devices  # Should work

# Redis connectivity
docker exec gpn-redis redis-cli ping  # Should output PONG
```

### Performance Monitoring

```bash
# CPU and Memory usage
docker stats

# Database size
du -sh device_data.db

# API metrics
docker-compose exec api curl http://localhost:8000/docs  # Swagger UI
```

## Backup and Recovery

### Backup Database

```bash
# SQLite
cp device_data.db device_data.db.backup

# PostgreSQL
pg_dump device_db > backup.sql
```

### Restore Database

```bash
# SQLite
cp device_data.db.backup device_data.db

# PostgreSQL
psql device_db < backup.sql
```

### Automated Backups (Cron)

```bash
# Add to crontab
0 2 * * * docker exec gpn-api sqlite3 /app/device_data.db ".backup '/backups/device_data_$(date +\%Y-\%m-\%d).db'"
```

## Performance Tuning

### 1. Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_device_readings_device_id 
ON device_readings(device_id);

CREATE INDEX idx_device_readings_timestamp 
ON device_readings(timestamp);

CREATE INDEX idx_device_readings_device_timestamp 
ON device_readings(device_id, timestamp);

-- Vacuum (SQLite only)
VACUUM;
PRAGMA optimize;
```

### 2. API Tuning

Update `app/config.py`:
```python
# Connection pooling
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40

# Query optimization
SQLALCHEMY_ECHO = False  # Disable query logging in production
```

### 3. Docker Optimization

Update `docker-compose.yml`:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Troubleshooting

### Issue: "Address already in use"
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
export API_PORT=8001
```

### Issue: "Connection refused" to Redis
```bash
# Check Redis health
docker-compose ps redis

# Restart Redis
docker-compose restart redis

# Check Redis logs
docker-compose logs redis
```

### Issue: "Database is locked" (SQLite)
```bash
# Restart API
docker-compose restart api

# Or migrate to PostgreSQL (recommended for production)
```

### Issue: High memory usage
```bash
# Check what's consuming memory
docker stats

# Reduce database connections
SQLALCHEMY_POOL_SIZE = 5

# Clear cache
docker exec gpn-redis redis-cli FLUSHALL
```

## Upgrade Procedure

```bash
# Pull latest changes
git pull origin main

# Rebuild images
docker-compose build --no-cache

# Stop current services
docker-compose down

# Start new version
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

## Security Checklist

- [ ] Change default credentials
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Enable database authentication
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Set up CORS properly
- [ ] Enable logging and monitoring
- [ ] Regular backups configured
- [ ] Security patches applied

## Support and Troubleshooting

For issues, check:
1. Docker logs: `docker-compose logs -f`
2. Health endpoint: `curl http://localhost:8000/health`
3. API documentation: `http://localhost:8000/docs`

