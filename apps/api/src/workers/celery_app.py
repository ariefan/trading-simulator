from celery import Celery

from src.config import settings

# Create Celery app
celery_app = Celery(
    "trading_simulator",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max for backtests
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["src.workers"])
