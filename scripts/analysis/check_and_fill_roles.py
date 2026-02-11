#!/usr/bin/env python3
"""
检查和填充roles表
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

import sqlite3
import os

def check_database():
    """检查数据库状态"""
    print("=" * 60)
    print("检查数据库状态")
    print("=" * 60)
    
    # 检查多个可能的数据库文件
    db_files = [
        ('项目根目录', 'sport_lottery.db'),
        ('backend目录', 'backend/sport_lottery.db'),
        ('data目录', 'data/sport_lottery.db')
    ]
    
    for location, db_file in db_files:
        if os.path.exists(db_file):
            print(f"\n[文件夹] {location}: {db_file}")
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # 检查roles表是否存在
                cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="roles"')
                roles_exists = cursor.fetchone()
                
                if roles_exists:
                    print(f"  [OK] roles表存在")
                    
                    # 获取表结构
                    cursor.execute('PRAGMA table_info(roles)')
                    columns = cursor.fetchall()
                    print(f"    表结构 ({len(columns)} 列):")
                    for col in columns:
                        print(f"      {col[1]} ({col[2]})")
                    
                    # 获取行数
                    cursor.execute('SELECT COUNT(*) FROM roles')
                    row_count = cursor.fetchone()[0]
                    print(f"    行数: {row_count}")
                    
                    if row_count > 0:
                        cursor.execute('SELECT id, name, description, status FROM roles')
                        rows = cursor.fetchall()
                        print(f"    现有角色:")
                        for row in rows:
                            status = "激活" if row[3] else "禁用"
                            print(f"      ID: {row[0]}, 名称: {row[1]}, 描述: {row[2]}, 状态: {status}")
                else:
                    print(f"  [ERROR] roles表不存在")
                
                # 检查admin_users表
                cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="admin_users"')
                admin_users_exists = cursor.fetchone()
                
                if admin_users_exists:
                    cursor.execute('SELECT COUNT(*) FROM admin_users')
                    admin_count = cursor.fetchone()[0]
                    print(f"  [用户] admin_users表: {admin_count} 个用户")
                    
                    if admin_count > 0:
                        cursor.execute('SELECT id, username, role, status FROM admin_users LIMIT 5')
                        admins = cursor.fetchall()
                        for admin in admins:
                            print(f"      ID: {admin[0]}, 用户名: {admin[1]}, 角色: {admin[2]}, 状态: {admin[3]}")
                else:
                    print(f"  [ERROR] admin_users表不存在")
                
                conn.close()
                
            except Exception as e:
                print(f"  错误: {e}")
        else:
            print(f"\n[文件夹] {location}: {db_file} - 文件不存在")

def fill_roles_table():
    """填充roles表"""
    print("\n" + "=" * 60)
    print("填充roles表")
    print("=" * 60)
    
    # 使用项目根目录的数据库文件
    db_file = 'sport_lottery.db'
    
    if not os.path.exists(db_file):
        print(f"[ERROR] 数据库文件不存在: {db_file}")
        return False
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 首先确保roles表存在，如果不存在则创建
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            permissions TEXT,
            status BOOLEAN DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            deleted_at DATETIME
        )
        ''')
        
        print("[OK] 确保roles表存在")
        
        # 默认角色数据
        default_roles = [
            ("admin", "系统管理员，拥有最高权限", None, 1, 1),
            ("user", "普通用户，拥有基本权限", None, 1, 2),
            ("analyst", "数据分析师，可以查看和分析数据", None, 1, 3),
            ("operator", "操作员，可以执行日常操作", None, 1, 4)
        ]
        
        inserted_count = 0
        for role_name, description, permissions, status, sort_order in default_roles:
            # 检查是否已存在
            cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"  [INFO] 角色 '{role_name}' 已存在，跳过")
            else:
                cursor.execute('''
                INSERT INTO roles (name, description, permissions, status, sort_order)
                VALUES (?, ?, ?, ?, ?)
                ''', (role_name, description, permissions, status, sort_order))
                inserted_count += 1
                print(f"  [OK] 插入角色: '{role_name}'")
        
        conn.commit()
        
        if inserted_count > 0:
            print(f"\n[OK] 成功插入 {inserted_count} 个新角色")
        else:
            print(f"\n[INFO] 所有默认角色已存在，无需插入")
        
        # 验证结果
        cursor.execute('SELECT COUNT(*) FROM roles')
        final_count = cursor.fetchone()[0]
        print(f"roles表现在共有 {final_count} 个角色")
        
        cursor.execute('SELECT id, name, description, status FROM roles')
        rows = cursor.fetchall()
        for row in rows:
            status_text = "激活" if row[3] else "禁用"
            print(f"  ID: {row[0]}, 名称: {row[1]}, 描述: {row[2]}, 状态: {status_text}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] 填充roles表失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # 检查数据库状态
    check_database()
    
    # 填充roles表
    success = fill_roles_table()
    
    if success:
        print("\n" + "=" * 60)
        print("[OK] 操作完成！")
        print("=" * 60)
        print("\n建议: 重启后端服务后测试登录功能")
        return 0
    else:
        print("\n[ERROR] 操作失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())