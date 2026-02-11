#!/usr/bin/env python3
"""
用户活动日志服务测试用例
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import os

from backend.database import Base
from backend.models.log_entry import LogEntry
from backend.models.user import User, UserStatus
from backend.services.user_activity_logger import UserActivityLogger
from backend.config import settings

# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_activity.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_db():
    """创建测试数据库"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_activity.db"):
        os.remove("./test_activity.db")

@pytest.fixture
def activity_logger(test_db):
    """创建用户活动日志记录器"""
    return UserActivityLogger(test_db)

class TestUserActivityLogger:
    """用户活动日志记录器测试"""
    
    def test_log_user_login_success(self, test_db, activity_logger):
        """测试记录成功登录事件"""
        initial_count = test_db.query(LogEntry).count()
        
        activity_logger.log_user_login(
            user_id=1,
            username="testuser",
            ip_address="192.168.1.1",
            user_agent="Test Agent",
            success=True
        )
        
        final_count = test_db.query(LogEntry).count()
        assert final_count == initial_count + 1
        
        log_entry = test_db.query(LogEntry).order_by(LogEntry.id.desc()).first()
        assert log_entry.level == "INFO"
        assert log_entry.module == "auth"
        assert "登录成功" in log_entry.message
        assert log_entry.user_id == 1
        assert log_entry.ip_address == "192.168.1.1"
        
        # 检查额外数据
        extra_data = json.loads(log_entry.extra_data)
        assert extra_data["event_type"] == "login"
        assert extra_data["success"] is True
        
    def test_log_user_login_failure(self, test_db, activity_logger):
        """测试记录失败登录事件"""
        activity_logger.log_user_login(
            user_id=0,
            username="unknown",
            ip_address="192.168.1.2",
            user_agent="Test Agent",
            success=False,
            failure_reason="用户不存在"
        )
        
        log_entry = test_db.query(LogEntry).order_by(LogEntry.id.desc()).first()
        assert log_entry.level == "WARN"
        assert "登录失败" in log_entry.message
        assert "用户不存在" in log_entry.message
        
    def test_log_profile_update(self, test_db, activity_logger):
        """测试记录个人资料更新事件"""
        updated_fields = {
            "nickname": "New Nickname",
            "email": "new@example.com",
            "bio": "New bio"
        }
        
        activity_logger.log_profile_update(
            user_id=1,
            username="testuser",
            updated_fields=updated_fields,
            ip_address="192.168.1.3"
        )
        
        log_entry = test_db.query(LogEntry).order_by(LogEntry.id.desc()).first()
        assert log_entry.level == "INFO"
        assert log_entry.module == "user_profile"
        assert "更新了个人资料" in log_entry.message
        assert "nickname" in log_entry.message
        assert "email" in log_entry.message
        assert "bio" not in log_entry.message  # bio字段应该被包含
        
        # 检查额外数据
        extra_data = json.loads(log_entry.extra_data)
        assert set(extra_data["updated_fields"]) == {"nickname", "email", "bio"}
        
    def test_log_profile_update_sensitive_fields_filtered(self, test_db, activity_logger):
        """测试敏感字段被过滤"""
        updated_fields = {
            "nickname": "Safe Field",
            "password": "secret123",
            "hashed_password": "hash123"
        }
        
        activity_logger.log_profile_update(
            user_id=1,
            username="testuser",
            updated_fields=updated_fields
        )
        
        log_entry = test_db.query(LogEntry).order_by(LogEntry.id.desc()).first()
        assert "password" not in log_entry.message
        assert "hashed_password" not in log_entry.message
        assert "nickname" in log_entry.message
        
    def test_log_password_change(self, test_db, activity_logger):
        """测试记录密码修改事件"""
        activity_logger.log_password_change(
            user_id=1,
            username="testuser",
            ip_address="192.168.1.4"
        )
        
        log_entry = test_db.query(LogEntry).order_by(LogEntry.id.desc()).first()
        assert log_entry.level == "INFO"
        assert log_entry.module == "user_profile"
        assert "修改了密码" in log_entry.message
        
    def test_log_avatar_upload(self, test_db, activity_logger):
        """测试记录头像上传事件"""
        activity_logger.log_avatar_upload(
            user_id=1,
            username="testuser",
            avatar_url="/uploads/avatars/test.jpg",
            ip_address="192.168.1.5"
        )
        
        log_entry = test_db.query(LogEntry).order_by(LogEntry.id.desc()).first()
        assert log_entry.level == "INFO"
        assert "上传了新头像" in log_entry.message
        
        extra_data = json.loads(log_entry.extra_data)
        assert extra_data["avatar_url"] == "/uploads/avatars/test.jpg"
        
    def test_log_permission_change(self, test_db, activity_logger):
        """测试记录权限变更事件"""
        activity_logger.log_permission_change(
            user_id=2,
            username="targetuser",
            old_role="operator",
            new_role="admin",
            changed_by_user_id=1,
            changed_by_username="adminuser",
            ip_address="192.168.1.6"
        )
        
        log_entry = test_db.query(LogEntry).order_by(LogEntry.id.desc()).first()
        assert log_entry.level == "WARN"  # 权限变更是重要事件
        assert "角色从 operator 变更为 admin" in log_entry.message
        assert "(由 adminuser 操作)" in log_entry.message
        
    def test_log_token_refresh(self, test_db, activity_logger):
        """测试记录令牌刷新事件"""
        activity_logger.log_token_refresh(
            user_id=1,
            username="testuser",
            ip_address="192.168.1.7"
        )
        
        log_entry = test_db.query(LogEntry).order_by(LogEntry.id.desc()).first()
        assert log_entry.level == "INFO"
        assert log_entry.module == "auth"
        assert "刷新了访问令牌" in log_entry.message
        
    def test_error_handling(self, test_db, activity_logger, monkeypatch):
        """测试错误处理"""
        # 模拟数据库错误
        def mock_add(*args, **kwargs):
            raise Exception("Database error")
        
        monkeypatch.setattr(test_db, 'add', mock_add)
        
        # 这个调用应该不会抛出异常（错误被内部捕获）
        activity_logger.log_user_login(
            user_id=1,
            username="testuser",
            success=True
        )
        # 如果没有异常抛出，说明错误处理正常工作

if __name__ == "__main__":
    pytest.main([__file__, "-v"])