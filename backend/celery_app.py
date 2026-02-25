"""
Celery application and draw-prediction training task entry.
"""

from __future__ import annotations

import logging
from typing import Dict, Any

from celery import Celery

from backend.database import SessionLocal
from backend.services.draw_prediction_service import (
    append_training_log,
    update_training_job_status,
)
from backend.services.draw_training_pipeline import train_job_with_real_data

logger = logging.getLogger(__name__)


celery_app = Celery(
    "sport_lottery_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["backend.tasks.draw_prediction_tasks"],
)

celery_app.conf.result_expires = 86400
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.task_reject_on_worker_lost = True
celery_app.conf.task_time_limit = 3600


def _execute_training_job(job_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        append_training_log(job_id, "训练任务开始执行。")
        update_training_job_status(db, job_id, "running")
        append_training_log(job_id, "状态更新为 running。")

        result = train_job_with_real_data(
            db,
            job_id,
            log_callback=lambda message: append_training_log(job_id, message),
        )

        metrics = result.get("metrics") if isinstance(result, dict) else None
        model_path = result.get("model_path") if isinstance(result, dict) else None
        update_training_job_status(db, job_id, "success", metrics=metrics, model_path=model_path)
        append_training_log(job_id, "训练完成，状态更新为 success。")
        return {"status": "success", "metrics": metrics, "model_path": model_path}
    except Exception as exc:
        try:
            db.rollback()
        except Exception:
            pass
        append_training_log(job_id, f"训练失败: {exc}")
        try:
            update_training_job_status(db, job_id, "failed")
        except Exception as status_exc:
            logger.exception("更新训练任务失败状态时出错: %s", status_exc)
        raise
    finally:
        db.close()


@celery_app.task(bind=True, name="train_model_task")
def train_model_task(self, job_id: int):
    try:
        return _execute_training_job(job_id)
    except Exception as exc:
        retries = getattr(self.request, "retries", 0)
        if retries < 2:
            raise self.retry(exc=exc, countdown=60, max_retries=2)
        raise


def run_training_job_local(job_id: int) -> Dict[str, Any]:
    """
    Fallback entry used when queue dispatch is unavailable.
    Runs the same real training pipeline as Celery worker.
    """
    return _execute_training_job(job_id)


if __name__ == "__main__":
    celery_app.start()
