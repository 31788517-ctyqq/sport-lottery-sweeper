import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

# 查询前台用户数量
cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'regular_user'")
count = cursor.fetchone()[0]
print(f"前台用户数量: {count}")

# 查询前几个用户的详细信息
cursor.execute("""
    SELECT username, email, role, status, notification_preferences, config 
    FROM users 
    WHERE role = 'regular_user' 
    LIMIT 3
""")
users = cursor.fetchall()

print("\n前3个用户的详细信息:")
for user in users:
    username, email, role, status, notification_prefs, config = user
    print(f"用户名: {username}")
    print(f"邮箱: {email}")
    print(f"角色: {role}")
    print(f"状态: {status}")
    print(f"通知偏好: {notification_prefs}")
    print(f"配置: {config}")
    print("-" * 40)

conn.close()