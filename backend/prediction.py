# backend/prediction.py
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from .models import Base

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    home_win_prob = Column(Float)
    draw_prob = Column(Float)
    away_win_prob = Column(Float)
    score_home = Column(Integer)
    score_away = Column(Integer)
    total_goals = Column(Integer)
    match = relationship("Match", back_populates="prediction")
