#!/usr/bin/env python3
"""
测试配置文件
包含测试夹具、模拟对象和测试配置
"""

import sys
import os
# 添加项目根目录到Python路径，确保backend包可导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 导入应用模块
from backend.main import app
from backend.core.security import get_password_hash, verify_password
from backend.database import Base

# 测试数据库配置 (使用SQLite内存数据库)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# 创建测试引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

# 创建测试会话
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class MockQueryResult:
    """模拟SQLAlchemy查询结果"""
    def __init__(self, items=None):
        self.items = items or []
    
    def first(self):
        return self.items[0] if self.items else None
    
    def all(self):
        return self.items
    
    def filter(self, *args, **kwargs):
        return self
    
    def filter_by(self, **kwargs):
        return self
    
    def order_by(self, *args, **kwargs):
        return self
    
    def limit(self, limit):
        return MockQueryResult(self.items[:limit])
    
    def offset(self, offset):
        return MockQueryResult(self.items[offset:])
    
    def count(self):
        return len(self.items)
    
    def scalar(self):
        return self.items[0] if self.items else None

class MockDBSession:
    """模拟数据库会话"""
    def __init__(self):
        self.query_results = []
        self.added_objects = []
        self.deleted_objects = []
        self.committed = False
        self.rolled_back = False
    
    def query(self, model):
        return MockQueryResult(self.query_results)
    
    def add(self, obj):
        self.added_objects.append(obj)
    
    def delete(self, obj):
        self.deleted_objects.append(obj)
    
    def commit(self):
        self.committed = True
    
    def rollback(self):
        self.rolled_back = True
    
    def close(self):
        pass
    
    def flush(self):
        pass
    
    def refresh(self, obj):
        pass
    
    def execute(self, stmt):
        return Mock()
    
    @property
    def is_active(self):
        return True

@pytest.fixture(scope="session")
def test_app():
    """测试应用实例"""
    return app

@pytest.fixture(scope="session")
def test_client(test_app):
    """测试客户端"""
    return TestClient(test_app)

@pytest.fixture(scope="function")
def db_session():
    """数据库会话夹具"""
    # 创建测试表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # 清理测试数据
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_db_session():
    """模拟数据库会话"""
    return MockDBSession()

@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123"
    }

@pytest.fixture
def sample_login_data():
    """示例登录数据"""
    return {
        "username": "testuser",
        "password": "testpass123"
    }

@pytest.fixture
def sample_user_object():
    """示例用户对象"""
    user = Mock()
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.hashed_password = get_password_hash("testpass123")
    user.is_active = True
    user.status = "active"
    user.roles = ["user"]
    user.avatar = None
    user.last_login_time = datetime.utcnow()
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    
    # 添加角色属性
    role_mock = Mock()
    role_mock.name = "user"
    user.roles = [role_mock]
    
    return user

@pytest.fixture
def sample_admin_user():
    """示例管理员用户对象"""
    user = Mock()
    user.id = 2
    user.username = "admin"
    user.email = "admin@example.com"
    user.hashed_password = get_password_hash("adminpass123")
    user.is_active = True
    user.status = "active"
    user.roles = ["admin", "user"]
    user.avatar = "https://example.com/admin.jpg"
    user.last_login_time = datetime.utcnow()
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    
    # 添加角色属性
    admin_role = Mock()
    admin_role.name = "admin"
    user_role = Mock()
    user_role.name = "user"
    user.roles = [admin_role, user_role]
    
    return user

@pytest.fixture
def inactive_user():
    """示例非活跃用户对象"""
    user = Mock()
    user.id = 3
    user.username = "inactiveuser"
    user.email = "inactive@example.com"
    user.hashed_password = get_password_hash("testpass123")
    user.is_active = False  # 非活跃
    user.status = "inactive"
    user.roles = ["user"]
    user.avatar = None
    user.last_login_time = None
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    
    return user

@pytest.fixture
def mock_async_db():
    """模拟异步数据库"""
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.close = AsyncMock()
    mock_db.get = AsyncMock()
    mock_db.scalar = AsyncMock()
    mock_db.scalars = AsyncMock()
    return mock_db

@pytest.fixture
def mock_user_repository():
    """模拟用户仓储"""
    mock_repo = Mock()
    mock_repo.get_by_username = Mock(return_value=None)
    mock_repo.get_by_email = Mock(return_value=None)
    mock_repo.create_user = Mock(return_value=sample_user_object())
    mock_repo.get_user_by_id = Mock(return_value=sample_user_object())
    return mock_repo

@pytest.fixture
def mock_auth_service(sample_user_object, mock_db_session):
    """模拟认证服务"""
    with patch('backend.services.auth_service.AuthenticationService') as mock_class:
        mock_instance = mock_class.return_value
        mock_instance.register_user = Mock(return_value=(True, sample_user_object, "注册成功"))
        mock_instance.authenticate_user = Mock(return_value=sample_user_object)
        mock_instance.get_user_by_id = Mock(return_value=sample_user_object)
        mock_instance.update_last_login = Mock()
        yield mock_instance

@pytest.fixture
def mock_jwt_encode():
    """模拟JWT编码"""
    with patch('backend.api.v1.auth.jwt.encode') as mock:
        mock.return_value = "test-jwt-token"
        yield mock

@pytest.fixture
def mock_jwt_decode():
    """模拟JWT解码"""
    with patch('backend.api.v1.auth.jwt.decode') as mock:
        mock.return_value = {
            "sub": "1",
            "username": "testuser",
            "email": "test@example.com",
            "roles": ["user"],
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        yield mock

@pytest.fixture
def mock_datetime():
    """模拟datetime"""
    with patch('backend.api.v1.auth.datetime') as mock:
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock.utcnow.return_value = mock_now
        mock.return_value = mock_now
        yield mock

@pytest.fixture
def password_utils_test_data():
    """密码工具测试数据"""
    return {
        "valid_password": "StrongPass123!",
        "weak_password": "123",
        "empty_password": "",
        "common_password": "password123",
        "special_chars_only": "!!!@@@###",
        "numbers_only": "12345678",
        "letters_only": "abcdefgh",
        "with_spaces": "pass word 123"
    }

@pytest.fixture
def token_test_data():
    """令牌测试数据"""
    return {
        "valid_user_id": "1",
        "valid_subject": "testuser",
        "invalid_token": "invalid.jwt.token",
        "expired_timestamp": datetime.utcnow() - timedelta(hours=2),
        "future_timestamp": datetime.utcnow() + timedelta(hours=1)
    }

# 异步测试支持
@pytest.fixture(scope="session")
def event_loop():
    """事件循环夹具"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# 测试标记
def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )

# 测试数据清理
@pytest.fixture(autouse=True)
def setup_test_data():
    """自动使用的测试数据设置"""
    # 在每个测试前执行
    yield
    # 在每个测试后执行清理
    pass