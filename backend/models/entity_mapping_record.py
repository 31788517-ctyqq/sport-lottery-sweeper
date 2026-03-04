"""
DB-backed entity mapping records and sync run logs.
"""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)

from .base import Base


class EntityMappingRecord(Base):
    __tablename__ = "entity_mapping_records"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(16), nullable=False, index=True)  # team | league
    entity_ref_id = Column(String(64), nullable=False, index=True)  # Team.id / League.id
    canonical_key = Column(String(128), nullable=False, index=True)
    display_name = Column(String(255), nullable=True)

    zh_names = Column(JSON, nullable=False, default=list)
    en_names = Column(JSON, nullable=False, default=list)
    jp_names = Column(JSON, nullable=False, default=list)
    source_aliases = Column(JSON, nullable=False, default=dict)
    official_info = Column(JSON, nullable=False, default=dict)

    confidence_score = Column(Float, nullable=False, default=1.0)
    auto_generated = Column(Boolean, nullable=False, default=True, index=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        index=True,
    )

    __table_args__ = (
        UniqueConstraint("entity_type", "entity_ref_id", name="uq_entity_mapping_records_type_ref"),
        Index("idx_entity_mapping_records_type_display", "entity_type", "display_name"),
    )


class EntityMappingSyncRun(Base):
    __tablename__ = "entity_mapping_sync_runs"

    id = Column(Integer, primary_key=True, index=True)
    trigger_type = Column(String(32), nullable=False, default="scheduler", index=True)
    status = Column(String(20), nullable=False, default="running", index=True)

    scanned_teams = Column(Integer, nullable=False, default=0)
    scanned_leagues = Column(Integer, nullable=False, default=0)
    upserted_teams = Column(Integer, nullable=False, default=0)
    upserted_leagues = Column(Integer, nullable=False, default=0)
    failed_count = Column(Integer, nullable=False, default=0)

    error_message = Column(Text, nullable=True)
    summary = Column(JSON, nullable=False, default=dict)

    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    finished_at = Column(DateTime(timezone=True), nullable=True, index=True)

