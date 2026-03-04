"""
初始化用户相关表的脚本
"""
import sys
import os

# 正确获取项目根目录（scripts的父目录）
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Table, func
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.sqlite import JSON
import enum

class UserBase(DeclarativeBase):
    """
    用户模型专用的Base类
    """
    __allow_unmapped__ = True

# 定义用户-角色关联表
user_roles = Table(
    'user_roles',
    UserBase.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), default=func.now(), nullable=False)
)

# 定义角色-权限关联表
role_permissions = Table(
    'role_permissions',
    UserBase.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), default=func.now(), nullable=False)
)

# 用户状态枚举
class UserStatusEnum(enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"

# 用户类型枚举
class UserTypeEnum(enum.Enum):
    """用户类型枚举"""
    NORMAL = "normal"        # 普通用户
    PREMIUM = "premium"      # 高级用户
    ANALYST = "analyst"      # 分析师
    ADMIN = "admin"          # 管理员
    SUPER_ADMIN = "super_admin"  # 超级管理员

# 用户模型
class User(UserBase):
    """用户模型"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    status = Column(Enum(UserStatusEnum), default=UserStatusEnum.ACTIVE, nullable=False)
    user_type = Column(Enum(UserTypeEnum), default=UserTypeEnum.NORMAL, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    phone = Column(String(20))
    avatar_url = Column(String(255))
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    login_logs = relationship("UserLoginLog", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")

# 角色模型
class Role(UserBase):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

# 权限模型
class Permission(UserBase):
    """权限模型"""
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    resource = Column(String(100), nullable=False)  # 资源名称
    action = Column(String(50), nullable=False)     # 操作类型 (read, write, delete, etc.)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

# 用户登录日志模型
class UserLoginLog(UserBase):
    """用户登录日志模型"""
    __tablename__ = 'user_login_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    ip_address = Column(String(45))  # IPv6最大长度为45
    user_agent = Column(Text)
    login_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    success = Column(Boolean, default=True, nullable=False)
    failure_reason = Column(String(100))  # 登录失败原因
    
    # 关系
    user = relationship("User", back_populates="login_logs")

# 用户活动日志模型
class UserActivity(UserBase):
    """用户活动日志模型"""
    __tablename__ = 'user_activities'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    activity_type = Column(String(50), nullable=False)  # 活动类型
    description = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    occurred_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    metadata_json = Column(JSON, default=dict)  # 使用SQLite的JSON类型
    
    # 关系
    user = relationship("User", back_populates="activities")

# 用户订阅模型
class UserSubscription(UserBase):
    """用户订阅模型"""
    __tablename__ = 'user_subscriptions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    subscription_type = Column(String(50), nullable=False)  # 订阅类型
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    auto_renew = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    user = relationship("User", back_populates="subscriptions")

def init_user_tables():
    """初始化用户相关表"""
    try:
        # 创建数据库引擎
        db_path = os.path.join(project_root, 'backend', 'data/sport_lottery.db')
        engine = create_engine(f'sqlite:///{db_path}')
        
        # 创建所有用户相关的表
        UserBase.metadata.create_all(engine)
        
        print("用户相关表创建成功!")
        
        # 验证表是否创建成功
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        user_tables = ['users', 'roles', 'permissions', 'user_roles', 'role_permissions', 
                      'user_login_logs', 'user_activities', 'user_subscriptions']
        
        print("\n检查用户相关表:")
        for table in user_tables:
            if table in tables:
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table}")
                
    except Exception as e:
        print(f"创建表时出错: {e}")
        raise

if __name__ == "__main__":
    init_user_tables()