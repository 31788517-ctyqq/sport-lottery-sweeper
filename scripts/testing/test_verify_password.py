#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_verify_password():
    # 使用后端服务中的verify_password函数
    from backend.core.security import verify_password
    
    password = "admin123"
    password_hash = "$2b$12$Qe08aiiYwt4obrdW2YG93ujmJCwJFY/CCd.XcgcjizRxYr88GQMD."
    
    is_valid = verify_password(password, password_hash)
    print(f"密码: {password}")
    print(f"哈希: {password_hash}")
    print(f"验证结果: {is_valid}")
    
    # 测试错误密码
    wrong_password = "wrongpassword"
    is_invalid = verify_password(wrong_password, password_hash)
    print(f"错误密码: {wrong_password}")
    print(f"验证结果: {is_invalid}")

if __name__ == "__main__":
    test_verify_password()