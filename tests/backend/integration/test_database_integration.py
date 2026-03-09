"""
鏁版嵁搴撻泦鎴愭祴璇?
娴嬭瘯鏁版嵁搴撹繛鎺ャ€丆RUD鎿嶄綔浠ュ強涓嶅悓妯″潡涔嬮棿鐨勬暟鎹氦浜?
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
    """娴嬭瘯鏁版嵁搴撹繛鎺?""
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        row = result.fetchone()
        assert row is not None
        assert row[0] == 1
    
    await engine.dispose()
    print("SUCCESS 鏁版嵁搴撹繛鎺ユ祴璇曢€氳繃")


@pytest.mark.asyncio
async def test_admin_user_crud_integration():
    """娴嬭瘯绠＄悊鍛樼敤鎴风殑CRUD鎿嶄綔闆嗘垚"""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 鍒涘缓娴嬭瘯鐢ㄦ埛
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
        
        # 浣跨敤CRUD鍒涘缓鐢ㄦ埛
        created_user = await crud_admin_user.create(
            session, 
            obj_in=new_user_data,
            created_by=None
        )
        
        # 楠岃瘉鐢ㄦ埛宸插垱寤?
        assert created_user.id is not None
        assert created_user.username == new_user_data["username"]
        
        # 閫氳繃ID鑾峰彇鐢ㄦ埛
        retrieved_user = await crud_admin_user.get(session, id=created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.username == new_user_data["username"]
        
        # 鏇存柊鐢ㄦ埛淇℃伅
        update_data = {"real_name": "Updated Integration Test User"}
        updated_user = await crud_admin_user.update(
            session, 
            db_obj=retrieved_user, 
            obj_in=update_data
        )
        assert updated_user.real_name == update_data["real_name"]
        
        # 鍒犻櫎鐢ㄦ埛
        deletion_result = await crud_admin_user.remove(session, id=created_user.id)
        assert deletion_result is True
        
        # 楠岃瘉鐢ㄦ埛宸茶鍒犻櫎
        deleted_user = await crud_admin_user.get(session, id=created_user.id)
        assert deleted_user is None
    
    await engine.dispose()
    print("SUCCESS 绠＄悊鍛樼敤鎴稢RUD闆嗘垚娴嬭瘯閫氳繃")


@pytest.mark.asyncio
async def test_crawler_config_crud_integration():
    """娴嬭瘯鐖櫕閰嶇疆鐨凜RUD鎿嶄綔闆嗘垚"""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 鍒涘缓娴嬭瘯閰嶇疆
        new_config_data = {
            "name": "Integration Test Config",
            "description": "Configuration for integration test",
            "url": "https://test.example.com",
            "frequency": 3600,
            "is_active": True,
            "config_data": '{"timeout": 30}'
        }
        
        # 浣跨敤CRUD鍒涘缓閰嶇疆
        created_config = await crud_crawler_config.create(session, obj_in=new_config_data)
        
        # 楠岃瘉閰嶇疆宸插垱寤?
        assert created_config.id is not None
        assert created_config.name == new_config_data["name"]
        
        # 閫氳繃ID鑾峰彇閰嶇疆
        retrieved_config = await crud_crawler_config.get(session, id=created_config.id)
        assert retrieved_config is not None
        assert retrieved_config.name == new_config_data["name"]
        
        # 鏇存柊閰嶇疆
        update_data = {"frequency": 7200}
        updated_config = await crud_crawler_config.update(
            session, 
            db_obj=retrieved_config, 
            obj_in=update_data
        )
        assert updated_config.frequency == update_data["frequency"]
        
        # 鍒犻櫎閰嶇疆
        deletion_result = await crud_crawler_config.remove(session, id=created_config.id)
        assert deletion_result is True
        
        # 楠岃瘉閰嶇疆宸茶鍒犻櫎
        deleted_config = await crud_crawler_config.get(session, id=created_config.id)
        assert deleted_config is None
    
    await engine.dispose()
    print("SUCCESS 鐖櫕閰嶇疆CRUD闆嗘垚娴嬭瘯閫氳繃")


@pytest.mark.asyncio
async def test_cross_module_integration():
    """娴嬭瘯璺ㄦā鍧楁暟鎹氦浜掗泦鎴?""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 鍒涘缓涓€涓鐞嗗憳鐢ㄦ埛
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
        
        # 鍒涘缓涓€涓叧鑱旇绠＄悊鍛樼殑鐖櫕閰嶇疆
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
        
        # 楠岃瘉涓や釜瀹炰綋閮藉凡鍒涘缓
        assert created_admin.id is not None
        assert created_config.id is not None
        assert created_config.created_by == created_admin.id
        
        # 楠岃瘉鍙互閫氳繃鍏宠仈瀛楁鏌ヨ
        configs_by_creator = await crud_crawler_config.get_multi(
            session,
            created_by=created_admin.id
        )
        assert len(configs_by_creator[0]) >= 1
        
        # 娓呯悊鏁版嵁
        await crud_crawler_config.remove(session, id=created_config.id)
        await crud_admin_user.remove(session, id=created_admin.id)
    
    await engine.dispose()
    print("SUCCESS 璺ㄦā鍧楁暟鎹氦浜掗泦鎴愭祴璇曢€氳繃")


if __name__ == "__main__":
    asyncio.run(test_database_connection())
    asyncio.run(test_admin_user_crud_integration())
    asyncio.run(test_crawler_config_crud_integration())
    asyncio.run(test_cross_module_integration())
