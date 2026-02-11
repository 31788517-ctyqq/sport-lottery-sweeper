"""
用户相关数据库模型模块
定义用户和用户预测相关的SQLAlchemy ORM模型，解决循环导入问题
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
from enum import Enum as PyEnum
from .base import Base, BaseAuditModel, BaseFullModel
import re


# 用户相关枚举定义
class UserRole(PyEnum):
    """用户角色枚举"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
    VIP = "vip"

class UserStatus(PyEnum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING = "pending"

class SocialProvider(PyEnum):
    """社交登录提供商枚举"""
    WECHAT = "wechat"
    QQ = "qq"
    WEIBO = "weibo"
    GITHUB = "github"
    GOOGLE = "google"
    FACEBOOK = "facebook"

class UserType(PyEnum):
    """用户类型枚举"""
    FREE = "free"
    PREMIUM = "premium"
    VIP = "vip"


# 预测相关枚举定义
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


class User(Base):
    """用户数据库模型"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    # 基础字段
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=True)
    avatar = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True, unique=True)
    bio = Column(Text, nullable=True)
    
    # 状态字段
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    
    # 登录统计字段
    last_login_time = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 compatible
    login_count = Column(Integer, default=0, nullable=False)
    
    # 时间戳字段
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), 
                       onupdate=func.now(), nullable=False)
    
    # 关系定义
    # AI_WORKING: coder1 @2026-01-29T06:05:00 - 明确指定外键关系，解决AmbiguousForeignKeysError
    roles = relationship("UserRoleMapping", foreign_keys="[UserRoleMapping.user_id]", back_populates="user", cascade="all, delete-orphan")
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    login_records = relationship("LoginRecord", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    email_verification_tokens = relationship("EmailVerificationToken", back_populates="user", cascade="all, delete-orphan")
    # 使用字符串引用解决循环导入问题
    user_predictions = relationship("UserPrediction", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    
    # AI_WORKING: coder1 @2026-01-26T01:16:00 - 修复User.__repr__缺少闭合括号的语法错误
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', status='{self.status}')>"
    # AI_DONE: coder1 @2026-01-26T01:16:00
    
    @property
    def is_active(self) -> bool:
        """检查用户是否处于活跃状态"""
        return self.status == UserStatus.ACTIVE
    
    @property
    def display_name(self) -> str:
        """获取用户显示名称"""
        return self.nickname or self.username
    
    @property
    def has_admin_role(self) -> bool:
        """检查用户是否具有管理员角色"""
        return any(role.role == UserRole.ADMIN for role in self.roles)
    
    @property
    def avatar_url(self) -> str:
        """获取用户头像URL"""
        if self.avatar:
            return self.avatar
        # 返回默认头像
        return f"https://ui-avatars.com/api/?name={self.username}&background=random"
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "phone": self.phone,
            "bio": self.bio,
            "status": self.status.value,
            "email_verified": self.email_verified,
            "phone_verified": self.phone_verified,
            "last_login_time": self.last_login_time.isoformat() if self.last_login_time else None,
            "last_login_ip": self.last_login_ip,
            "login_count": self.login_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "roles": [role.role.value for role in self.roles]
        }
    
    @staticmethod
    def validate_username(username):
        """验证用户名"""
        if not username or len(username.strip()) == 0:
            raise ValueError('用户名不能为空')
        
        username = username.strip()
        
        # 长度验证
        if len(username) < 3 or len(username) > 50:
            raise ValueError('用户名长度必须在3-50个字符之间')
        
        # 格式验证（字母、数字、下划线）
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError('用户名只能包含字母、数字和下划线')
        
        # 保留字检查
        reserved_words = ['admin', 'root', 'system', 'test', 'guest']
        if username.lower() in reserved_words:
            raise ValueError(f'用户名不能使用保留字: {username}')
        
        # 连续字符检查
        if re.search(r'(.)\1{2,}', username):
            raise ValueError('用户名不能包含连续3个以上相同字符')
        
        return username
    
    @staticmethod
    def validate_email(email):
        """验证邮箱"""
        if not email:
            raise ValueError('邮箱不能为空')
        
        # 基础邮箱格式验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError('邮箱格式不正确')
        
        return email.lower()
    
    @staticmethod
    def validate_phone(phone):
        """验证手机号"""
        if phone is not None:
            # 简单的中国手机号验证
            if not re.match(r'^1[3-9]\d{9}$', phone):
                raise ValueError('手机号格式不正确')
        return phone
    
    @staticmethod
    def validate_bio(bio):
        """验证个人简介"""
        if bio is not None and len(bio) > 500:
            raise ValueError('个人简介不能超过500个字符')
        return bio


class UserPrediction(BaseFullModel):
    """
    用户预测模型
    """
    __tablename__ = "user_predictions"
    
    # 关联信息
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    match_id = Column(Integer, ForeignKey('matches.id', ondelete='CASCADE'), nullable=False, index=True)
    prediction_id = Column(Integer, ForeignKey('predictions.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # 用户预测内容
    user_choice = Column(String(100), nullable=False)  # 用户的选择
    user_confidence = Column(Float, nullable=False, index=True)  # 用户信心指数 (0-1)
    
    # 结果
    is_successful = Column(Boolean, nullable=True, index=True)  # 是否成功
    profit_loss = Column(Float, default=0.0, nullable=False, index=True)  # 盈亏
    
    # 参与信息
    stake_amount = Column(Float, nullable=True)  # 投注金额
    odds_offered = Column(Float, nullable=True)  # 提供的赔率
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # 验证和评价
    user_evaluation = Column(Integer, nullable=True)  # 用户评价 (1-5星)
    notes = Column(Text, nullable=True)  # 用户备注
    
    # 关系 - 使用字符串引用解决循环导入问题
    user = relationship("User", back_populates="user_predictions")
    match = relationship("Match")
    prediction = relationship("Prediction", back_populates="user_predictions")

    # 索引
    __table_args__ = (
        Index('idx_user_predictions_user_match', 'user_id', 'match_id'),
        Index('idx_user_predictions_match_user', 'match_id', 'user_id'),
        Index('idx_user_predictions_pred_conf', 'prediction_id', 'user_confidence'),
        Index('idx_user_predictions_success', 'is_successful'),
        Index('idx_user_predictions_profit', 'profit_loss'),
        Index('idx_user_predictions_active', 'is_active'),
        Index('idx_user_predictions_evaluation', 'user_evaluation'),
        {'extend_existing': True}
    )
    
    def __repr__(self) -> str:
        return f"<UserPrediction(id={self.id}, user_id={self.user_id}, match_id={self.match_id})>"


class UserRoleMapping(Base):
    """用户角色映射模型"""
    __tablename__ = "user_role_mappings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    granted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # 关系定义
    user = relationship("User", foreign_keys=[user_id], back_populates="roles")
    granted_by_user = relationship("User", foreign_keys=[granted_by])
    
    def __repr__(self):
        return f"<UserRoleMapping(user_id={self.user_id}, role='{self.role}')>"
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role": self.role.value,
            "granted_at": self.granted_at.isoformat(),
            "granted_by": self.granted_by
        }


class SocialAccount(Base):
    """社交账号关联模型"""
    __tablename__ = "social_accounts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(Enum(SocialProvider), nullable=False)
    openid = Column(String(100), nullable=False)  # 社交平台用户唯一标识
    unionid = Column(String(100), nullable=True)   # 微信开放平台统一标识
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    profile_data = Column(Text, nullable=True)  # 社交平台返回的用户资料JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), 
                       onupdate=func.now(), nullable=False)
    
    # 关系定义
    user = relationship("User", foreign_keys=[user_id], back_populates="social_accounts")
    
    # 表级配置
    __table_args__ = (
        # 唯一约束：同一用户在同一平台只能绑定一个账号
        Index('uix_user_provider', 'user_id', 'provider', unique=True),
        {'sqlite_autoincrement': True, 'mysql_charset': 'utf8mb4', 'extend_existing': True}
    )

    
    def __repr__(self):
        return f"<SocialAccount(user_id={self.user_id}, provider='{self.provider}', openid='{self.openid}')>"
    
    @property
    def is_token_valid(self) -> bool:
        """检查访问令牌是否有效"""
        if not self.expires_at:
            return True  # 如果没有过期时间，认为一直有效
        return self.expires_at > func.now()
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "provider": self.provider.value,
            "openid": self.openid,
            "unionid": self.unionid,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class LoginRecord(Base):
    """登录记录模型"""
    __tablename__ = "login_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    login_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    login_ip = Column(String(45), nullable=False)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=True, nullable=False)
    failure_reason = Column(String(200), nullable=True)  # 登录失败原因
    location = Column(String(100), nullable=True)  # IP地理位置
    device_info = Column(Text, nullable=True)  # 设备信息JSON
    
    # 关系定义
    user = relationship("User", foreign_keys=[user_id], back_populates="login_records")
    
    # AI_WORKING: coder1 @2026-01-28 - 修复LoginRecord.__repr__缺少闭合括号的语法错误
    def __repr__(self):
        return f"<LoginRecord(user_id={self.user_id}, login_time={self.login_time}, success={self.success})>"
    # AI_DONE: coder1 @2026-01-28
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "login_time": self.login_time.isoformat(),
            "login_ip": self.login_ip,
            "user_agent": self.user_agent,
            "success": self.success,
            "failure_reason": self.failure_reason,
            "location": self.location,
            "device_info": self.device_info
        }


class PasswordResetToken(Base):
    """密码重置令牌模型"""
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系定义
    user = relationship("User", foreign_keys=[user_id], back_populates="password_reset_tokens")
    
    # AI_WORKING: coder1 @2026-01-25T21:36:00 - 修复PasswordResetToken.__repr__缺少闭合括号的语法错误
    def __repr__(self):
        return f"<PasswordResetToken(user_id={self.user_id}, used={self.used}, expires_at={self.expires_at})>"
    # AI_DONE: coder1 @2026-01-25T21:36:00
    
    @property
    def is_valid(self) -> bool:
        """检查令牌是否有效"""
        return not self.used and self.expires_at > func.now()
    
    @property
    def is_expired(self) -> bool:
        """检查令牌是否过期"""
        return self.expires_at <= func.now()
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token,
            "expires_at": self.expires_at.isoformat(),
            "used": self.used,
            "created_at": self.created_at.isoformat(),
            "used_at": self.used_at.isoformat() if self.used_at else None,
            "is_valid": self.is_valid
        }


class EmailVerificationToken(Base):
    """邮箱验证令牌模型"""
    __tablename__ = "email_verification_tokens"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(100), nullable=False)  # 验证的邮箱地址
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系定义
    user = relationship("User", foreign_keys=[user_id], back_populates="email_verification_tokens")
    
    # AI_WORKING: coder1 @2026-01-25T21:37:00 - 修复EmailVerificationToken.__repr__缺少闭合括号的语法错误
    def __repr__(self):
        return f"<EmailVerificationToken(user_id={self.user_id}, email='{self.email}', used={self.used})>"
    # AI_DONE: coder1 @2026-01-25T21:37:00
    
    @property
    def is_valid(self) -> bool:
        """检查令牌是否有效"""
        return not self.used and self.expires_at > func.now()
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email": self.email,
            "token": self.token,
            "expires_at": self.expires_at.isoformat(),
            "used": self.used,
            "created_at": self.created_at.isoformat(),
            "used_at": self.used_at.isoformat() if self.used_at else None,
            "is_valid": self.is_valid
        }


# 导出所有模型
__all__ = [
    # 枚举
    'UserRole', 'UserStatus', 'SocialProvider', 'UserType',
    'PredictionMethodEnum', 'PredictionTypeEnum', 'PredictionAccuracyEnum',
    # 主要模型
    'User', 'UserPrediction', 'UserRoleMapping', 'SocialAccount', 
    'LoginRecord', 'PasswordResetToken', 'EmailVerificationToken'
]