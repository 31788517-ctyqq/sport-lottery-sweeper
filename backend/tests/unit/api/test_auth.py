"""
认证API单元测试
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.api.v1.auth import router, create_access_token
from backend.core.security import verify_password, get_password_hash
from backend.schemas.user import UserCreate
from backend.services.auth_service import AuthenticationService

class TestPasswordUtils:
    """测试密码工具函数"""
    
    def test_verify_password_success(self):
        """测试密码验证成功"""
        plain_password = "testpassword123"
        hashed_password = get_password_hash(plain_password)
        
        assert verify_password(plain_password, hashed_password) == True
    
    def test_verify_password_failure(self):
        """测试密码验证失败"""
        plain_password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed_password = get_password_hash(plain_password)
        
        assert verify_password(wrong_password, hashed_password) == False
    
    def test_password_hash_different_each_time(self):
        """测试相同密码每次哈希结果不同"""
        plain_password = "testpassword123"
        hash1 = get_password_hash(plain_password)
        hash2 = get_password_hash(plain_password)
        
        assert hash1 != hash2
        assert verify_password(plain_password, hash1) == True
        assert verify_password(plain_password, hash2) == True

class TestCreateAccessToken:
    """测试访问令牌创建"""
    
    @patch('backend.api.v1.auth.jwt.encode')
    @patch('backend.api.v1.auth.datetime')
    def test_create_access_token_no_expiry(self, mock_datetime, mock_jwt_encode):
        """测试创建无过期时间的访问令牌"""
        from datetime import datetime, timedelta
        
        # Mock datetime
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.return_value = mock_now
        
        # Mock JWT encode
        mock_jwt_encode.return_value = "test-jwt-token"
        
        result = create_access_token({"sub": "testuser"})
        
        # 验证JWT encode被正确调用
        mock_jwt_encode.assert_called_once()
        call_args = mock_jwt_encode.call_args
        
        # 验证payload包含正确的subject和过期时间
        payload = call_args[0][0]
        assert payload["sub"] == "testuser"
        assert "exp" in payload
        
        # 验证过期时间是30分钟后
        expected_exp = mock_now + timedelta(minutes=30)
        assert payload["exp"] == expected_exp
        
        assert result == "test-jwt-token"
    
    @patch('backend.api.v1.auth.jwt.encode')
    @patch('backend.api.v1.auth.datetime')
    def test_create_access_token_with_expiry(self, mock_datetime, mock_jwt_encode):
        """测试创建有自定义过期时间的访问令牌"""
        from datetime import datetime, timedelta
        
        # Mock datetime
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.return_value = mock_now
        
        # Mock JWT encode
        mock_jwt_encode.return_value = "test-jwt-token-custom"
        
        custom_expiry = timedelta(hours=2)
        result = create_access_token({"sub": "testuser"}, expires_delta=custom_expiry)
        
        # 验证JWT encode被正确调用
        call_args = mock_jwt_encode.call_args
        payload = call_args[0][0]
        
        # 验证过期时间是2小时后
        expected_exp = mock_now + custom_expiry
        assert payload["exp"] == expected_exp
        
        assert result == "test-jwt-token-custom"

class TestAuthService:
    """测试认证服务"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def auth_service(self, mock_db):
        """创建认证服务实例"""
        return AuthenticationService(mock_db)
    
    def test_authenticate_user_success(self, auth_service):
        """测试用户认证成功"""
        # Mock用户对象
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.hashed_password = get_password_hash("testpass")
        mock_user.is_active = True
        mock_user.status = "active"
        
        # Mock数据库查询
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        auth_service.db.query.return_value = mock_query
        
        result = auth_service.authenticate_user("testuser", "testpass")
        
        assert result == mock_user
        # 验证查询被调用
        auth_service.db.query.assert_called_once()
    
    def test_authenticate_user_wrong_password(self, auth_service):
        """测试用户认证失败 - 密码错误"""
        # Mock用户对象
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.hashed_password = get_password_hash("correctpass")
        mock_user.is_active = True
        mock_user.status = "active"
        
        # Mock数据库查询
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        auth_service.db.query.return_value = mock_query
        
        result = auth_service.authenticate_user("testuser", "wrongpass")
        
        assert result is None
    
    def test_authenticate_user_inactive(self, auth_service):
        """测试用户认证失败 - 用户未激活"""
        # Mock用户对象
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.hashed_password = get_password_hash("testpass")
        mock_user.is_active = False
        mock_user.status = "inactive"
        
        # Mock数据库查询
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        auth_service.db.query.return_value = mock_query
        
        result = auth_service.authenticate_user("testuser", "testpass")
        
        assert result is None
    
    def test_authenticate_user_not_found(self, auth_service):
        """测试用户认证失败 - 用户不存在"""
        # Mock数据库查询返回None
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        auth_service.db.query.return_value = mock_query
        
        result = auth_service.authenticate_user("nonexistent", "testpass")
        
        assert result is None

class TestRegisterUser:
    """测试用户注册功能"""
    
    @pytest.mark.asyncio
    @patch('backend.api.v1.auth.AuthenticationService')
    async def test_register_user_success(self, mock_auth_service_class, test_client, sample_user_data):
        """测试用户注册成功"""
        # Mock认证服务
        mock_auth_instance = Mock()
        mock_auth_instance.register_user.return_value = (True, Mock(username="testuser"), "注册成功")
        mock_auth_service_class.return_value = mock_auth_instance
        
        # 模拟JWT token创建
        with patch('backend.api.v1.auth.create_access_token', return_value="test-token"):
            response = test_client.post("/api/v1/register", json=sample_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "注册成功"
        assert "access_token" in data["data"]
    
    @pytest.mark.asyncio
    @patch('backend.api.v1.auth.AuthenticationService')
    async def test_register_user_failure(self, mock_auth_service_class, test_client, sample_user_data):
        """测试用户注册失败"""
        # Mock认证服务返回失败
        mock_auth_instance = Mock()
        mock_auth_instance.register_user.return_value = (False, None, "用户名已存在")
        mock_auth_service_class.return_value = mock_auth_instance
        
        response = test_client.post("/api/v1/register", json=sample_user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "用户名已存在" in data["detail"]

class TestLoginUser:
    """测试用户登录功能"""
    
    @pytest.mark.asyncio
    @patch('backend.api.v1.auth.AuthenticationService')
    async def test_login_user_success(self, mock_auth_service_class, test_client):
        """测试用户登录成功"""
        login_data = {"username": "testuser", "password": "testpass"}
        
        # Mock认证服务
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.status.value = "active"
        
        mock_auth_instance = Mock()
        mock_auth_instance.authenticate_user.return_value = mock_user
        mock_auth_service_class.return_value = mock_auth_instance
        
        # Mock JWT token创建
        with patch.multiple('backend.api.v1.auth',
                            create_access_token=Mock(return_value="test-token"),
                            create_refresh_token=Mock(return_value="test-refresh-token")):
            response = test_client.post("/api/v1/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test-token"
        assert data["refresh_token"] == "test-refresh-token"
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800  # ACCESS_TOKEN_EXPIRE_MINUTES * 60
        assert data["user_info"]["username"] == "testuser"
    
    @pytest.mark.asyncio
    @patch('backend.api.v1.auth.AuthenticationService')
    async def test_login_user_invalid_credentials(self, mock_auth_service_class, test_client):
        """测试用户登录失败 - 凭据无效"""
        login_data = {"username": "testuser", "password": "wrongpass"}
        
        # Mock认证服务返回None（认证失败）
        mock_auth_instance = Mock()
        mock_auth_instance.authenticate_user.return_value = None
        mock_auth_service_class.return_value = mock_auth_instance
        
        response = test_client.post("/api/v1/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "用户名或密码错误"
        assert "WWW-Authenticate" in response.headers