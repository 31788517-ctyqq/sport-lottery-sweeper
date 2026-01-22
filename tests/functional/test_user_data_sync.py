"""
测试用户管理数据 - 同步版本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db, engine
from backend.models.admin_user import AdminUser
from backend.models.user import User
from backend.models.base import Base
from sqlalchemy import select, func, text


def test_user_data():
    """测试用户数据"""
    print("=== 测试用户管理数据 ===\n")

    # 创建所有表
    print("1. 创建数据库表...")
    try:
        Base.metadata.create_all(bind=engine)
        print("   ✅ 表创建成功\n")
    except Exception as e:
        print(f"   ❌ 表创建失败: {e}\n")
        return

    db = get_db().__next__()

    try:
        # 查询后台用户
        print("2. 查询后台用户...")
        result = db.execute(select(AdminUser))
        admin_users = result.scalars().all()
        print(f"   后台用户总数: {len(admin_users)}")

        if admin_users:
            # 按角色统计
            print("\n   按角色统计:")
            for role in ['SUPER_ADMIN', 'ADMIN', 'MODERATOR', 'AUDITOR', 'OPERATOR']:
                result = db.execute(
                    select(func.count(AdminUser.id)).where(AdminUser.role == role)
                )
                count = result.scalar()
                print(f"   - {role}: {count}人")

            # 按状态统计
            print("\n   按状态统计:")
            for status in ['ACTIVE', 'INACTIVE', 'SUSPENDED', 'LOCKED']:
                result = db.execute(
                    select(func.count(AdminUser.id)).where(AdminUser.status == status)
                )
                count = result.scalar()
                print(f"   - {status}: {count}人")

            # 显示前几个用户
            print("\n   后台用户示例:")
            result = db.execute(select(AdminUser).limit(3))
            for user in result.scalars():
                print(f"   - {user.username} ({user.role}, {user.status})")
        else:
            print("   ⚠️  没有找到后台用户数据")

        print("\n3. 查询前台用户...")
        result = db.execute(select(User))
        frontend_users = result.scalars().all()
        print(f"   前台用户总数: {len(frontend_users)}")

        if frontend_users:
            # 按用户类型统计
            print("\n   按用户类型统计:")
            for user_type in ['NORMAL', 'PREMIUM', 'ANALYST']:
                result = db.execute(
                    select(func.count(User.id)).where(User.user_type == user_type)
                )
                count = result.scalar()
                print(f"   - {user_type}: {count}人")

            # 显示前几个用户
            print("\n   前台用户示例:")
            result = db.execute(select(User).limit(3))
            for user in result.scalars():
                print(f"   - {user.username} ({user.user_type}, {user.status})")
        else:
            print("   ⚠️  没有找到前台用户数据")

        print("\n4. 检查模拟数据标识...")
        # 检查是否有包含标识符的数据
        result = db.execute(select(AdminUser).where(AdminUser.username.like('%mock_data_2026_01_19%')))
        mock_admin_count = len(result.scalars().all())
        print(f"   后台模拟用户数: {mock_admin_count}")

        result = db.execute(select(User).where(User.username.like('%mock_data_2026_01_19%')))
        mock_user_count = len(result.scalars().all())
        print(f"   前台模拟用户数: {mock_user_count}")

        print("\n✅ 用户数据测试完成!")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_user_data()
