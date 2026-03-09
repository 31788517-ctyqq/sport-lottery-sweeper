from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Float, Integer, String, UniqueConstraint

from .base import Base


class MarketRegimeDaily(Base):
    __tablename__ = "market_regime_daily"

    id = Column(Integer, primary_key=True, index=True)
    scope_type = Column(String(32), nullable=False, index=True)
    scope_key = Column(String(64), nullable=False, index=True)
    draw_rate_rolling = Column(Float, nullable=True)
    mu = Column(Float, nullable=True)
    sigma = Column(Float, nullable=True)
    zscore = Column(Float, nullable=True)
    regime_label = Column(String(32), nullable=True)
    biz_date = Column(Date, nullable=False, default=date.today, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("scope_type", "scope_key", "biz_date", name="uq_market_regime_daily_scope_date"),
        {"extend_existing": True},
    )
