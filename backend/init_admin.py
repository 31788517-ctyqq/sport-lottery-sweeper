"""
初始化管理员用户脚本
"""
import asyncio
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import engine
from .models import User, UserRoleEnum, UserStatusEnum
from .api.v1.auth import get_password_hash


async def init_admin_user():
    """初始化管理员用户"""
    async with AsyncSession(engine) as db:
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