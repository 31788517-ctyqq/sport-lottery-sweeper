from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime


class Prediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, index=True)
    predicted_outcome = Column(String(50))
    confidence_score = Column(Float)
    algorithm_version = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Remove this property if it doesn't exist in the actual database relationship
    user_predictions = relationship("UserPrediction", back_populates="prediction")


class UserPrediction(Base):
    __tablename__ = 'user_predictions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    prediction_id = Column(Integer, ForeignKey('predictions.id'))
    selected_outcome = Column(String(50))
    stake_amount = Column(Float)
    potential_payout = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Define the relationship correctly
    # prediction = relationship("Prediction", back_populates="user_predictions")