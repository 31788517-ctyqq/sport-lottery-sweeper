#!/usr/bin/env python3
# AI_WORKING: coder1 @2026-01-29 - 创建AuthenticationService单元测试
"""
AuthenticationService单元测试模块
测试认证服务的核心业务逻辑
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

# 导入服务
try:
    from backend.services.auth_service import AuthenticationService
    from backend.models.user import User, UserStatus
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    sys.path.append('.')
    from backend.services.auth_service import AuthenticationService
    from backend.models.user import User, UserStatus


class TestAuthenticationService:
    """AuthenticationService测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def auth_service(self, mock_db):
        """创建认证服务实例"""
        return AuthenticationService(mock_db)
    
    @pytest.fixture
    def sample_user(self):
        """创建示例用户"""
        user = User()
        user.id = 1
        user.username = 'testuser'
        user.email = 'test@example.com'
        user.hashed_password = 'hashed_password'
        user.nickname = 'Test User'
        user.status = UserStatus.ACTIVE
        user.email_verified = True
        user.phone_verified = False
        return user
    
    def test_init(self, mock_db):
        """测试服务初始化"""
        service = AuthenticationService(mock_db)
        assert service.db == mock_db
        assert hasattr(service, 'token_expire_minutes')
        assert hasattr(service, 'refresh_token_expire_days')
    
    def test_register_user_success(self, auth_service, mock_db):
        """测试成功注册用户"""
        # 模拟查询结果 - 用户不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # 模拟密码验证
        with patch('backend.services.auth_service.validate_password_strength') as mock_validate:
            mock_validate.return_value = {"valid": True, "errors": []}
            
            # 模拟密码哈希
            with patch('backend.services.auth_service.get_password_hash') as mock_hash:
                mock_hash.return_value = 'hashed_password'
                
                # 模拟保存用户
                mock_db.add = Mock()
                mock_db.commit = Mock()
                mock_db.refresh = Mock()
                
                # 执行注册
                success, user, message = auth_service.register_user(
                    username='newuser',
                    email='new@example.com',
                    password='Password123!',
                    confirm_password='Password123!'
                )
                
                # 验证结果
                assert success is True
                assert user is not None
                assert user.username == 'newuser'
                assert user.email == 'new@example.com'
                assert user.hashed_password == 'hashed_password'
                assert message == '注册成功'
                
                # 验证数据库操作
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
                mock_db.refresh.assert_called_once()
    
    def test_register_user_password_mismatch(self, auth_service):
        """测试注册用户 - 密码不匹配"""
        success, user, message = auth_service.register_user(
            username='newuser',
            email='new@example.com',
            password='Password123!',
            confirm_password='Different123!'
        )
        
        assert success is False
        assert user is None
        assert message == '两次输入的密码不一致'
    
    def test_register_user_weak_password(self, auth_service):
        """测试注册用户 - 密码强度不足"""
        with patch('backend.services.auth_service.validate_password_strength') as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "errors": ["密码长度至少8位", "必须包含数字"]
            }
            
            success, user, message = auth_service.register_user(
                username='newuser',
                email='new@example.com',
                password='weak',
                confirm_password='weak'
            )
            
            assert success is False
            assert user is None
            assert '密码强度不足' in message
    
    def test_register_user_already_exists(self, auth_service, mock_db):
        """测试注册用户 - 用户已存在"""
        # 模拟查询结果 - 用户已存在
        existing_user = Mock(spec=User)
        existing_user.username = 'existinguser'
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user
        
        success, user, message = auth_service.register_user(
            username='existinguser',
            email='existing@example.com',
            password='Password123!',
            confirm_password='Password123!'
        )
        
        assert success is False
        assert user is None
        assert '用户名或邮箱已存在' in message
    
    @patch('backend.services.auth_service.verify_password')
    def test_authenticate_user_success(self, mock_verify, auth_service, mock_db, sample_user):
        """测试成功认证用户"""
        # 模拟查询结果
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        
        # 模拟密码验证
        mock_verify.return_value = True
        
        # 模拟更新登录信息
        mock_db.commit = Mock()
        
        # 执行认证
        success, user, message = auth_service.authenticate_user(
            username='testuser',
            password='correct_password'
        )
        
        assert success is True
        assert user == sample_user
        assert message == '认证成功'
        
        # 验证登录信息更新
        assert sample_user.last_login_time is not None
        assert sample_user.login_count == 1
        mock_db.commit.assert_called_once()
    
    @patch('backend.services.auth_service.verify_password')
    def test_authenticate_user_wrong_password(self, mock_verify, auth_service, mock_db, sample_user):
        """测试认证用户 - 密码错误"""
        # 模拟查询结果
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        
        # 模拟密码验证失败
        mock_verify.return_value = False
        
        success, user, message = auth_service.authenticate_user(
            username='testuser',
            password='wrong_password'
        )
        
        assert success is False
        assert user is None
        assert '用户名或密码错误' in message
    
    def test_authenticate_user_not_found(self, auth_service, mock_db):
        """测试认证用户 - 用户不存在"""
        # 模拟查询结果 - 用户不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        success, user, message = auth_service.authenticate_user(
            username='nonexistent',
            password='password'
        )
        
        assert success is False
        assert user is None
        assert '用户名或密码错误' in message
    
    def test_authenticate_user_inactive(self, auth_service, mock_db, sample_user):
        """测试认证用户 - 用户不活跃"""
        sample_user.status = UserStatus.INACTIVE
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        
        success, user, message = auth_service.authenticate_user(
            username='testuser',
            password='password'
        )
        
        assert success is False
        assert user is None
        assert '用户账户已停用' in message
    
    @patch('backend.services.auth_service.create_access_token')
    @patch('backend.services.auth_service.create_refresh_token')
    def test_generate_tokens(self, mock_refresh, mock_access, auth_service, sample_user):
        """测试生成令牌"""
        # 模拟令牌生成
        mock_access.return_value = 'access_token'
        mock_refresh.return_value = 'refresh_token'
        
        access_token, refresh_token = auth_service.generate_tokens(sample_user)
        
        assert access_token == 'access_token'
        assert refresh_token == 'refresh_token'
        
        # 验证调用参数
        mock_access.assert_called_once()
        mock_refresh.assert_called_once()
    
    @patch('backend.services.auth_service.verify_token')
    def test_verify_access_token_valid(self, mock_verify, auth_service, sample_user):
        """测试验证有效的访问令牌"""
        mock_verify.return_value = {"sub": "1", "username": "testuser"}
        
        result = auth_service.verify_access_token('valid_token')
        
        assert result is not None
        assert result["sub"] == "1"
        assert result["username"] == "testuser"
        
        mock_verify.assert_called_once_with('valid_token')
    
    @patch('backend.services.auth_service.verify_token')
    def test_verify_access_token_invalid(self, mock_verify, auth_service):
        """测试验证无效的访问令牌"""
        mock_verify.return_value = None
        
        result = auth_service.verify_access_token('invalid_token')
        
        assert result is None
        
        mock_verify.assert_called_once_with('invalid_token')
    
    def test_update_user_profile(self, auth_service, mock_db, sample_user):
        """测试更新用户资料"""
        # 模拟查询结果
        mock_db.query.return_value.filter.return_value.first.return_value = sample_user
        
        mock_db.commit = Mock()
        
        # 执行更新
        success, updated_user, message = auth_service.update_user_profile(
            user_id=1,
            nickname='New Nickname',
            bio='New bio text',
            phone='13987654321'
        )
        
        assert success is True
        assert updated_user == sample_user
        assert sample_user.nickname == 'New Nickname'
        assert sample_user.bio == 'New bio text'
        assert sample_user.phone == '13987654321'
        assert message == '资料更新成功'
        
        mock_db.commit.assert_called_once()
    
    def test_update_user_profile_not_found(self, auth_service, mock_db):
        """测试更新用户资料 - 用户不存在"""
        # 模拟查询结果 - 用户不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        success, user, message = auth_service.update_user_profile(
            user_id=999,
            nickname='New Nickname'
        )
        
        assert success is False
        assert user is None
        assert '用户不存在' in message


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

# AI_DONE: coder1 @2026-01-29