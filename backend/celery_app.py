"""
Celery 应用配置
用于异步执行训练任务和定时任务
"""
from celery import Celery
from ..services.draw_prediction_service import (
    get_training_job_by_id, update_training_job_status,
    append_training_log, create_model_version_from_job
)
from ..database import SessionLocal
import time
import random

# 创建 Celery 应用
celery_app = Celery(
    'sport_lottery_worker',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['backend.tasks.draw_prediction_tasks']
)

# 配置任务结果过期时间（1天）
celery_app.conf.result_expires = 86400

# 配置任务重试
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.task_reject_on_worker_lost = True
celery_app.conf.task_time_limit = 3600  # 1小时超时


@celery_app.task(bind=True)
def train_model_task(self, job_id: int):
    """
    异步训练模型任务
    模拟训练过程：状态从 PENDING -> RUNNING -> SUCCESS
    """
    db = SessionLocal()
    try:
        append_training_log(job_id, "训练任务开始执行")

        # 1. 更新状态为 RUNNING
        update_training_job_status(db, job_id, "running")
        append_training_log(job_id, "状态更新为 RUNNING，开始加载数据")

        # 2. 模拟加载数据
        time.sleep(3)
        append_training_log(job_id, "数据加载完成，开始特征工程")

        # 3. 模拟特征工程
        time.sleep(5)
        append_training_log(job_id, "特征工程完成，开始模型训练")

        # 4. 模拟训练过程
        for epoch in range(1, 6):
            time.sleep(2)
            loss = 0.5 - (epoch * 0.08) + random.uniform(-0.02, 0.02)
            accuracy = 0.6 + (epoch * 0.06) + random.uniform(-0.02, 0.02)
            append_training_log(
                job_id,
                f"Epoch {epoch}/5 - Loss: {loss:.4f}, Accuracy: {accuracy:.4f}"
            )

        # 5. 生成模型路径
        model_path = f"/models/job_{job_id}/model.pkl"
        append_training_log(job_id, f"模型训练完成，保存至 {model_path}")

        # 6. 计算并保存性能指标
        metrics = {
            "accuracy": round(0.85 + random.uniform(-0.05, 0.05), 3),
            "f1_score": round(0.82 + random.uniform(-0.05, 0.05), 3),
            "precision": round(0.88 + random.uniform(-0.05, 0.05), 3),
            "recall": round(0.78 + random.uniform(-0.05, 0.05), 3)
        }

        # 7. 更新状态为 SUCCESS，自动创建模型版本
        update_training_job_status(db, job_id, "success", metrics, model_path)
        append_training_log(job_id, f"训练成功！性能指标: {metrics}")
        append_training_log(job_id, "已自动创建模型版本")

        return {"status": "success", "metrics": metrics}

    except Exception as e:
        append_training_log(job_id, f"训练失败: {str(e)}")
        update_training_job_status(db, job_id, "failed")
        self.retry(exc=e, countdown=60, max_retries=2)

    finally:
        db.close()


if __name__ == '__main__':
    celery_app.start()
