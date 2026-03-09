from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class DrawModelVersion(Base):
    __tablename__ = "draw_model_versions"

    id = Column(Integer, primary_key=True, index=True)
    version_tag = Column(String(64), nullable=False, comment="版本标签")
    training_job_id = Column(Integer, ForeignKey("draw_training_jobs.id"), nullable=False)
    model_path = Column(String(256), nullable=False, comment="模型存储路径")
    performance_metrics = Column(JSON, comment="性能指标 JSON")
    deployed_at = Column(DateTime, nullable=True, comment="部署时间")
    status = Column(String(32), default="inactive", comment="模型状态 active/inactive")
    created_at = Column(DateTime, default=datetime.utcnow)

    training_job = relationship("DrawTrainingJob", backref="model_versions")
