from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, Index

from .base import Base


class OddsSnapshot(Base):
    __tablename__ = "odds_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(128), nullable=False, index=True)
    source = Column(String(32), nullable=False, default="500", index=True)
    fixture_id = Column(String(64), nullable=True, index=True)
    captured_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    kickoff_time = Column(DateTime, nullable=False, index=True)
    odds_draw = Column(Float, nullable=False)
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_odds_snapshots_match_capture", "match_id", "captured_at"),
        Index("idx_odds_snapshots_fixture_capture", "fixture_id", "captured_at"),
        {"extend_existing": True},
    )
