#!/usr/bin/env python3
import sqlite3
import os

print("检查数据库...")
db_path = "data/sport_lottery.db"
if not os.path.exists(db_path):
    print(f"数据库文件不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()
print(f"表数量: {len(tables)}")
for t in tables:
    print(f"  {t[0]}")

# 检查admin_users表
print("\n检查admin_users表:")
try:
    cursor.execute("SELECT COUNT(*) FROM admin_users")
    count = cursor.fetchone()[0]
    print(f"  行数: {count}")
    if count > 0:
        cursor.execute("SELECT username, email, password_hash, is_superuser, is_active FROM admin_users LIMIT 10")
        rows = cursor.fetchall()
        print("  用户列表:")
        for r in rows:
            print(f"    用户名: {r[0]}, 邮箱: {r[1]}, 超级用户: {r[3]}, 活跃: {r[4]}")
            print(f"      密码哈希: {r[2][:30]}..." if r[2] else "      无密码哈希")
except Exception as e:
    print(f"  查询错误: {e}")

# 检查users表（前台用户）
print("\n检查users表:")
try:
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"  行数: {count}")
    if count > 0:
        cursor.execute("SELECT username, email, password_hash FROM users LIMIT 5")
        rows = cursor.fetchall()
        print("  用户列表:")
        for r in rows:
            print(f"    用户名: {r[0]}, 邮箱: {r[1]}")
except Exception as e:
    print(f"  查询错误: {e}")

conn.close()
print("\n检查完成")