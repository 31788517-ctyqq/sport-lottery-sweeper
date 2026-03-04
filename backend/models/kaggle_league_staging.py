"""
Kaggle league staging model.
"""

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from .base import Base


class KaggleLeagueStaging(Base):
    __tablename__ = "kaggle_league_staging"

    id = Column(Integer, primary_key=True, index=True)
    dataset_slug = Column(String(255), nullable=False)
    version = Column(String(64), nullable=False)
    external_id = Column(String(255), nullable=False)
    league_name_raw = Column(String(255), nullable=True)
    country_raw = Column(String(128), nullable=True)
    normalized_hash = Column(String(64), nullable=True)
    payload_json = Column(JSON, nullable=False)
    is_valid = Column(Boolean, nullable=False, default=True)
    reject_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("dataset_slug", "version", "external_id", name="uq_kaggle_league_staging_identity"),
        Index("idx_kaggle_league_staging_hash", "normalized_hash"),
    )

