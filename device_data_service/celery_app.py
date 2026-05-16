from celery import Celery
from device_data_service.config import settings

celery_app = Celery(
    "device_data_service",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    task_ignore_result=True,
    result_cache_max=100,
    result_backend_always_retry=False,
    worker_max_tasks_per_child=100,
    worker_max_memory_per_child=200000,
    worker_prefetch_multiplier=1,
    worker_disable_rate_limits=True,
    broker_pool_limit=10,
    redis_max_connections=20,
)


@celery_app.task(ignore_result=False, expires=600)
def analyze_device_task(device_id: str, start_time: str = None, end_time: str = None):
    """Async task for device analysis"""
    from device_data_service.database import SessionLocal
    from device_data_service.services import AnalysisService
    from datetime import datetime
    
    db = SessionLocal()
    try:
        start = datetime.fromisoformat(start_time) if start_time else None
        end = datetime.fromisoformat(end_time) if end_time else None
        result = AnalysisService.analyze_device(db, device_id, start, end)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task
def generate_report_task(user_id: int, start_time: str = None, end_time: str = None):
    """Async task for generating user report"""
    from device_data_service.database import SessionLocal
    from device_data_service.services import AnalysisService
    from datetime import datetime
    
    db = SessionLocal()
    try:
        start = datetime.fromisoformat(start_time) if start_time else None
        end = datetime.fromisoformat(end_time) if end_time else None
        result = AnalysisService.analyze_user_devices(db, user_id, start, end)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
