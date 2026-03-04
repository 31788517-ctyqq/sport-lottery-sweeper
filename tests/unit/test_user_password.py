import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backend.core.security import verify_password

def test_user_password():
    """测试用户密码验证"""
    # 测试admin用户
    admin_password_hash = "$2b$12$KY67JnKViXqWX1x0WJ0M1.GOl1Dc4AlFS2PF3Fkj6oZMgv5zosVj."
    admin_plain_password = "admin123"
    
    result = verify_password(admin_plain_password, admin_password_hash)
    print(f"Admin用户密码验证结果: {result}")
    
    # 测试其他用户（看起来是MD5）
    other_password_hash = "4cd7108afdef44e88326d6d269f33268"
    other_plain_password = "password123"  # 假设的密码
    
    try:
        other_result = verify_password(other_plain_password, other_password_hash)
        print(f"其他用户密码验证结果: {other_result}")
    except Exception as e:
        print(f"其他用户密码验证出错: {e}")

if __name__ == "__main__":
    test_user_password()