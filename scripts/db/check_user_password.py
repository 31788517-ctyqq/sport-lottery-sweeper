#!/usr/bin/env python3
import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir
sys.path.insert(0, str(project_root))

try:
    from backend.core.security import verify_password, get_password_hash
except ImportError:
    print("无法导入security模块，尝试直接验证...")
    verify_password = None

def check_user():
    db_path = "data/sport_lottery.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=== 检查用户密码 ===")
    
    # 1. 检查admin用户在users表中的密码哈希
    cursor.execute("SELECT username, email, password_hash, role, user_type FROM users WHERE username='admin';")
    user = cursor.fetchone()
    
    if user:
        print(f"\n1. users表中的admin用户:")
        print(f"   用户名: {user['username']}")
        print(f"   邮箱: {user['email']}")
        print(f"   密码哈希: {user['password_hash']}")
        print(f"   角色: {user['role']}")
        print(f"   用户类型: {user['user_type']}")
        
        # 尝试验证密码
        test_passwords = ["admin123", "Admin123!@#", "password", "admin"]
        
        if verify_password:
            print("\n   密码验证测试:")
            for pwd in test_passwords:
                try:
                    if verify_password(pwd, user['password_hash']):
                        print(f"     - '{pwd}': 匹配!")
                    else:
                        print(f"     - '{pwd}': 不匹配")
                except Exception as e:
                    print(f"     - '{pwd}': 验证错误: {e}")
        else:
            print("\n   无法验证密码（security模块不可用）")
            
        # 计算新哈希
        print("\n   计算新密码哈希:")
        for pwd in test_passwords:
            try:
                new_hash = get_password_hash(pwd)
                print(f"     - '{pwd}': {new_hash}")
            except:
                pass
    else:
        print("\n1. users表中未找到admin用户")
    
    # 2. 检查admin_users表
    print("\n2. admin_users表:")
    cursor.execute("SELECT COUNT(*) as count FROM admin_users;")
    admin_count = cursor.fetchone()['count']
    print(f"   记录数: {admin_count}")
    
    if admin_count > 0:
        cursor.execute("SELECT username, email, password_hash, role FROM admin_users;")
        admins = cursor.fetchall()
        for admin in admins:
            print(f"   用户名: {admin['username']}, 邮箱: {admin['email']}, 角色: {admin['role']}")
    
    # 3. 尝试创建admin_users记录
    print("\n3. 测试创建admin_users记录:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_users';")
    admin_table_exists = cursor.fetchone()
    
    if admin_table_exists:
        print("   admin_users表存在")
        # 显示表结构
        cursor.execute("PRAGMA table_info(admin_users);")
        columns = cursor.fetchall()
        print("   表结构:")
        for col in columns:
            print(f"     - {col[1]} ({col[2]})")
    else:
        print("   admin_users表不存在")
    
    conn.close()
    print("\n=== 检查完成 ===")

if __name__ == "__main__":
    check_user()