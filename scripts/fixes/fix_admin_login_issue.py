#!/usr/bin/env python3
"""
修复管理员登录问题的脚本
问题：项目有前端用户(users表)和后端用户(admin_users表)的区分
但当前：
1. admin用户在users表中（普通用户表）
2. admin_users表为空
3. 管理员登录端点(/api/v1/admin/login)可能查询的是users表
解决方案：
1. 在admin_users表中创建正确的管理员账户
2. 或者修改认证逻辑
"""
import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir
sys.path.insert(0, str(project_root))

try:
    from backend.core.security import get_password_hash
    print("✓ 导入security模块成功")
except ImportError as e:
    print(f"⚠ 无法导入security模块: {e}")
    get_password_hash = None

def fix_admin_login():
    db_path = "data/sport_lottery.db"
    print(f"\n=== 修复管理员登录问题 ===")
    print(f"数据库: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. 检查当前状态
    print("\n1. 当前状态检查:")
    
    # 检查users表中的admin用户
    cursor.execute("SELECT username, email, role, status FROM users WHERE username='admin';")
    user_admin = cursor.fetchone()
    if user_admin:
        print(f"   ✓ users表中有admin用户:")
        print(f"      用户名: {user_admin['username']}, 邮箱: {user_admin['email']}")
        print(f"      角色: {user_admin['role']}, 状态: {user_admin['status']}")
    else:
        print("   ✗ users表中没有admin用户")
    
    # 检查admin_users表
    cursor.execute("SELECT COUNT(*) as count FROM admin_users;")
    admin_count = cursor.fetchone()['count']
    print(f"   ⚠ admin_users表中有 {admin_count} 条记录")
    
    if admin_count > 0:
        cursor.execute("SELECT username, email, role, status FROM admin_users LIMIT 3;")
        admins = cursor.fetchall()
        for admin in admins:
            print(f"      - {admin['username']} ({admin['email']}), 角色: {admin['role']}")
    
    # 2. 解决方案选择
    print("\n2. 解决方案:")
    print("   a) 在admin_users表中创建管理员账户（推荐）")
    print("   b) 修改users表中的admin用户为正确的角色")
    
    # 3. 实施解决方案a: 在admin_users表中创建管理员
    print("\n3. 在admin_users表中创建管理员账户...")
    
    if not get_password_hash:
        print("   ✗ 无法创建密码哈希，停止执行")
        conn.close()
        return
    
    # 检查admin_users表结构
    cursor.execute("PRAGMA table_info(admin_users);")
    columns = cursor.fetchall()
    column_names = [col['name'] for col in columns]
    print(f"   admin_users表字段: {', '.join(column_names[:10])}...")
    
    # 检查admin用户是否已存在
    cursor.execute("SELECT id FROM admin_users WHERE username='admin';")
    existing = cursor.fetchone()
    
    if existing:
        print(f"   admin用户已存在，ID: {existing['id']}")
        # 更新密码
        password_hash = get_password_hash("admin123")
        cursor.execute("""
            UPDATE admin_users 
            SET password_hash = ?, 
                status = 'active',
                role = 'admin',
                is_verified = 1,
                real_name = '系统管理员',
                email = 'admin@example.com',
                updated_at = datetime('now')
            WHERE username = ?
        """, (password_hash, "admin"))
        print(f"   ✓ 已更新admin用户密码为 'admin123'")
    else:
        # 创建新的admin用户
        password_hash = get_password_hash("admin123")
        
        # 根据表结构构建插入语句
        if 'real_name' in column_names:
            cursor.execute("""
                INSERT INTO admin_users (
                    username, email, password_hash, real_name,
                    role, status, is_verified, must_change_password,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (
                "admin",
                "admin@example.com",
                password_hash,
                "系统管理员",
                "admin",
                "active",
                1,  # is_verified
                0   # must_change_password
            ))
        else:
            # 备用方案
            cursor.execute("""
                INSERT INTO admin_users (username, email, password_hash, role, status)
                VALUES (?, ?, ?, ?, ?)
            """, ("admin", "admin@example.com", password_hash, "admin", "active"))
        
        print(f"   ✓ 已创建admin用户，密码: 'admin123'")
    
    conn.commit()
    
    # 4. 验证
    print("\n4. 验证:")
    cursor.execute("SELECT username, email, role, status FROM admin_users WHERE username='admin';")
    new_admin = cursor.fetchone()
    if new_admin:
        print(f"   ✓ admin_users表中的admin用户:")
        print(f"      用户名: {new_admin['username']}")
        print(f"      邮箱: {new_admin['email']}")
        print(f"      角色: {new_admin['role']}")
        print(f"      状态: {new_admin['status']}")
    else:
        print("   ✗ 未找到admin用户")
    
    # 5. 测试建议
    print("\n5. 后续步骤:")
    print("   a) 测试普通用户登录: POST /api/v1/auth/login")
    print("      用户名: admin, 密码: admin123")
    print("   b) 测试管理员登录: POST /api/v1/admin/login")
    print("      用户名: admin, 密码: admin123")
    print("   c) 如果管理员登录仍然失败，可能需要修改")
    print("     /api/v1/admin/login 端点，使其查询admin_users表")
    
    # 6. 统计
    cursor.execute("SELECT COUNT(*) as count FROM admin_users;")
    final_count = cursor.fetchone()['count']
    print(f"\n6. 最终状态: admin_users表中有 {final_count} 条记录")
    
    conn.close()
    
    print("\n=== 修复完成 ===")
    print("请运行 test_both_logins.py 测试两个登录端点")

if __name__ == "__main__":
    fix_admin_login()