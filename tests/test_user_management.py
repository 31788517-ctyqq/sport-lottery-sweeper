#!/usr/bin/env python3
"""
用户管理功能测试用例
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import jwt
import os

os.environ.setdefault("DATABASE_PATH", os.path.abspath("./test.db"))

from backend.main import app
from backend.database import get_db, Base as LegacyBase
from backend.models.base import Base as ModelsBase
from backend.models.log_entry import LogEntry
from backend.models.user import User, UserStatus
from backend.models.admin_user import AdminUser, AdminRoleEnum, AdminStatusEnum
from backend.core.security import get_password_hash
from backend.config import settings

# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_db():
    """创建测试数据库"""
    ModelsBase.metadata.create_all(bind=engine)
    LegacyBase.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        ModelsBase.metadata.drop_all(bind=engine)
        LegacyBase.metadata.drop_all(bind=engine)
        engine.dispose()
        if os.path.exists("./test.db"):
            os.remove("./test.db")

@pytest.fixture(scope="function")
def client(test_db):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.rollback()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(test_db):
    """创建测试用户"""
    test_db.rollback()
    existing_user = test_db.query(User).filter(User.username == "testuser").first()
    if existing_user:
        return existing_user
    hashed_password = get_password_hash("testpassword123")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
        nickname="Test User",
        status=UserStatus.ACTIVE,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def test_admin_user(test_db):
    """创建测试管理员用户"""
    test_db.rollback()
    existing_admin = test_db.query(AdminUser).filter(AdminUser.username == "admin").first()
    if existing_admin:
        return existing_admin
    hashed_password = get_password_hash("adminpassword123")
    admin_user = AdminUser(
        username="admin",
        email="admin@example.com",
        password_hash=hashed_password,
        real_name="Admin User",
        role=AdminRoleEnum.ADMIN,
        status=AdminStatusEnum.ACTIVE,
    )
    test_db.add(admin_user)
    test_db.commit()
    test_db.refresh(admin_user)
    return admin_user

@pytest.fixture
def auth_headers(test_user):
    """生成认证头部"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": test_user.username,
        "user_id": test_user.id,
        "username": test_user.username,
        "role": "user",
    }
    expire = datetime.utcnow() + access_token_expires
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return {"Authorization": f"Bearer {encoded_jwt}"}

class TestUserAuthentication:
    """用户认证相关测试"""
    
    def test_user_login_success(self, client, test_admin_user):
        """测试用户登录成功"""
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "adminpassword123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert "expires_in" in data["data"]
        
    def test_user_login_invalid_credentials(self, client):
        """测试无效凭据登录"""
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        
    def test_user_login_inactive_user(self, client, test_db):
        """测试非活跃用户登录"""
        # 创建非活跃用户
        hashed_password = get_password_hash("inactivepass")
        inactive_user = AdminUser(
            username="inactive",
            email="inactive@example.com",
            password_hash=hashed_password,
            real_name="Inactive User",
            role=AdminRoleEnum.ADMIN,
            status=AdminStatusEnum.INACTIVE
        )
        test_db.add(inactive_user)
        test_db.commit()
        
        response = client.post("/api/v1/auth/login", json={
            "username": "inactive",
            "password": "inactivepass"
        })
        assert response.status_code == 401
        
    def test_token_refresh_success(self, client, test_admin_user):
        """测试令牌刷新成功"""
        # 先登录获取refresh token
        login_response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "adminpassword123"
        })
        refresh_token = login_response.json()["data"]["refresh_token"]
        
        # 刷新令牌
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

class TestUserProfileManagement:
    """用户个人资料管理测试"""
    
    def test_get_profile_success(self, client, auth_headers, test_user):
        """测试获取个人资料成功"""
        response = client.get("/api/v1/admin/users/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        
    def test_update_profile_success(self, client, auth_headers, test_user):
        """测试更新个人资料成功"""
        update_data = {
            "nickname": "Updated Nickname",
            "bio": "Updated bio",
            "gender": "male"
        }
        response = client.put("/api/v1/admin/users/profile", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["nickname"] == "Updated Nickname"
        assert data["bio"] == "Updated bio"
        
    def test_update_profile_email_conflict(self, client, auth_headers, test_user, test_db):
        """测试更新邮箱冲突"""
        # 创建另一个用户
        test_db.rollback()
        other_user = test_db.query(User).filter(User.username == "otheruser").first()
        if not other_user:
            other_user = User(
                username="otheruser",
                email="other@example.com",
                hashed_password=get_password_hash("otherpass"),
                status=UserStatus.ACTIVE,
            )
            test_db.add(other_user)
            test_db.commit()
        
        # 尝试更新为已存在的邮箱
        update_data = {"email": "other@example.com"}
        response = client.put("/api/v1/admin/users/profile", json=update_data, headers=auth_headers)
        assert response.status_code == 409
        
    def test_change_password_success(self, client, auth_headers, test_user):
        """测试修改密码成功"""
        form_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        response = client.put("/api/v1/admin/users/profile/password", data=form_data, headers=auth_headers)
        assert response.status_code == 200
        
    def test_change_password_mismatch(self, client, auth_headers, test_user):
        """测试新密码不匹配"""
        form_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123",
            "confirm_password": "differentpassword"
        }
        response = client.put("/api/v1/admin/users/profile/password", data=form_data, headers=auth_headers)
        assert response.status_code == 400

class TestAvatarUpload:
    """头像上传测试"""
    
    def test_avatar_upload_success(self, client, auth_headers, test_user):
        """测试头像上传成功"""
        # 创建一个简单的PNG文件用于测试
        import io
        from PIL import Image
        
        img = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        files = {"avatar": ("test_avatar.png", img_byte_arr, "image/png")}
        response = client.post("/api/v1/admin/users/profile/avatar", files=files, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "avatar_url" in data
        assert data["message"] == "头像上传成功"

class TestUserActivityLogging:
    """用户活动日志测试"""
    
    def test_login_activity_logged(self, client, test_admin_user, test_db):
        """测试登录活动被记录"""
        initial_log_count = test_db.query(LogEntry).count()
        
        client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "adminpassword123"
        })
        
        final_log_count = test_db.query(LogEntry).count()
        assert final_log_count > initial_log_count
        
        # 检查日志内容
        latest_log = test_db.query(LogEntry).order_by(LogEntry.id.desc()).first()
        assert latest_log.module == "auth"
        assert "登录成功" in latest_log.message
        
    def test_profile_update_logged(self, client, auth_headers, test_user, test_db):
        """测试个人资料更新被记录"""
        initial_log_count = test_db.query(LogEntry).count()
        
        update_data = {"nickname": "Logged Update"}
        client.put("/api/v1/admin/users/profile", json=update_data, headers=auth_headers)
        
        final_log_count = test_db.query(LogEntry).count()
        assert final_log_count > initial_log_count
        
        # 检查日志内容
        latest_log = test_db.query(LogEntry).order_by(LogEntry.id.desc()).first()
        assert latest_log.module == "user_profile"
        assert "更新了个人资料" in latest_log.message

if __name__ == "__main__":
    pytest.main([__file__, "-v"])