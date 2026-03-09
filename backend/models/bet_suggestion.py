from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, Text, Index

from .base import Base


class BetSuggestion(Base):
    __tablename__ = "bet_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(128), nullable=False, index=True)
    decision = Column(String(16), nullable=False, default="SKIP", index=True)
    stake_pct = Column(Float, nullable=False, default=0.0)
    edge = Column(Float, nullable=True)
    base_prob = Column(Float, nullable=True)
    implied_prob = Column(Float, nullable=True)
    odds_draw_place = Column(Float, nullable=True)
    odds_draw_close = Column(Float, nullable=True)
    clv = Column(Float, nullable=True)
    window_min_hours = Column(Integer, nullable=True)
    window_max_hours = Column(Integer, nullable=True)
    hours_to_kickoff = Column(Float, nullable=True)
    killswitch_state = Column(String(16), nullable=False, default="RUN", index=True)
    regime_label = Column(String(32), nullable=True)
    reason_codes = Column(JSON, nullable=True)
    reason_text = Column(Text, nullable=True)
    features = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_bet_suggestions_match_created", "match_id", "created_at"),
        {"extend_existing": True},
    )
