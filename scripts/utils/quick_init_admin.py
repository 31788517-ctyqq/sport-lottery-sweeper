#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
纯SQLite方式快速初始化管理员角色、权限和用户
"""
import sqlite3
import hashlib
import os

DB_PATH = 'data/sport_lottery.db'

def hash_password(password):
    # 使用SHA256简单哈希（仅用于测试，生产请用bcrypt）
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. 插入角色
        print("插入角色...")
        roles = [
            ('超级管理员', 'super_admin', '系统超级管理员，拥有所有权限', 1),
            ('管理员', 'admin', '系统管理员，拥有大部分管理权限', 1),
            ('分析师', 'analyst', '数据分析师，可以查看和分析所有数据', 1),
            ('高级用户', 'premium', '高级用户，可以查看所有情报和高级功能', 1),
            ('普通用户', 'normal', '普通用户，只能查看基本情报', 1),
        ]
        for name, code, desc, active in roles:
            cursor.execute("INSERT OR IGNORE INTO roles (name, code, description, is_active) VALUES (?, ?, ?, ?)", (name, code, desc, active))
            print(f"  角色: {name}")
        
        # 2. 插入权限
        print("\n插入权限...")
        permissions = [
            ('访问管理后台', 'admin.access', 'admin', 'access', 1),
            ('查看爬虫配置', 'crawler.read', 'crawler', 'read', 1),
            ('管理爬虫配置', 'crawler.manage', 'crawler', 'manage', 1),
            ('查看用户列表', 'user.read', 'user', 'read', 1),
            ('创建用户', 'user.create', 'user', 'create', 1),
            ('编辑用户', 'user.update', 'user', 'update', 1),
            ('删除用户', 'user.delete', 'user', 'delete', 1),
        ]
        for name, code, res, act, active in permissions:
            cursor.execute("INSERT OR IGNORE INTO permissions (name, code, resource, action, is_active) VALUES (?, ?, ?, ?, ?)", (name, code, res, act, active))
            print(f"  权限: {name}")
        
        conn.commit()
        
        # 3. 建立角色-权限关联
        print("\n建立角色权限关联...")
        # 获取角色ID
        cursor.execute("SELECT id, code FROM roles")
        role_ids = {code: rid for rid, code in cursor.fetchall()}
        # 获取权限ID
        cursor.execute("SELECT id, code FROM permissions")
        perm_ids = {code: pid for pid, code in cursor.fetchall()}
        
        # super_admin 拥有所有权限
        all_perm_ids = list(perm_ids.values())
        for pid in all_perm_ids:
            cursor.execute("INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)", (role_ids['super_admin'], pid))
        
        # admin 拥有部分权限
        admin_perms = ['admin.access', 'crawler.read', 'crawler.manage', 'user.read', 'user.create', 'user.update', 'user.delete']
        for code in admin_perms:
            if code in perm_ids:
                cursor.execute("INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)", (role_ids['admin'], perm_ids[code]))
        
        # 4. 创建管理员用户
        print("\n创建管理员用户...")
        pwd_hash = hash_password('admin123')
        cursor.execute("""
            INSERT OR IGNORE INTO users 
            (username, email, password_hash, first_name, last_name, nickname, role, status, is_verified, is_active, user_type, login_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, ('admin', 'admin@example.com', pwd_hash, '系统', '管理员', 'Admin', 'admin', 'active', 1, 1, 'admin', 0))
        print("  用户: admin (密码: admin123)")
        
        # 5. 建立用户-角色关联
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        user_id = cursor.fetchone()[0]
        for role_code in ['admin', 'super_admin']:
            cursor.execute("INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_ids[role_code]))
        
        conn.commit()
        
        print("\n✅ 初始化成功!")
        print("\n登录信息:")
        print("  用户名: admin")
        print("  密码: admin123")
        print("\n下一步:")
        print("  1. 重启后端服务")
        print("  2. 登录后台管理系统")
        print("  3. 在爬虫配置页面查看 500.com足球竞彩 数据源")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 错误: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
