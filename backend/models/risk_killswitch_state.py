from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String

from .base import Base


class RiskKillSwitchState(Base):
    __tablename__ = "risk_killswitch_states"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(16), nullable=False, default="RUN", index=True)
    reason_json = Column(JSON, nullable=True)
    manual_override = Column(Integer, nullable=False, default=0)
    operator = Column(String(64), nullable=True)
    operator_note = Column(String(500), nullable=True)
    triggered_at = Column(DateTime, nullable=True)
    released_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
