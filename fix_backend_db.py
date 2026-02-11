#!/usr/bin/env python3
"""
修复backend数据库结构
"""
import sqlite3
import os
import sys

def fix_roles_table():
    """修复backend数据库中的roles表结构"""
    print("=" * 60)
    print("修复backend数据库roles表结构")
    print("=" * 60)
    
    db_file = 'backend/sport_lottery.db'
    
    if not os.path.exists(db_file):
        print(f"[ERROR] 数据库文件不存在: {db_file}")
        return False
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print(f"修复数据库: {db_file}")
        
        # 获取当前表结构
        cursor.execute('PRAGMA table_info(roles)')
        current_columns = cursor.fetchall()
        current_column_names = [col[1] for col in current_columns]
        
        print(f"当前roles表结构 ({len(current_columns)} 列):")
        for col in current_columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 期望的表结构（根据模型定义）
        expected_columns = [
            ('id', 'INTEGER', 'PRIMARY KEY'),
            ('name', 'VARCHAR(100)', 'NOT NULL'),
            ('description', 'TEXT', ''),
            ('permissions', 'TEXT', ''),
            ('status', 'BOOLEAN', 'DEFAULT 1'),
            ('sort_order', 'INTEGER', 'DEFAULT 0'),
            ('created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP'),
            ('deleted_at', 'DATETIME', '')
        ]
        
        print(f"\n期望的roles表结构 ({len(expected_columns)} 列):")
        for name, type_, extra in expected_columns:
            print(f"  {name} ({type_}) {extra}")
        
        # 检查缺失的列
        missing_columns = []
        for name, type_, extra in expected_columns:
            if name not in current_column_names:
                missing_columns.append((name, type_, extra))
        
        if not missing_columns:
            print(f"\n[OK] roles表结构正确，无需修复")
            conn.close()
            return True
        
        print(f"\n缺失 {len(missing_columns)} 列:")
        for name, type_, extra in missing_columns:
            print(f"  {name} ({type_})")
        
        # 创建新表并迁移数据
        print(f"\n开始修复表结构...")
        
        # 创建临时表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles_new (
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
        
        # 迁移现有数据
        cursor.execute('''
        INSERT INTO roles_new (id, name, description, status, sort_order, created_at, updated_at)
        SELECT id, name, description, CASE WHEN is_active = 1 THEN 1 ELSE 0 END, 0, created_at, updated_at
        FROM roles
        ''')
        
        # 删除旧表
        cursor.execute('DROP TABLE roles')
        
        # 重命名新表
        cursor.execute('ALTER TABLE roles_new RENAME TO roles')
        
        conn.commit()
        
        print(f"\n[OK] roles表结构修复完成")
        
        # 验证修复结果
        cursor.execute('PRAGMA table_info(roles)')
        fixed_columns = cursor.fetchall()
        
        print(f"\n修复后的roles表结构 ({len(fixed_columns)} 列):")
        for col in fixed_columns:
            print(f"  {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def fill_roles_data():
    """填充roles表数据"""
    print("\n" + "=" * 60)
    print("填充roles表数据")
    print("=" * 60)
    
    db_file = 'backend/sport_lottery.db'
    
    if not os.path.exists(db_file):
        print(f"[ERROR] 数据库文件不存在: {db_file}")
        return False
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
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
        print(f"[ERROR] 填充数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("修复backend数据库")
    print("=" * 60)
    
    # 修复roles表结构
    if not fix_roles_table():
        print("\n[ERROR] 表结构修复失败，退出")
        return 1
    
    # 填充roles表数据
    if not fill_roles_data():
        print("\n[ERROR] 数据填充失败，退出")
        return 1
    
    print("\n" + "=" * 60)
    print("[OK] 数据库修复完成！")
    print("=" * 60)
    print("\n建议: 重启后端服务后测试登录功能")
    print("注意: 后端使用的是 backend/sport_lottery.db 文件")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())