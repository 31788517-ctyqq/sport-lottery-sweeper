#!/usr/bin/env python3
"""
测试密码验证
"""
import sys
sys.path.insert(0, '.')

from backend.core.security import verify_password
from backend.core.database import SessionLocal
from backend.models.admin_user import AdminUser

def test_password():
    print("=== 测试密码验证 ===")
    session = SessionLocal()
    try:
        admin = session.query(AdminUser).filter(AdminUser.username == 'admin').first()
        if not admin:
            print("未找到admin用户")
            return
        
        print(f"admin密码哈希: {admin.password_hash}")
        print(f"哈希长度: {len(admin.password_hash)}")
        
        # 测试密码
        test_passwords = [
            'admin123',  # 预期密码
            'wrong',
            ''
        ]
        
        for pwd in test_passwords:
            result = verify_password(pwd, admin.password_hash)
            print(f"密码 '{pwd}' 验证结果: {result}")
            
        # 直接从数据库查询哈希
        import sqlite3
        conn = sqlite3.connect('data/sport_lottery.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM admin_users WHERE username='admin'")
        row = cursor.fetchone()
        if row:
            db_hash = row[0]
            print(f"\n直接数据库哈希: {db_hash}")
            print(f"与模型哈希相同: {db_hash == admin.password_hash}")
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    test_password()