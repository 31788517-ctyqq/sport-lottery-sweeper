from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, UniqueConstraint

from .base import Base


class ExternalSourceMapping(Base):
    __tablename__ = "external_source_mappings"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(32), nullable=False, index=True)
    external_id = Column(String(128), nullable=False, index=True)
    internal_match_id = Column(String(128), nullable=False, index=True)
    confidence_score = Column(Float, nullable=True)
    mapping_meta = Column(JSON, nullable=True)
    verified = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_external_source_mappings_source_external"),
        {"extend_existing": True},
    )
