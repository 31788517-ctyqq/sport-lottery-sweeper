"""
数据库集成测试
测试数据库连接、CRUD操作以及不同模块之间的数据交互
"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.models.admin_user import AdminUser
from backend.models.crawler_config import CrawlerConfig
from backend.crud.admin_user import admin_user as crud_admin_user
from backend.crud.crawler_config import crawler_config as crud_crawler_config
from backend.core.security import get_password_hash
from backend.config import settings


@pytest.mark.asyncio
async def test_database_connection():
    """测试数据库连接"""
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        row = result.fetchone()
        assert row is not None
        assert row[0] == 1
    
    await engine.dispose()
    print("✅ 数据库连接测试通过")


@pytest.mark.asyncio
async def test_admin_user_crud_integration():
    """测试管理员用户的CRUD操作集成"""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 创建测试用户
        new_user_data = {
            "username": "integration_test_user",
            "email": "test@example.com",
            "password": "testpassword123",
            "real_name": "Integration Test User",
            "phone": "+1234567890",
            "department": "Test Department",
            "position": "Tester",
            "role": "admin"
        }
        
        # 使用CRUD创建用户
        created_user = await crud_admin_user.create(
            session, 
            obj_in=new_user_data,
            created_by=None
        )
        
        # 验证用户已创建
        assert created_user.id is not None
        assert created_user.username == new_user_data["username"]
        
        # 通过ID获取用户
        retrieved_user = await crud_admin_user.get(session, id=created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.username == new_user_data["username"]
        
        # 更新用户信息
        update_data = {"real_name": "Updated Integration Test User"}
        updated_user = await crud_admin_user.update(
            session, 
            db_obj=retrieved_user, 
            obj_in=update_data
        )
        assert updated_user.real_name == update_data["real_name"]
        
        # 删除用户
        deletion_result = await crud_admin_user.remove(session, id=created_user.id)
        assert deletion_result is True
        
        # 验证用户已被删除
        deleted_user = await crud_admin_user.get(session, id=created_user.id)
        assert deleted_user is None
    
    await engine.dispose()
    print("✅ 管理员用户CRUD集成测试通过")


@pytest.mark.asyncio
async def test_crawler_config_crud_integration():
    """测试爬虫配置的CRUD操作集成"""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 创建测试配置
        new_config_data = {
            "name": "Integration Test Config",
            "description": "Configuration for integration test",
            "url": "https://test.example.com",
            "frequency": 3600,
            "is_active": True,
            "config_data": '{"timeout": 30}'
        }
        
        # 使用CRUD创建配置
        created_config = await crud_crawler_config.create(session, obj_in=new_config_data)
        
        # 验证配置已创建
        assert created_config.id is not None
        assert created_config.name == new_config_data["name"]
        
        # 通过ID获取配置
        retrieved_config = await crud_crawler_config.get(session, id=created_config.id)
        assert retrieved_config is not None
        assert retrieved_config.name == new_config_data["name"]
        
        # 更新配置
        update_data = {"frequency": 7200}
        updated_config = await crud_crawler_config.update(
            session, 
            db_obj=retrieved_config, 
            obj_in=update_data
        )
        assert updated_config.frequency == update_data["frequency"]
        
        # 删除配置
        deletion_result = await crud_crawler_config.remove(session, id=created_config.id)
        assert deletion_result is True
        
        # 验证配置已被删除
        deleted_config = await crud_crawler_config.get(session, id=created_config.id)
        assert deleted_config is None
    
    await engine.dispose()
    print("✅ 爬虫配置CRUD集成测试通过")


@pytest.mark.asyncio
async def test_cross_module_integration():
    """测试跨模块数据交互集成"""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 创建一个管理员用户
        admin_user_data = {
            "username": "cross_module_admin",
            "email": "cross_module@example.com",
            "password": "password123",
            "real_name": "Cross Module Admin",
            "phone": "+1234567890",
            "department": "Integration",
            "position": "Manager",
            "role": "admin"
        }
        
        created_admin = await crud_admin_user.create(
            session, 
            obj_in=admin_user_data,
            created_by=None
        )
        
        # 创建一个关联该管理员的爬虫配置
        crawler_config_data = {
            "name": "Admin Associated Config",
            "description": "Config associated with admin user",
            "url": "https://admin-associated.example.com",
            "frequency": 1800,
            "is_active": True,
            "config_data": '{"timeout": 30}',
            "created_by": created_admin.id
        }
        
        created_config = await crud_crawler_config.create(session, obj_in=crawler_config_data)
        
        # 验证两个实体都已创建
        assert created_admin.id is not None
        assert created_config.id is not None
        assert created_config.created_by == created_admin.id
        
        # 验证可以通过关联字段查询
        configs_by_creator = await crud_crawler_config.get_multi(
            session,
            created_by=created_admin.id
        )
        assert len(configs_by_creator[0]) >= 1
        
        # 清理数据
        await crud_crawler_config.remove(session, id=created_config.id)
        await crud_admin_user.remove(session, id=created_admin.id)
    
    await engine.dispose()
    print("✅ 跨模块数据交互集成测试通过")


if __name__ == "__main__":
    asyncio.run(test_database_connection())
    asyncio.run(test_admin_user_crud_integration())
    asyncio.run(test_crawler_config_crud_integration())
    asyncio.run(test_cross_module_integration())