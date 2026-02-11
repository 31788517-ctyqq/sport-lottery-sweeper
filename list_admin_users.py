#!/usr/bin/env python3
import sqlite3

def list_admin_users():
    conn = sqlite3.connect('sport_lottery.db')
    conn.row_factory = sqlite3.Row  # 启用列名访问
    cursor = conn.cursor()
    
    # 获取所有列
    cursor.execute('PRAGMA table_info(admin_users);')
    columns = cursor.fetchall()
    print("列信息:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # 获取所有用户
    cursor.execute('SELECT * FROM admin_users;')
    users = cursor.fetchall()
    
    print(f"\n总共 {len(users)} 个管理员用户:")
    for user in users:
        print(f"\n用户ID: {user['id']}")
        print(f"  用户名: {user['username']}")
        print(f"  邮箱: {user['email']}")
        print(f"  角色: {user.get('role', 'N/A')}")
        print(f"  状态: {user.get('status', 'N/A')}")
        print(f"  是否活跃: {user.get('is_active', 'N/A')}")
        print(f"  是否超级用户: {user.get('is_superuser', 'N/A')}")
        print(f"  密码哈希: {user['password_hash'][:30]}..." if user.get('password_hash') else "  无密码哈希")
        print(f"  创建时间: {user.get('created_at', 'N/A')}")
        print(f"  最后登录: {user.get('last_login_at', 'N/A')}")
    
    conn.close()
    
    # 尝试使用 authenticate_user
    print("\n\n尝试使用 authenticate_user 函数:")
    try:
        from backend.database_utils import authenticate_user
        for user in users:
            username = user['username']
            print(f"\n测试用户 '{username}':")
            result = authenticate_user(username, "wrong_password")
            print(f"  错误密码: {result}")
            # 不测试正确密码，因为我们不知道
    except Exception as e:
        print(f"导入错误: {e}")

if __name__ == "__main__":
    list_admin_users()