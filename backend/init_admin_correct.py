"""
正确版异步初始化管理员用户脚本
使用bcrypt进行密码哈希
"""
import asyncio
import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

from backend.config import settings
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """使用bcrypt进行密码哈希"""
    return pwd_context.hash(password)

# 简化版用户角色枚举
class UserRoleEnum(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# 简化版用户状态枚举  
class UserStatusEnum(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# 简化版Base
Base = declarative_base()


# 简化版User模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRoleEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), 
                  default=UserRoleEnum.USER, nullable=False, index=True)
    status = Column(Enum(UserStatusEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), 
                    default=UserStatusEnum.ACTIVE, nullable=False, index=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    nickname = Column(String(50), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)


async def init_admin_user():
    """初始化管理员用户"""
    # 创建异步引擎
    async_engine = create_async_engine(
        settings.ASYNC_DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False} if "sqlite" in settings.ASYNC_DATABASE_URL else {}
    )
    
    # 创建表（如果不存在）
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(async_engine) as db:
        # 检查是否已存在管理员用户
        result = await db.execute(
            select(User).where(User.role == UserRoleEnum.ADMIN)
        )
        admin_users = result.scalars().all()
        
        if admin_users:
            print("管理员用户已存在，跳过初始化")
            for user in admin_users:
                print(f"- 用户名: {user.username}, 邮箱: {user.email}")
            return
        
        # 创建默认管理员用户
        username = "admin"
        email = "admin@sports-lottery.local"
        password = "admin123"  # 默认密码，请在生产环境中更改
        
        # 对密码进行哈希
        hashed_password = get_password_hash(password)
        
        # 创建管理员用户
        admin_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=UserRoleEnum.ADMIN,
            status=UserStatusEnum.ACTIVE,
            first_name="System",
            last_name="Administrator",
            nickname="Admin",
            is_verified=True
        )
        
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        
        print(f"管理员用户创建成功!")
        print(f"用户名: {admin_user.username}")
        print(f"邮箱: {admin_user.email}")
        print(f"密码: {password} (请在登录后立即更改)")
        print("\n⚠️  安全警告: 请在生产环境中更改默认密码!")


if __name__ == "__main__":
    asyncio.run(init_admin_user())