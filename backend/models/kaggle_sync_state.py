"""
Kaggle sync state model.
"""

from sqlalchemy import Column, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from .base import Base


class KaggleSyncState(Base):
    __tablename__ = "kaggle_sync_state"

    id = Column(Integer, primary_key=True, index=True)
    dataset_slug = Column(String(255), nullable=False)
    sync_status = Column(String(20), nullable=False, default="idle")
    latest_detected_version = Column(String(64), nullable=True)
    last_success_version = Column(String(64), nullable=True)
    last_run_id = Column(Integer, nullable=True)
    last_started_at = Column(DateTime, nullable=True)
    last_finished_at = Column(DateTime, nullable=True)
    next_scheduled_at = Column(DateTime, nullable=True)
    consecutive_failures = Column(Integer, nullable=False, default=0)
    last_error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("dataset_slug", name="uq_kaggle_sync_state_slug"),
        Index("idx_kaggle_sync_state_status", "sync_status"),
    )

