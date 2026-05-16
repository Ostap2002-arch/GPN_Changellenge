# Device Data Service - Documentation Index

## 📖 Start Here

New to the project? Start with one of these documents:

1. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** ⭐ **START HERE**
   - Complete project overview
   - Feature checklist
   - Quick start guide
   - Technology stack

2. **[README.md](README.md)** 
   - Full feature description (Russian)
   - Installation instructions
   - API endpoint list
   - Usage examples
   - Environment setup

## 🚀 Getting Started

### For Local Development
→ See **[README.md - Установка и запуск](README.md#установка-и-запуск)**

Quick start on Windows:
```bash
setup.bat
poetry run python -m uvicorn device_data_service.main:app --reload
```

Quick start on Linux/Mac:
```bash
bash setup.sh
poetry run python -m uvicorn device_data_service.main:app --reload
```

### For Docker
→ See **[README.md - Запуск в Docker](README.md#вариант-2-запуск-в-docker)**

```bash
docker-compose up -d
```

### For Production
→ See **[DEPLOYMENT.md](DEPLOYMENT.md)**

Covers AWS, Heroku, Kubernetes deployment options

## 📚 Documentation by Topic

### API Usage
- **[API_EXAMPLES.md](API_EXAMPLES.md)** - 10 complete API examples with curl, Python, responses
- **[README.md - API Endpoints](README.md#api-endpoints)** - List of all 15 endpoints
- **[README.md - Примеры использования](README.md#примеры-использования)** - Basic examples

### Performance & Testing
- **[LOAD_TEST_REPORT.md](LOAD_TEST_REPORT.md)** - Load testing results and analysis
  - Performance metrics (45K+ requests tested)
  - Response time analysis
  - Bottleneck identification
  - Scaling recommendations
- **[README.md - Нагрузочное тестирование](README.md#нагрузочное-тестирование)** - How to run tests

### Deployment & Operations
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
  - Docker Compose setup
  - AWS EC2 deployment
  - Heroku deployment
  - Kubernetes deployment
  - Monitoring and logging
  - Backup strategies
  - Troubleshooting

### Code & Architecture
- **[README.md - Структура проекта](README.md#структура-проекта)** - Folder structure
- **[PROJECT_SUMMARY.md - Project Structure](PROJECT_SUMMARY.md#-project-structure)** - Detailed file breakdown

## 🔍 Quick Reference

### Common Tasks

**Want to...**
- ✅ **Add a device reading**
  → [API_EXAMPLES.md #2](API_EXAMPLES.md#2-add-device-reading)

- ✅ **Analyze device data**
  → [API_EXAMPLES.md #4](API_EXAMPLES.md#4-analyze-device-all-time)

- ✅ **Get user's devices analysis**
  → [API_EXAMPLES.md #9](API_EXAMPLES.md#9-analyze-user-devices)

- ✅ **Run load tests**
  → [LOAD_TEST_REPORT.md - Running](LOAD_TEST_REPORT.md#test-execution-parameters)

- ✅ **Deploy to production**
  → [DEPLOYMENT.md](DEPLOYMENT.md#production-deployment)

- ✅ **Monitor logs**
  → [DEPLOYMENT.md - Logs](DEPLOYMENT.md#docker-logs)

- ✅ **Backup database**
  → [DEPLOYMENT.md - Backups](DEPLOYMENT.md#backup-and-recovery)

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| Total Files | 23 |
| Lines of Code | 1,500+ |
| Lines of Documentation | 1,500+ |
| API Endpoints | 15 |
| Test Cases | 10+ |
| Dependencies | 18 |
| Load Test Volume | 45,230+ requests |

## 🎯 Learning Path

### Beginner Level (30 minutes)
1. Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Overview
2. Run `setup.bat` (Windows) or `bash setup.sh` (Linux)
3. Start server: `python -m uvicorn device_data_service.main:app --reload`
4. Open browser: http://localhost:8000/docs
5. Try example API calls in [API_EXAMPLES.md](API_EXAMPLES.md) #1-3

### Intermediate Level (1-2 hours)
1. Review API structure in [README.md](README.md#api-endpoints)
2. Study examples in [API_EXAMPLES.md](API_EXAMPLES.md) (all 10 examples)
3. Review code structure in [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md#-project-structure)
4. Run unit tests: `pytest tests/test_api.py -v`

### Advanced Level (2-4 hours)
1. Study performance report: [LOAD_TEST_REPORT.md](LOAD_TEST_REPORT.md)
2. Run load tests with Locust
3. Review deployment options in [DEPLOYMENT.md](DEPLOYMENT.md)
4. Deep dive into code: `device_data_service/services.py` and `device_data_service/main.py`
5. Study Celery async tasks in `device_data_service/celery_app.py`

## 🔢 API Endpoints Quick List

### Health
- `GET /health`

### Devices (CRUD)
- `POST /devices`
- `GET /devices`
- `GET /devices/{device_id}`
- `DELETE /devices/{device_id}`

### Readings
- `POST /devices/{device_id}/readings`
- `GET /devices/{device_id}/readings`

### Analysis (Device)
- `GET /analysis/device/{device_id}`
- `GET /analysis/device/{device_id}/last-24h`
- `GET /analysis/device/{device_id}/last-7d`

### Users
- `POST /users`
- `GET /users/{user_id}`

### Analysis (User)
- `GET /analysis/user/{user_id}/devices`
- `GET /analysis/user/{user_id}/devices/last-24h`

**For detailed requests/responses**: See [API_EXAMPLES.md](API_EXAMPLES.md)

## 🛠 Development Environment

### Setup Instructions
See appropriate section based on OS:
- Windows: [README.md - Установка и запуск (Вариант 1)](README.md#вариант-1-локальный-запуск)
- Linux/Mac: [README.md - Установка и запуск (Вариант 1 + setup.sh)](README.md)

### Running Services
- API: `python -m uvicorn device_data_service.main:app --reload`
- Celery Worker: `celery -A device_data_service.celery_app worker`
- Redis: `redis-server` (or via Docker)

### Testing
- Unit tests: `pytest tests/test_api.py -v`
- Load tests: `locust -f tests/load_test.py --host=http://localhost:8000`
- Coverage: `pytest tests/ --cov=device_data_service`

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f api

# Rebuild images
docker-compose build --no-cache

# Remove all data
docker-compose down -v
```

More commands: [DEPLOYMENT.md - Docker](DEPLOYMENT.md#quick-start-with-docker-compose)

## 📈 Performance & Optimization

**Current Performance (100 concurrent users):**
- 99.53% success rate ✅
- 45.7ms average response time ✅
- 187.2ms P95 response time ✅

**Recommendations:**
1. Add database indexes (HIGH)
2. Implement caching (MEDIUM)
3. Switch to PostgreSQL (MEDIUM)
4. See full analysis: [LOAD_TEST_REPORT.md](LOAD_TEST_REPORT.md)

## 🚀 Deployment Options

| Option | Complexity | Cost | Speed | Use Case |
|--------|-----------|------|-------|----------|
| Local | Easy | $0 | Instant | Development |
| Docker | Easy | $5-10/mo | 5 min | Testing |
| Heroku | Easy | $50-100/mo | 10 min | Small prod |
| AWS EC2 | Medium | $20-100/mo | 15 min | Medium prod |
| Kubernetes | Hard | $100+/mo | 30 min | Large prod |

→ See [DEPLOYMENT.md](DEPLOYMENT.md) for each option

## ⚠️ Troubleshooting

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| Port 8000 in use | [README.md - Решение проблем](README.md#решение-проблем) |
| Redis not connecting | [DEPLOYMENT.md - Troubleshooting](DEPLOYMENT.md#troubleshooting) |
| Database locked | [DEPLOYMENT.md - Troubleshooting](DEPLOYMENT.md#troubleshooting) |

## 📞 Support Resources

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Project Files**: See file listing below
- **Issues**: Check [DEPLOYMENT.md - Troubleshooting](DEPLOYMENT.md#troubleshooting)
- **Examples**: [API_EXAMPLES.md](API_EXAMPLES.md)

## 📁 Complete File Structure

```
GPN/
├── 📄 PROJECT_SUMMARY.md       ← Full project overview
├── 📄 README.md                ← Main documentation (Russian)
├── 📄 API_EXAMPLES.md          ← 10 complete API examples
├── 📄 DEPLOYMENT.md            ← Production deployment guide
├── 📄 LOAD_TEST_REPORT.md      ← Performance analysis
├── 📄 DOCUMENTATION_INDEX.md   ← This file
│
├── app/                         ← Main application
│   ├── main.py                 ← FastAPI endpoints
│   ├── config.py               ← Configuration
│   ├── database.py             ← Database setup
│   ├── models.py               ← ORM models
│   ├── schemas.py              ← Validation schemas
│   ├── services.py             ← Business logic
│   ├── celery_app.py           ← Async tasks
│   └── celery_tasks.py         ← Task definitions
│
├── tests/                       ← Testing suite
│   ├── test_api.py             ← Unit tests
│   └── load_test.py            ← Load tests
│
├── 🐳 Dockerfile               ← Docker image
├── 🐳 docker-compose.yml       ← Services config
├── 📋 pyproject.toml           ← Poetry dependencies
├── 📋 requirements.txt         ← Pip dependencies
├── ⚙️ .env.example             ← Environment template
├── 🔐 .gitignore               ← Git ignore
│
├── ⚡ setup.sh                 ← Linux/Mac setup
└── ⚡ setup.bat                ← Windows setup
```

---

**Last Updated**: May 15, 2024  
**Version**: 1.0.0  
**Status**: ✅ Complete & Production Ready

**Start reading**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
