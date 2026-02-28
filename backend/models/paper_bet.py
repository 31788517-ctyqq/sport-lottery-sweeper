from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Index

from .base import Base


class PaperBet(Base):
    __tablename__ = "paper_bets"

    id = Column(Integer, primary_key=True, index=True)
    suggestion_id = Column(Integer, ForeignKey("bet_suggestions.id", ondelete="CASCADE"), nullable=False, index=True)
    stake = Column(Float, nullable=False, default=1.0)
    fee_rate = Column(Float, nullable=False, default=0.08)
    rebate_rate = Column(Float, nullable=False, default=0.75)
    rebate_mode = Column(String(32), nullable=False, default="on_win_stake")
    actual_result = Column(String(16), nullable=True)
    is_win = Column(Integer, nullable=True)
    pnl = Column(Float, nullable=True)
    roi = Column(Float, nullable=True)
    status = Column(String(16), nullable=False, default="OPEN", index=True)
    settled_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_paper_bets_status_created", "status", "created_at"),
        {"extend_existing": True},
    )
