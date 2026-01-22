"""
测试密码验证脚本
"""
import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backend.core.security import verify_password

def test_password():
    plain_password = "admin123"
    hashed_password = "$2b$12$KY67JnKViXqWX1x0WJ0M1.GOl1Dc4AlFS2PF3Fkj6oZMgv5zosVj."
    
    result = verify_password(plain_password, hashed_password)
    print(f"Password verification result: {result}")
    
    # 测试错误密码
    wrong_password = "wrongpass"
    wrong_result = verify_password(wrong_password, hashed_password)
    print(f"Wrong password verification result: {wrong_result}")

if __name__ == "__main__":
    test_password()