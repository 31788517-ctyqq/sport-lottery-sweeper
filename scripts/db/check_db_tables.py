#!/usr/bin/env python3
import sqlite3
import sys

def check_database():
    db_path = "sport_lottery.db"
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("=== 数据库检查 ===")
        
        # 1. 检查所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        print(f"\n1. 数据库中有 {len(tables)} 个表:")
        for table in tables:
            print(f"   - {table['name']}")
        
        # 2. 检查users表
        print("\n2. users表:")
        cursor.execute("SELECT COUNT(*) as count FROM users;")
        user_count = cursor.fetchone()['count']
        print(f"   记录数: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT id, username, email, role, user_type, status FROM users LIMIT 5;")
            users = cursor.fetchall()
            for user in users:
                print(f"     ID: {user['id']}, 用户名: {user['username']}, 邮箱: {user['email']}, 角色: {user['role']}, 类型: {user['user_type']}, 状态: {user['status']}")
        
        # 3. 检查admin_users表
        print("\n3. admin_users表:")
        cursor.execute("SELECT COUNT(*) as count FROM admin_users;")
        admin_count = cursor.fetchone()['count']
        print(f"   记录数: {admin_count}")
        
        if admin_count > 0:
            cursor.execute("SELECT id, username, email, role, status, real_name FROM admin_users LIMIT 5;")
            admins = cursor.fetchall()
            for admin in admins:
                print(f"     ID: {admin['id']}, 用户名: {admin['username']}, 邮箱: {admin['email']}, 角色: {admin['role']}, 状态: {admin['status']}, 姓名: {admin['real_name']}")
        
        # 4. 检查是否有admin用户
        print("\n4. 用户检查:")
        cursor.execute("SELECT username, role FROM users WHERE username='admin' OR username LIKE '%admin%';")
        admin_users = cursor.fetchall()
        if admin_users:
            print("   在users表中找到的admin用户:")
            for user in admin_users:
                print(f"     用户名: {user['username']}, 角色: {user['role']}")
        else:
            print("   在users表中未找到admin用户")
            
        cursor.execute("SELECT username, role FROM admin_users WHERE username='admin' OR username LIKE '%admin%';")
        admin_admins = cursor.fetchall()
        if admin_admins:
            print("   在admin_users表中找到的admin用户:")
            for admin in admin_admins:
                print(f"     用户名: {admin['username']}, 角色: {admin['role']}")
        else:
            print("   在admin_users表中未找到admin用户")
        
        conn.close()
        print("\n=== 检查完成 ===")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    check_database()