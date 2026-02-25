"""
Dedicated Celery app for intelligence collection task queueing.
"""

from celery import Celery

from backend.config import settings


celery_app = Celery(
    "intelligence_collection_worker",
    broker=settings.REDIS_URL or "redis://localhost:6379/0",
    backend=settings.REDIS_URL or "redis://localhost:6379/0",
    include=["backend.tasks.intelligence_collection_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=False,
    result_expires=86400,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    task_time_limit=3600,
)
