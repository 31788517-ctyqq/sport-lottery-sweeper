import sqlite3
import hashlib

DB_PATH = 'data/sport_lottery.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 检查 users 表中的 admin 用户
cursor.execute("SELECT username, password_hash FROM users WHERE username = 'admin' OR username LIKE '%admin%'")
admin_users = cursor.fetchall()

print("users 表中的管理员用户:")
for username, password_hash in admin_users:
    print(f"  用户名: {username}")
    print(f"  密码哈希: {password_hash}")
    print(f"  哈希长度: {len(password_hash)}")
    
    # 检查是否是 SHA256 哈希 (64 字符十六进制)
    if len(password_hash) == 64 and all(c in '0123456789abcdef' for c in password_hash.lower()):
        print(f"  哈希类型: SHA256")
    else:
        print(f"  哈希类型: 未知")
    print()

# 检查 admin_users 表
cursor.execute("SELECT username, password_hash FROM admin_users")
all_admin_users = cursor.fetchall()

print("admin_users 表中的所有用户:")
for username, password_hash in all_admin_users:
    print(f"  用户名: {username}")
    print(f"  密码哈希: {password_hash[:50]}..." if password_hash and len(password_hash) > 50 else f"  密码哈希: {password_hash}")
    print(f"  哈希长度: {len(password_hash) if password_hash else 0}")
    print()

conn.close()