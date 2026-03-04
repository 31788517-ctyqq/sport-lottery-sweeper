"""
预测数据模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, 
    ForeignKey, Float, Text, Enum, CheckConstraint, Index, Date, Time, JSON
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy import event
from sqlalchemy.orm.mapper import Mapper
import enum

from sqlalchemy.ext.mutable import MutableDict
from .base import Base, BaseAuditModel, BaseFullModel


class PredictionMethodEnum(enum.Enum):
    """预测方法枚举"""
    AI_MACHINE_LEARNING = "ai_ml"           # AI机器学习
    STATISTICAL_MODEL = "statistical"       # 统计模型
    EXPERT_OPINION = "expert"               # 专家意见
    USER_CONSENSUS = "user_consensus"       # 用户共识
    COMBINED = "combined"                   # 综合预测
    FORMER_MATCHES = "former_matches"       # 基于过往比赛
    PLAYER_FORM = "player_form"             # 基于球员状态


class PredictionTypeEnum(enum.Enum):
    """预测类型枚举"""
    MATCH_OUTCOME = "match_outcome"         # 比赛结果
    SCORE_PREDICTION = "score_prediction"   # 比分预测
    GOALS_PREDICTION = "goals_prediction"   # 进球数预测
    CORNERS_PREDICTION = "corners_prediction" # 角球数预测
    CARDS_PREDICTION = "cards_prediction"   # 红黄牌预测
    PLAYER_PERFORMANCE = "player_performance" # 球员表现预测


class PredictionAccuracyEnum(enum.Enum):
    """预测准确度枚举"""
    VERY_HIGH = "very_high"                 # 非常高
    HIGH = "high"                           # 高
    MEDIUM = "medium"                       # 中等
    LOW = "low"                             # 低
    VERY_LOW = "very_low"                   # 非常低


class Prediction(BaseFullModel):
    """
    预测模型
    """
    __tablename__ = "predictions"
    
    # 关联信息
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 预测类型和方法
    prediction_type = Column(Enum(PredictionTypeEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), nullable=False, index=True)
    prediction_method = Column(Enum(PredictionMethodEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), nullable=False, index=True)
    
    # 预测结果
    predicted_outcome = Column(String(100), nullable=False, index=True)  # 预测结果文本描述
    confidence_level = Column(Float, nullable=False, index=True)  # 置信水平 (0-1)
    
    # 概率信息
    probability_home_win = Column(Float, nullable=True, index=True)  # 主胜概率
    probability_draw = Column(Float, nullable=True, index=True)      # 平局概率
    probability_away_win = Column(Float, nullable=True, index=True)  # 客胜概率
    
    # 特定预测结果
    predicted_score = Column(String(20), nullable=True)  # 预测比分 (如 "2-1")
    
    # 准确性
    accuracy = Column(Float, nullable=True, index=True)  # 实际准确性 (0-1)
    is_correct = Column(Boolean, nullable=True, index=True)  # 是否正确
    
    # 模型信息
    model_version = Column(String(50), nullable=True, index=True)  # 模型版本
    features_used = Column(MutableDict.as_mutable(Text), default=lambda: [], nullable=False)  # 使用的特征
    
    # 训练数据信息
    training_data_date = Column(Date, nullable=True, index=True)  # 训练数据日期
    
    # 算法详情
    algorithm_details = Column(Text, nullable=True)  # 算法详情
    
    # 外部数据
    external_id = Column(String(100), nullable=True, index=True)  # 外部系统ID
    external_source = Column(String(50), nullable=True, index=True)  # 外部数据来源
    
    # 预测来源
    predictor_type = Column(String(50), default='system', nullable=False, index=True)  # system, expert, user
    predictor_id = Column(Integer, nullable=True, index=True)  # 预测者ID (如果是专家或用户)
    
    # 评估指标
    precision = Column(Float, nullable=True)  # 精确率
    recall = Column(Float, nullable=True)     # 召回率
    f1_score = Column(Float, nullable=True)   # F1分数
    
    # 关系
    match = relationship("Match", back_populates="predictions")
    user_predictions = relationship("UserPrediction", back_populates="prediction")
    # 注意：user_predictions关系现在在user_models.py中的UserPrediction模型里定义
    
    # 索引
    __table_args__ = (
        Index('idx_predictions_match_method', 'match_id', 'prediction_method'),
        Index('idx_predictions_type_accuracy', 'prediction_type', 'accuracy'),
        Index('idx_predictions_confidence', 'confidence_level'),
        Index('idx_predictions_model_version', 'model_version'),
        Index('idx_predictions_predictor', 'predictor_type', 'predictor_id'),
        Index('idx_predictions_is_correct', 'is_correct'),
        Index('idx_predictions_external_id_source', 'external_id', 'external_source'),
        Index('idx_predictions_training_date', 'training_data_date'),
        {'extend_existing': True}
    )
    
    def __repr__(self) -> str:
        return f"<Prediction(id={self.id}, match_id={self.match_id}, type={self.prediction_type}, confidence={self.confidence_level})>"
# 注意：UserPrediction模型已移至user_models.py文件中，以解决循环导入问题