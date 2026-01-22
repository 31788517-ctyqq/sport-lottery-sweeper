import sqlite3
import os

# 连接到数据库
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sport_lottery.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 检查后台用户数量
    cursor.execute("SELECT COUNT(*) FROM admin_users WHERE username LIKE '%mock_data_2026_01_19%'")
    admin_count = cursor.fetchone()[0]
    print(f"后台用户数量: {admin_count}")

    # 检查前台用户数量
    cursor.execute("SELECT COUNT(*) FROM users WHERE username LIKE '%mock_data_2026_01_19%'")
    user_count = cursor.fetchone()[0]
    print(f"前台用户数量: {user_count}")

    # 检查是否有其他表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"数据库中存在的表: {[table[0] for table in tables]}")

    # 显示一些示例数据
    if admin_count > 0:
        cursor.execute("SELECT id, username, real_name, role, status FROM admin_users WHERE username LIKE '%mock_data_2026_01_19%' LIMIT 5")
        sample_admins = cursor.fetchall()
        print("\n示例后台用户数据:")
        for admin in sample_admins:
            print(f"  ID: {admin[0]}, 用户名: {admin[1]}, 真实姓名: {admin[2]}, 角色: {admin[3]}, 状态: {admin[4]}")

    if user_count > 0:
        cursor.execute("SELECT id, username, nickname, user_type, status FROM users WHERE username LIKE '%mock_data_2026_01_19%' LIMIT 5")
        sample_users = cursor.fetchall()
        print("\n示例前台用户数据:")
        for user in sample_users:
            print(f"  ID: {user[0]}, 用户名: {user[1]}, 昵称: {user[2]}, 类型: {user[3]}, 状态: {user[4]}")

except Exception as e:
    print(f"查询数据库时出错: {e}")
finally:
    conn.close()