"""
Kaggle file manifest model.
"""

from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, JSON, String, UniqueConstraint
from sqlalchemy.sql import func

from .base import Base


class KaggleFileManifest(Base):
    __tablename__ = "kaggle_file_manifest"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), nullable=False)
    dataset_slug = Column(String(255), nullable=False)
    version = Column(String(64), nullable=True)
    file_path = Column(String(1024), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=True)
    file_sha256 = Column(String(64), nullable=True)
    row_count = Column(Integer, nullable=True)
    schema_hash = Column(String(64), nullable=True)
    manifest_meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("run_id", "file_path", name="uq_kaggle_file_manifest_run_file"),
        Index("idx_kaggle_file_manifest_slug_version", "dataset_slug", "version"),
    )

