"""
测试密码验证功能
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir
sys.path.insert(0, str(project_root))

import sqlite3
from backend.core.security import verify_password

def test_password_verification():
    """测试密码验证"""
    # 连接数据库
    conn = sqlite3.connect('data/sport_lottery.db')
    cursor = conn.cursor()
    
    try:
        # 获取管理员用户的密码哈希
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", ("admin",))
        result = cursor.fetchone()
        
        if not result:
            print("未找到管理员用户")
            return
        
        password_hash = result[0]
        print(f"数据库中的密码哈希: {password_hash}")
        
        # 测试不同的密码
        test_passwords = ["Admin123!@#", "admin123", "password", "123456"]
        
        for password in test_passwords:
            is_valid = verify_password(password, password_hash)
            print(f"密码 '{password}' 验证结果: {is_valid}")
            
    except Exception as e:
        print(f"测试密码验证时出错: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_password_verification()