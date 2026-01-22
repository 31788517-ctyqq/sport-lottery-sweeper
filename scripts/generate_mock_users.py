"""
生成用户管理系统的模拟数据
用于测试和演示后台用户管理功能
"""

import asyncio
import random
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from faker import Faker

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.models.admin_user import AdminUser, AdminOperationLog, AdminLoginLog, AdminRoleEnum, AdminStatusEnum
from backend.models.user import User, UserStatusEnum, UserTypeEnum, UserRoleEnum
from backend.core.auth import get_password_hash
from backend.database import SQLALCHEMY_DATABASE_URL

fake = Faker('zh_CN')

# 模拟数据标识，便于后续清理
MOCK_DATA_TAG = "mock_data_2026_01_19"


async def create_mock_admin_users(db_session):
    """创建后台管理用户模拟数据"""
    print("开始创建后台管理用户模拟数据...")
    
    # 超级管理员
    super_admin = AdminUser(
        username=f"sa_{MOCK_DATA_TAG}",
        email=f"sa_{MOCK_DATA_TAG}@example.com",
        password_hash=get_password_hash("SuperAdmin@123456"),
        real_name="超级管理员",
        role=AdminRoleEnum.SUPER_ADMIN,
        status=AdminStatusEnum.ACTIVE,
        is_verified=True,
        two_factor_enabled=True,
        login_count=0,
        failed_login_attempts=0,
        remarks="模拟超级管理员账户",
        created_by=None
    )
    db_session.add(super_admin)
    await db_session.commit()
    await db_session.refresh(super_admin)
    
    # 创建其他管理员
    admin_users = []
    roles = [AdminRoleEnum.ADMIN, AdminRoleEnum.MODERATOR, AdminRoleEnum.AUDITOR, AdminRoleEnum.OPERATOR]
    
    for i in range(10):
        role = random.choice(roles)
        status = random.choice(list(AdminStatusEnum))
        
        admin_user = AdminUser(
            username=f"admin_{i}_{MOCK_DATA_TAG}",
            email=f"admin{i}_{MOCK_DATA_TAG}@example.com",
            password_hash=get_password_hash("Admin@123456"),
            real_name=fake.name(),
            phone=fake.phone_number(),
            department=random.choice(["技术部", "运营部", "客服部", "审计部"]),
            position=random.choice(["主管", "专员", "经理", "总监"]),
            role=role,
            status=status,
            is_verified=True,
            two_factor_enabled=random.choice([True, False]),
            login_count=random.randint(0, 100),
            failed_login_attempts=random.randint(0, 5),
            remarks=f"模拟{role.value}账户",
            created_by=super_admin.id
        )
        db_session.add(admin_user)
        admin_users.append(admin_user)
    
    await db_session.commit()
    
    # 创建操作日志
    print("开始创建后台操作日志模拟数据...")
    actions = ["create", "read", "update", "delete", "login", "logout"]
    resources = ["user", "match", "intelligence", "config", "log"]
    
    for admin in admin_users:
        for _ in range(random.randint(5, 20)):
            log_entry = AdminOperationLog(
                admin_id=admin.id,
                action=random.choice(actions),
                resource_type=random.choice(resources),
                resource_id=str(random.randint(1, 100)),
                resource_name=fake.word(),
                method=random.choice(["GET", "POST", "PUT", "DELETE"]),
                path=f"/api/v1/admin/{random.choice(resources)}/{random.randint(1, 100)}",
                status_code=random.choice([200, 201, 400, 403, 404, 500]),
                ip_address=fake.ipv4(),
                created_at=fake.date_time_between(start_date="-30d", end_date="now"),
                duration_ms=random.randint(10, 500)
            )
            db_session.add(log_entry)
    
    await db_session.commit()
    
    # 创建登录日志
    print("开始创建后台登录日志模拟数据...")
    for admin in admin_users:
        for _ in range(random.randint(3, 15)):
            login_log = AdminLoginLog(
                admin_id=admin.id,
                login_at=fake.date_time_between(start_date="-30d", end_date="now"),
                login_ip=fake.ipv4(),
                user_agent=fake.user_agent(),
                success=random.choice([True, False]),
                failure_reason=None if random.choice([True, False]) else "Invalid credentials",
                device_type=random.choice(["desktop", "mobile", "tablet"]),
                os=random.choice(["Windows", "MacOS", "Linux", "iOS", "Android"]),
                browser=random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
                two_factor_used=random.choice([True, False]),
                ip_whitelisted=random.choice([True, False])
            )
            db_session.add(login_log)
    
    await db_session.commit()
    print(f"成功创建11个后台管理用户，{len(admin_users)*15}条操作日志，{len(admin_users)*10}条登录日志")


async def create_mock_frontend_users(db_session):
    """创建前台用户模拟数据"""
    print("开始创建前台用户模拟数据...")
    
    user_types = [UserTypeEnum.NORMAL, UserTypeEnum.PREMIUM, UserTypeEnum.ANALYST]
    statuses = [UserStatusEnum.ACTIVE, UserStatusEnum.INACTIVE, UserStatusEnum.SUSPENDED, UserStatusEnum.BANNED]
    
    for i in range(50):
        user_type = random.choice(user_types)
        status = random.choice(statuses)
        
        user = User(
            username=f"user_{i}_{MOCK_DATA_TAG}",
            email=f"user{i}_{MOCK_DATA_TAG}@example.com",
            password_hash=get_password_hash("User@123456"),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            nickname=fake.user_name(),
            phone=fake.phone_number(),
            country="中国",
            city=fake.city(),
            role=UserRoleEnum.REGULAR_USER,
            status=status,
            user_type=user_type,
            login_count=random.randint(0, 100),
            last_login_at=fake.date_time_between(start_date="-30d", end_date="now"),
            is_verified=random.choice([True, False]),
            followers_count=random.randint(0, 1000),
            following_count=random.randint(0, 500),
            remarks=f"模拟{user_type.value}用户",
        )
        db_session.add(user)
    
    await db_session.commit()
    print(f"成功创建50个前台用户")


async def cleanup_mock_data(db_session):
    """清理模拟数据"""
    print("开始清理模拟数据...")
    
    # 删除后台用户及其相关数据
    admin_users = await db_session.execute(
        AdminUser.__table__.select().where(AdminUser.username.like(f"%{MOCK_DATA_TAG}%"))
    )
    admin_ids = [row.id for row in admin_users.scalars()]
    
    if admin_ids:
        # 删除相关的操作日志
        await db_session.execute(
            AdminOperationLog.__table__.delete().where(
                AdminOperationLog.admin_id.in_(admin_ids)
            )
        )
        
        # 删除相关的登录日志
        await db_session.execute(
            AdminLoginLog.__table__.delete().where(
                AdminLoginLog.admin_id.in_(admin_ids)
            )
        )
        
        # 删除管理员本身
        await db_session.execute(
            AdminUser.__table__.delete().where(
                AdminUser.username.like(f"%{MOCK_DATA_TAG}%")
            )
        )
    
    # 删除前台用户
    await db_session.execute(
        User.__table__.delete().where(
            User.username.like(f"%{MOCK_DATA_TAG}%")
        )
    )
    
    await db_session.commit()
    print("模拟数据清理完成")


async def main(action="create"):
    """主函数，执行创建或清理操作"""
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db_session:
        if action == "create":
            await cleanup_mock_data(db_session)  # 先清理旧的模拟数据
            await create_mock_admin_users(db_session)
            await create_mock_frontend_users(db_session)
            print("\n所有模拟数据创建完成！")
            print(f"标识符: {MOCK_DATA_TAG}")
            print("如需清理数据，可运行: python generate_mock_users.py cleanup")
        elif action == "cleanup":
            await cleanup_mock_data(db_session)
            print("\n模拟数据清理完成！")
        else:
            print("无效操作，请使用 'create' 或 'cleanup'")


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "create"
    asyncio.run(main(action))