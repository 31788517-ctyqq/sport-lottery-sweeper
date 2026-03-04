"""
检查前台用户数量的脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.models.user import User
from backend.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select


async def check_user_count():
    """检查用户数量"""
    engine = create_async_engine(settings.ASYNC_DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db_session:
        # 查询总用户数
        result = await db_session.execute(select(User))
        users = result.scalars().all()
        print(f"当前数据库中的用户总数: {len(users)}")
        
        # 显示前几个用户的用户名
        for i, user in enumerate(users[:5]):
            print(f"用户 {i+1}: {user.username} (状态: {user.status.value}, 类型: {user.user_type.value})")


if __name__ == "__main__":
    asyncio.run(check_user_count())