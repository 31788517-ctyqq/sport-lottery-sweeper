#!/usr/bin/env python3
# AI_WORKING: coder1 @2026-01-29 - 创建User模型单元测试
"""
User模型单元测试模块
测试User模型的验证逻辑和属性方法
"""
import pytest
from datetime import datetime

# 导入模型
try:
    from backend.models.user import User, UserStatus, UserRole
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys

    sys.path.append(".")
    from backend.models.user import User, UserStatus, UserRole


class TestUserModel:
    """User模型测试类"""

    def test_user_status_enum(self):
        """测试用户状态枚举值"""
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.INACTIVE.value == "inactive"
        assert UserStatus.SUSPENDED.value == "suspended"
        assert UserStatus.BANNED.value == "banned"
        assert UserStatus.PENDING.value == "pending"

    def test_user_role_enum(self):
        """测试用户角色枚举值"""
        assert UserRole.USER.value == "user"
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MODERATOR.value == "moderator"
        assert UserRole.VIP.value == "vip"

    def test_username_validation_valid(self):
        """测试有效的用户名验证"""
        user = User()
        # 有效的用户名
        assert user.validate_username("username", "testuser123") == "testuser123"
        assert user.validate_username("username", "user_name") == "user_name"
        assert user.validate_username("username", "Test123") == "Test123"

    def test_username_validation_invalid_empty(self):
        """测试无效的用户名验证 - 空值"""
        user = User()
        with pytest.raises(ValueError, match="用户名不能为空"):
            user.validate_username("username", "")
        with pytest.raises(ValueError, match="用户名不能为空"):
            user.validate_username("username", "   ")

    def test_username_validation_invalid_length(self):
        """测试无效的用户名验证 - 长度不符合要求"""
        user = User()
        with pytest.raises(ValueError, match="用户名长度必须在3-50个字符之间"):
            user.validate_username("username", "ab")
        with pytest.raises(ValueError, match="用户名长度必须在3-50个字符之间"):
            user.validate_username("username", "a" * 51)

    def test_username_validation_invalid_characters(self):
        """测试无效的用户名验证 - 非法字符"""
        user = User()
        with pytest.raises(ValueError, match="用户名只能包含字母、数字和下划线"):
            user.validate_username("username", "test-user")
            user.validate_username("username", "test@user")
            user.validate_username("username", "test user")

    def test_username_validation_reserved_words(self):
        """测试无效的用户名验证 - 保留字"""
        user = User()
        with pytest.raises(ValueError, match="用户名不能使用保留字"):
            user.validate_username("username", "admin")
        with pytest.raises(ValueError, match="用户名不能使用保留字"):
            user.validate_username("username", "ROOT")
        with pytest.raises(ValueError, match="用户名不能使用保留字"):
            user.validate_username("username", "SYSTEM")

    def test_username_validation_repeated_chars(self):
        """测试无效的用户名验证 - 连续相同字符"""
        user = User()
        with pytest.raises(ValueError, match="用户名不能包含连续3个以上相同字符"):
            user.validate_username("username", "aaaatest")
        with pytest.raises(ValueError, match="用户名不能包含连续3个以上相同字符"):
            user.validate_username("username", "test1111")

    def test_email_validation_valid(self):
        """测试有效的邮箱验证"""
        user = User()
        assert user.validate_email("email", "test@example.com") == "test@example.com"
        assert user.validate_email("email", "USER@DOMAIN.COM") == "user@domain.com"
        assert (
            user.validate_email("email", "test.user+tag@example.co.uk")
            == "test.user+tag@example.co.uk"
        )

    def test_email_validation_invalid(self):
        """测试无效的邮箱验证"""
        user = User()
        with pytest.raises(ValueError, match="邮箱不能为空"):
            user.validate_email("email", "")

        with pytest.raises(ValueError, match="邮箱格式不正确"):
            user.validate_email("email", "invalid-email")
            user.validate_email("email", "test@")
            user.validate_email("email", "@example.com")

    def test_phone_validation_valid(self):
        """测试有效的手机号验证"""
        user = User()
        assert user.validate_phone("phone", "13800138000") == "13800138000"
        assert user.validate_phone("phone", "13912345678") == "13912345678"
        assert user.validate_phone("phone", None) is None

    def test_phone_validation_invalid(self):
        """测试无效的手机号验证"""
        user = User()
        with pytest.raises(ValueError, match="手机号格式不正确"):
            user.validate_phone("phone", "1234567890")
            user.validate_phone("phone", "1380013800")
            user.validate_phone("phone", "23800138000")

    def test_is_active_property(self):
        """测试is_active属性"""
        user = User()
        user.status = UserStatus.ACTIVE
        assert user.is_active is True

        user.status = UserStatus.INACTIVE
        assert user.is_active is False

        user.status = UserStatus.SUSPENDED
        assert user.is_active is False

        user.status = UserStatus.BANNED
        assert user.is_active is False

        user.status = UserStatus.PENDING
        assert user.is_active is False

    def test_display_name_property(self):
        """测试display_name属性"""
        user = User()
        user.username = "testuser"
        user.nickname = None
        assert user.display_name == "testuser"

        user.nickname = "Test User"
        assert user.display_name == "Test User"

    def test_to_dict_method(self):
        """测试to_dict方法"""
        user = User()
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.nickname = "Test User"
        user.avatar = "avatar.jpg"
        user.phone = "13800138000"
        user.bio = "Test bio"
        user.status = UserStatus.ACTIVE
        user.email_verified = True
        user.phone_verified = False
        user.last_login_time = datetime(2023, 1, 1, 12, 0, 0)
        user.last_login_ip = "192.168.1.1"
        user.login_count = 10
        user.created_at = datetime(2023, 1, 1, 0, 0, 0)
        user.updated_at = datetime(2023, 1, 1, 0, 0, 0)

        result = user.to_dict()

        assert result["id"] == 1
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert result["nickname"] == "Test User"
        assert result["avatar"] == "avatar.jpg"
        assert result["phone"] == "13800138000"
        assert result["bio"] == "Test bio"
        assert result["status"] == "active"
        assert result["email_verified"] is True
        assert result["phone_verified"] is False
        assert result["last_login_time"] == "2023-01-01T12:00:00"
        assert result["last_login_ip"] == "192.168.1.1"
        assert result["login_count"] == 10
        assert result["created_at"] == "2023-01-01T00:00:00"
        assert result["updated_at"] == "2023-01-01T00:00:00"
        assert result["roles"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# AI_DONE: coder1 @2026-01-29
