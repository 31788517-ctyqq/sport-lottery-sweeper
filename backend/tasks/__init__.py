"""
Task module initialization.
"""

import importlib
import logging

from celery import Celery, Task

from ..core.config import settings

logger = logging.getLogger(__name__)


# Create default Celery application.
celery_app = Celery(
    "sport_lottery_worker",
    broker=settings.REDIS_URL or "redis://localhost:6379/0",
    backend=settings.REDIS_URL or "redis://localhost:6379/0",
    include=[
        "backend.tasks.500wang_scheduler",
        "backend.tasks.agent_tasks",
        "backend.tasks.alert_monitoring_tasks",
        "backend.tasks.analytics_tasks",
        "backend.tasks.crawler_tasks",
        "backend.tasks.crawler_tasks_v2",
        "backend.tasks.draw_prediction_tasks",
        "backend.tasks.intelligence_tasks",
        "backend.tasks.match_tasks",
        "backend.tasks.notification_tasks",
    ],
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


class DatabaseTask(Task):
    """Task base class with DB session lifecycle."""

    def __call__(self, *args, **kwargs):
        from backend.database import SessionLocal

        db = SessionLocal()
        try:
            return self.run(db, *args, **kwargs)
        finally:
            db.close()


def _safe_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception as exc:
        logger.warning("[tasks] skip module import %s: %s", module_name, exc)
        return None


match_tasks = _safe_import("backend.tasks.match_tasks")
intelligence_tasks = _safe_import("backend.tasks.intelligence_tasks")
crawler_tasks = _safe_import("backend.tasks.crawler_tasks")
analytics_tasks = _safe_import("backend.tasks.analytics_tasks")
notification_tasks = _safe_import("backend.tasks.notification_tasks")
alert_monitoring_tasks = _safe_import("backend.tasks.alert_monitoring_tasks")


__all__ = [
    "match_tasks",
    "intelligence_tasks",
    "crawler_tasks",
    "analytics_tasks",
    "notification_tasks",
    "alert_monitoring_tasks",
    "DatabaseTask",
    "celery_app",
]
