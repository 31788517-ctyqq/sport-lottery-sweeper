"""
API端点单元测试
测试所有管理员API端点的功能和响应
"""
import os
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent.parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

# 在导入任何backend模块之前设置环境变量
# 使用内存数据库
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ASYNC_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 从正确的模块导入
import enum
from backend.main import create_app
from backend.database import get_db
from backend.models.user import User, UserTypeEnum
from backend.core.security import get_password_hash
from backend.core.database import Base

def test_auth_login():
    """测试认证登录端点"""
    print("开始测试认证登录端点...")
    
    # 创建内存数据库引擎
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    
    # 创建测试用户
    db = TestingSessionLocal()
    test_user = User(
        username="test",
        email="test@example.com",
        password_hash=get_password_hash("test123"),
        first_name="Test",
        last_name="User",
        role=UserTypeEnum.NORMAL,
        status="active",
        is_verified=True
    )
    db.add(test_user)
    db.commit()
    db.close()
    
    # 测试登录
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test", "password": "test123"}
    )
    
    if response.status_code != 200:
        print(f"Test failed: {response.text}")
        return False
        
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    print("✓ 认证登录测试通过")
    return True


if __name__ == "__main__":
    success = test_auth_login()
    if success:
        print("\n✅ 所有测试通过!")
        sys.exit(0)
    else:
        print("\n❌ 测试失败!")
        sys.exit(1)
