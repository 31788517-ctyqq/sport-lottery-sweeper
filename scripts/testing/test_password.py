#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_password():
    from backend.core.security import get_password_hash, verify_password
    
    # 测试密码哈希
    password = "admin123"
    hashed = get_password_hash(password)
    print(f"原始密码: {password}")
    print(f"哈希密码: {hashed}")
    
    # 测试验证
    is_valid = verify_password(password, hashed)
    print(f"验证结果: {is_valid}")
    
    # 测试错误密码
    is_invalid = verify_password("wrongpassword", hashed)
    print(f"错误密码验证结果: {is_invalid}")

if __name__ == "__main__":
    test_password()