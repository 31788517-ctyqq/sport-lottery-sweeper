from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.sql import func
from ..database import Base


class BettingRecord(Base):
    """
    投注记录模型
    """
    __tablename__ = "betting_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    match_id = Column(Integer, index=True)
    bet_type = Column(String, default="unknown")  # 投注类型，如胜平负、大小球等
    amount = Column(Float, default=0.0)  # 投注金额
    odds = Column(Float)  # 投注时的赔率
    predicted_outcome = Column(String)  # 预测结果
    actual_outcome = Column(String)  # 实际结果
    is_winning = Column(Boolean, default=False)  # 是否中奖
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())