from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON
from datetime import datetime
from .base import Base

class DrawPredictionResult(Base):
    __tablename__ = "draw_prediction_results"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(128), nullable=False, comment="比赛唯一标识")
    predicted_draw_prob = Column(Float, nullable=False, comment="预测平局概率")
    actual_result = Column(String(16), nullable=True, comment="实际比赛结果")
    prediction_meta = Column(JSON, comment="预测时的额外信息")
    predicted_at = Column(DateTime, default=datetime.utcnow)
    match_time = Column(DateTime, nullable=False, comment="比赛开始时间")
