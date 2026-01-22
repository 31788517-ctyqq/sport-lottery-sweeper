from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Enum
from datetime import datetime
from sqlalchemy.orm import relationship
from .base import Base

class TrainingJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

class DrawTrainingJob(Base):
    __tablename__ = "draw_training_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String(128), nullable=False, comment="训练任务名称")
    feature_set_ids = Column(JSON, comment="使用的特征ID列表")
    algorithm = Column(String(64), nullable=False, comment="算法名称")
    hyperparameters = Column(JSON, comment="超参数字典")
    status = Column(String(20), default=TrainingJobStatus.PENDING)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    metrics = Column(JSON, comment="训练后评估指标")
    celery_task_id = Column(String(255), nullable=True, comment="Celery 任务ID，用于追踪异步任务")
    created_by = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
