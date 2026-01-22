import sqlite3
import bcrypt

conn = sqlite3.connect('sport_lottery.db')
c = conn.cursor()

# 检查表结构
c.execute("PRAGMA table_info(users)")
columns = c.fetchall()
print("users表结构:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# 检查所有用户
c.execute("SELECT id, username, email, role, password_hash, first_name, last_name FROM users")
users = c.fetchall()
print(f"\n共有 {len(users)} 个用户:")
for user in users:
    print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 角色: {user[3]}")
    print(f"    密码哈希: {user[4][:60]}...")
    print(f"    名: {user[5]}, 姓: {user[6]}")

conn.close()