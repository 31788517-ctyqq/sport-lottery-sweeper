from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, UniqueConstraint

from .base import Base


class AsyncTask(Base):
    __tablename__ = "async_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(128), nullable=False, index=True)
    task_type = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="PENDING", index=True)
    payload = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(String(1000), nullable=True)
    progress = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    __table_args__ = (
        UniqueConstraint("task_id", name="uq_async_tasks_task_id"),
        {"extend_existing": True},
    )
