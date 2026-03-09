import sqlite3

DB_PATH = 'data/sport_lottery.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 检查 admin 用户的详细信息
cursor.execute("""
    SELECT 
        id, username, email, role, status, 
        is_verified, is_active, user_type,
        login_count, last_login_at
    FROM users 
    WHERE username = 'admin'
""")
admin_row = cursor.fetchone()

if admin_row:
    print("Admin 用户详情:")
    print(f"  ID: {admin_row[0]}")
    print(f"  用户名: {admin_row[1]}")
    print(f"  邮箱: {admin_row[2]}")
    print(f"  角色: {admin_row[3]}")
    print(f"  状态: {admin_row[4]}")
    print(f"  已验证: {admin_row[5]}")
    print(f"  活跃: {admin_row[6]}")
    print(f"  用户类型: {admin_row[7]}")
    print(f"  登录次数: {admin_row[8]}")
    print(f"  最后登录: {admin_row[9]}")
else:
    print("未找到 admin 用户")

print("\n" + "="*60)

# 检查 roles 表
cursor.execute("SELECT id, name, code, is_active FROM roles ORDER BY id")
roles = cursor.fetchall()
print("Roles 表:")
for role in roles:
    print(f"  ID: {role[0]}, 名称: {role[1]}, 代码: {role[2]}, 活跃: {role[3]}")

print("\n" + "="*60)

# 检查 user_roles 表，查看 admin 用户的角色
cursor.execute("""
    SELECT ur.user_id, ur.role_id, r.name, r.code
    FROM user_roles ur
    JOIN roles r ON ur.role_id = r.id
    WHERE ur.user_id = (SELECT id FROM users WHERE username = 'admin')
""")
user_roles = cursor.fetchall()
print(f"Admin 用户的角色关联 ({len(user_roles)} 个):")
for ur in user_roles:
    print(f"  用户ID: {ur[0]}, 角色ID: {ur[1]}, 角色名称: {ur[2]}, 角色代码: {ur[3]}")

print("\n" + "="*60)

# 检查所有用户计数
cursor.execute("SELECT COUNT(*) FROM users")
total_users = cursor.fetchone()[0]
print(f"总用户数: {total_users}")

cursor.execute("SELECT COUNT(*) FROM users WHERE role LIKE '%admin%'")
admin_count = cursor.fetchone()[0]
print(f"管理员用户数: {admin_count}")

conn.close()