#!/usr/bin/env python3
import sqlite3

def list_admin_users():
    conn = sqlite3.connect('sport_lottery.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM admin_users;')
    users = cursor.fetchall()
    
    print(f"总共 {len(users)} 个管理员用户:")
    for user in users:
        print(f"\n用户ID: {user['id']}")
        print(f"  用户名: {user['username']}")
        print(f"  邮箱: {user['email']}")
        print(f"  角色: {user['role']}")
        print(f"  状态: {user['status']}")
        print(f"  密码哈希: {user['password_hash'][:30]}..." if user['password_hash'] else "  无密码哈希")
        print(f"  登录次数: {user['login_count']}")
        print(f"  最后登录: {user.get('last_login_at', 'N/A')}")
        print(f"  是否已验证: {user.get('is_verified', 'N/A')}")
    
    conn.close()
    
    # 尝试猜测密码
    print("\n\n尝试猜测密码:")
    common_passwords = ['admin123', 'Admin@123', 'admin', 'password', '123456', 'admin123456', 'Admin123456', 'SuperAdmin@123456']
    
    try:
        from backend.database_utils import verify_password
        for user in users:
            username = user['username']
            password_hash = user['password_hash']
            print(f"\n用户 '{username}':")
            for pwd in common_passwords:
                if verify_password(pwd, password_hash):
                    print(f"  找到密码: '{pwd}'")
                    break
            else:
                print(f"  未匹配常见密码")
    except Exception as e:
        print(f"导入错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_admin_users()