"""
Kaggle dataset registry model.
"""

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from .base import Base


class KaggleDatasetRegistry(Base):
    __tablename__ = "kaggle_dataset_registry"

    id = Column(Integer, primary_key=True, index=True)
    dataset_slug = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    owner_name = Column(String(128), nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    sync_interval_hours = Column(Integer, nullable=False, default=6)
    latest_version = Column(String(64), nullable=True)
    last_synced_version = Column(String(64), nullable=True)
    license_name = Column(String(128), nullable=True)
    import_mode = Column(String(32), nullable=False, default="incremental")
    mapping_strategy = Column(String(32), nullable=False, default="alias_first")
    config = Column(JSON, nullable=True)
    last_sync_at = Column(DateTime, nullable=True)
    last_error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("dataset_slug", name="uq_kaggle_dataset_registry_slug"),
        Index("idx_kaggle_dataset_registry_enabled", "enabled"),
    )

