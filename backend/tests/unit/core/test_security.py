#!/usr/bin/env python3
"""
安全模块单元测试
测试JWT、密码加密、权限验证等安全相关功能
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from backend.core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token,
    verify_token, get_token_payload,
    get_current_user, get_current_active_user,
    get_current_admin_user, authenticate_user,
    PasswordStrengthChecker, SecurityAuditLogger
)
from backend.core.exceptions import AuthenticationError, AuthorizationError
from backend.models.user import User, UserRole


class TestPasswordSecurity:
    """测试密码安全相关功能"""

    def test_password_hashing_and_verification(self):
        """测试密码哈希和验证"""
        password = "MySecurePassword123!"
        
        # 测试密码哈希
        hashed_password = get_password_hash(password)
        assert hashed_password != password
        assert len(hashed_password) > 0
        
        # 测试密码验证
        assert verify_password(password, hashed_password) == True
        assert verify_password("WrongPassword", hashed_password) == False

    def test_password_hashing_consistency(self):
        """测试密码哈希的一致性"""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # 相同密码应该产生不同的哈希值（salt不同）
        assert hash1 != hash2
        
        # 但都应该能验证通过
        assert verify_password(password, hash1) == True
        assert verify_password(password, hash2) == True

    def test_empty_password_handling(self):
        """测试空密码处理"""
        with pytest.raises(ValueError, match="密码不能为空"):
            get_password_hash("")
        
        with pytest.raises(ValueError, match="密码不能为空"):
            verify_password("", "some_hash")


class TestJWTTokens:
    """测试JWT令牌相关功能"""

    @patch('backend.core.security.SECRET_KEY', 'test-secret-key')
    @patch('backend.core.security.ALGORITHM', 'HS256')
    def test_create_access_token(self):
        """测试创建访问令牌"""
        payload = {"sub": "test@example.com", "role": "user"}
        token = create_access_token(payload)
        
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT有三个部分
        
        # 验证令牌可以解码
        decoded = jwt.decode(token, 'test-secret-key', algorithms=['HS256'])
        assert decoded["sub"] == "test@example.com"
        assert decoded["role"] == "user"
        assert "exp" in decoded

    @patch('backend.core.security.SECRET_KEY', 'test-secret-key')
    @patch('backend.core.security.ALGORITHM', 'HS256')
    @patch('backend.core.security.ACCESS_TOKEN_EXPIRE_MINUTES', 60)
    def test_create_access_token_with_expiry(self):
        """测试带过期时间的访问令牌"""
        payload = {"sub": "test@example.com"}
        token = create_access_token(payload)
        
        decoded = jwt.decode(token, 'test-secret-key', algorithms=['HS256'])
        
        # 验证过期时间设置正确（大约1小时后）
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.utcnow()
        time_diff = exp_time - now
        assert 3500 <= time_diff.total_seconds() <= 3700  # 允许一些误差

    @patch('backend.core.security.SECRET_KEY', 'test-secret-key')
    @patch('backend.core.security.ALGORITHM', 'HS256')
    def test_create_refresh_token(self):
        """测试创建刷新令牌"""
        payload = {"sub": "test@example.com"}
        token = create_refresh_token(payload)
        
        decoded = jwt.decode(token, 'test-secret-key', algorithms=['HS256'])
        assert decoded["sub"] == "test@example.com"
        assert decoded["type"] == "refresh"

    @patch('backend.core.security.SECRET_KEY', 'wrong-key')
    def test_verify_token_invalid_signature(self):
        """测试验证无效签名的令牌"""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        
        with pytest.raises(AuthenticationError, match="无效的令牌签名"):
            verify_token(token)

    @patch('backend.core.security.SECRET_KEY', 'test-secret-key')
    @patch('backend.core.security.ALGORITHM', 'HS256')
    def test_verify_token_expired(self):
        """测试验证过期令牌"""
        # 创建一个已过期的令牌
        expired_payload = {
            "sub": "test@example.com",
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        token = jwt.encode(expired_payload, 'test-secret-key', algorithm='HS256')
        
        with pytest.raises(AuthenticationError, match="令牌已过期"):
            verify_token(token)

    @patch('backend.core.security.SECRET_KEY', 'test-secret-key')
    @patch('backend.core.security.ALGORITHM', 'HS256')
    def test_get_token_payload(self):
        """测试获取令牌载荷"""
        payload = {"sub": "test@example.com", "role": "admin"}
        token = create_access_token(payload)
        
        retrieved_payload = get_token_payload(token)
        assert retrieved_payload["sub"] == "test@example.com"
        assert retrieved_payload["role"] == "admin"


class TestAuthentication:
    """测试用户认证功能"""

    @patch('backend.core.security.User')
    def test_authenticate_user_success(self, mock_user_class):
        """测试用户认证成功"""
        # Mock用户对象
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = get_password_hash("correct_password")
        mock_user.is_active = True
        mock_user.role = UserRole.USER.value
        
        mock_user_class.query.filter.return_value.first.return_value = mock_user
        
        authenticated_user = authenticate_user("test@example.com", "correct_password")
        assert authenticated_user == mock_user

    @patch('backend.core.security.User')
    def test_authenticate_user_wrong_password(self, mock_user_class):
        """测试用户认证失败-密码错误"""
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = get_password_hash("correct_password")
        mock_user.is_active = True
        
        mock_user_class.query.filter.return_value.first.return_value = mock_user
        
        with pytest.raises(AuthenticationError, match="密码错误"):
            authenticate_user("test@example.com", "wrong_password")

    @patch('backend.core.security.User')
    def test_authenticate_user_user_not_found(self, mock_user_class):
        """测试用户认证失败-用户不存在"""
        mock_user_class.query.filter.return_value.first.return_value = None
        
        with pytest.raises(AuthenticationError, match="用户不存在"):
            authenticate_user("nonexistent@example.com", "password")

    @patch('backend.core.security.User')
    def test_authenticate_user_inactive_user(self, mock_user_class):
        """测试用户认证失败-用户未激活"""
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = get_password_hash("password")
        mock_user.is_active = False
        
        mock_user_class.query.filter.return_value.first.return_value = mock_user
        
        with pytest.raises(AuthenticationError, match="用户账户已被禁用"):
            authenticate_user("test@example.com", "password")


class TestCurrentUserDependency:
    """测试当前用户依赖项"""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """测试获取当前用户成功"""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        
        credentials = MagicMock()
        credentials.credentials = "valid_token"
        
        with patch('backend.core.security.verify_token') as mock_verify:
            mock_verify.return_value = {"sub": "test@example.com"}
            
            with patch('backend.core.security.User') as mock_user_class:
                mock_user_class.query.filter.return_value.first.return_value = mock_user
                
                result = await get_current_user(credentials)
                assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """测试没有凭据的情况"""
        with pytest.raises(AuthenticationError, match="Not authenticated"):
            await get_current_user(None)

    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive(self):
        """测试非活跃用户"""
        mock_user = MagicMock()
        mock_user.is_active = False
        
        with pytest.raises(AuthenticationError, match="用户账户已被禁用"):
            await get_current_active_user(mock_user)

    @pytest.mark.asyncio
    async def test_get_current_admin_user_not_admin(self):
        """测试非管理员用户访问管理员接口"""
        mock_user = MagicMock()
        mock_user.role = UserRole.USER.value
        
        with pytest.raises(AuthorizationError, match="需要管理员权限"):
            await get_current_admin_user(mock_user)

    @pytest.mark.asyncio
    async def test_get_current_admin_user_is_admin(self):
        """测试管理员用户访问管理员接口"""
        mock_user = MagicMock()
        mock_user.role = UserRole.ADMIN.value
        
        result = await get_current_admin_user(mock_user)
        assert result == mock_user


class TestPasswordStrengthChecker:
    """测试密码强度检查器"""

    def test_check_password_strength_weak(self):
        """测试弱密码检查"""
        checker = PasswordStrengthChecker()
        
        # 测试各种弱密码
        weak_passwords = [
            "123456",
            "password",
            "abc123",
            "aaaaaa",
            "short",
            ""
        ]
        
        for pwd in weak_passwords:
            score = checker.check_strength(pwd)
            issues = checker.get_issues(pwd)
            assert score < 3  # 弱密码得分应该小于3
            assert len(issues) > 0  # 应该有问题描述

    def test_check_password_strength_strong(self):
        """测试强密码检查"""
        checker = PasswordStrengthChecker()
        
        strong_passwords = [
            "MySecureP@ssw0rd123!",
            "Complex#Pass2024$Word",
            "Str0ng&Prec1se#Pass"
        ]
        
        for pwd in strong_passwords:
            score = checker.check_strength(pwd)
            issues = checker.get_issues(pwd)
            assert score >= 4  # 强密码得分应该大于等于4
            # 强密码可能没有或只有很少的问题

    def test_password_strength_categories(self):
        """测试密码强度分类"""
        checker = PasswordStrengthChecker()
        
        assert checker.get_strength_category(1) == "很弱"
        assert checker.get_strength_category(2) == "弱"
        assert checker.get_strength_category(3) == "一般"
        assert checker.get_strength_category(4) == "强"
        assert checker.get_strength_category(5) == "很强"


class TestSecurityAuditLogger:
    """测试安全审计日志记录器"""

    def test_log_event(self):
        """测试记录安全事件"""
        logger = SecurityAuditLogger()
        
        # 测试记录登录成功事件
        logger.log_event(
            event_type="LOGIN_SUCCESS",
            user_email="test@example.com",
            ip_address="192.168.1.100",
            details={"user_agent": "Mozilla/5.0"}
        )
        
        # 验证日志条目被创建（这里主要是测试不会出错）
        assert len(logger.events) > 0

    def test_log_failed_login(self):
        """测试记录登录失败事件"""
        logger = SecurityAuditLogger()
        
        logger.log_failed_login(
            email="test@example.com",
            ip_address="192.168.1.100",
            reason="Invalid password"
        )
        
        assert len(logger.events) > 0
        event = logger.events[-1]
        assert event["event_type"] == "LOGIN_FAILED"
        assert event["details"]["reason"] == "Invalid password"

    def test_get_recent_events(self):
        """测试获取最近事件"""
        logger = SecurityAuditLogger()
        
        # 添加一些测试事件
        for i in range(5):
            logger.log_event(f"EVENT_{i}", "test@example.com")
        
        recent_events = logger.get_recent_events(limit=3)
        assert len(recent_events) == 3


class TestSecurityEdgeCases:
    """测试安全模块的边界情况"""

    def test_very_long_password(self):
        """测试超长密码"""
        long_password = "a" * 1000
        hashed = get_password_hash(long_password)
        assert verify_password(long_password, hashed) == True

    def test_unicode_password(self):
        """测试Unicode字符密码"""
        unicode_password = "密码🔐123🎯"
        hashed = get_password_hash(unicode_password)
        assert verify_password(unicode_password, hashed) == True

    @patch('backend.core.security.SECRET_KEY', '')
    def test_empty_secret_key(self):
        """测试空密钥"""
        with pytest.raises(Exception):  # JWT应该抛出异常
            create_access_token({"sub": "test"})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
