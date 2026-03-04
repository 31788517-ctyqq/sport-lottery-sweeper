"""
Kaggle sync runs model.
"""

from sqlalchemy import Column, DateTime, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from .base import Base


class KaggleSyncRun(Base):
    __tablename__ = "kaggle_sync_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), nullable=False)
    dataset_slug = Column(String(255), nullable=False)
    task_type = Column(String(64), nullable=False, default="kaggle_sync")
    trigger_type = Column(String(20), nullable=False, default="scheduler")
    status = Column(String(20), nullable=False, default="pending")
    version = Column(String(64), nullable=True)
    rows_raw = Column(Integer, nullable=False, default=0)
    rows_curated = Column(Integer, nullable=False, default=0)
    rows_upserted = Column(Integer, nullable=False, default=0)
    duration_ms = Column(Integer, nullable=True)
    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    run_meta = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("run_id", name="uq_kaggle_sync_runs_run_id"),
        Index("idx_kaggle_sync_runs_slug_status_created", "dataset_slug", "status", "created_at"),
    )

