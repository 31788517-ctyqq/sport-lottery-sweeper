#!/usr/bin/env python3
"""
同步roles表数据从主数据库到backend数据库

注意：自数据库路径统一后，所有数据库访问应通过 backend.database.DATABASE_PATH。
如果已配置硬链接，源数据库和目标数据库为同一物理文件，同步操作可能不需要。
"""
import sqlite3
import os
import sys
from pathlib import Path

# 添加backend目录到Python路径
sys.path.append(str(Path(__file__).parent / 'backend'))

def sync_roles_data():
    """同步roles表数据"""
    print("=" * 60)
    print("同步roles表数据")
    print("=" * 60)
    
    # 使用统一的数据库路径配置
    from backend.database import DATABASE_PATH
    
    # 源数据库（项目根目录）- 使用统一配置
    source_db = str(DATABASE_PATH)
    # 目标数据库（backend目录）- 由于硬链接，实际指向同一文件
    target_db = str(DATABASE_PATH)
    
    if not os.path.exists(source_db):
        print(f"[ERROR] 源数据库不存在: {source_db}")
        return False
    
    if not os.path.exists(target_db):
        print(f"[ERROR] 目标数据库不存在: {target_db}")
        return False
    
    try:
        # 连接源数据库
        source_conn = sqlite3.connect(source_db)
        source_cursor = source_conn.cursor()
        
        # 连接目标数据库
        target_conn = sqlite3.connect(target_db)
        target_cursor = target_conn.cursor()
        
        print(f"源数据库: {source_db}")
        print(f"目标数据库: {target_db}")
        
        # 检查源数据库中的roles表
        source_cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="roles"')
        if not source_cursor.fetchone():
            print("[ERROR] 源数据库中不存在roles表")
            return False
        
        # 检查目标数据库中的roles表
        target_cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="roles"')
        if not target_cursor.fetchone():
            print("[ERROR] 目标数据库中不存在roles表")
            return False
        
        # 获取源数据库中的roles数据
        source_cursor.execute('SELECT id, name, description, permissions, status, sort_order, created_at, updated_at FROM roles')
        source_rows = source_cursor.fetchall()
        
        print(f"源数据库中有 {len(source_rows)} 个角色")
        
        # 清空目标数据库中的roles表
        target_cursor.execute('DELETE FROM roles')
        print("已清空目标数据库中的roles表")
        
        # 插入数据到目标数据库
        inserted_count = 0
        for row in source_rows:
            try:
                target_cursor.execute('''
                INSERT INTO roles (id, name, description, permissions, status, sort_order, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', row)
                inserted_count += 1
                print(f"  [OK] 插入角色: '{row[1]}' (ID: {row[0]})")
            except sqlite3.IntegrityError as e:
                print(f"  [WARN] 插入角色 '{row[1]}' 失败: {e}")
        
        target_conn.commit()
        
        print(f"\n[OK] 成功同步 {inserted_count} 个角色到目标数据库")
        
        # 验证目标数据库中的数据
        target_cursor.execute('SELECT COUNT(*) FROM roles')
        target_count = target_cursor.fetchone()[0]
        print(f"目标数据库roles表现在共有 {target_count} 个角色")
        
        target_cursor.execute('SELECT id, name, description, status FROM roles')
        rows = target_cursor.fetchall()
        for row in rows:
            status_text = "激活" if row[3] else "禁用"
            print(f"  ID: {row[0]}, 名称: {row[1]}, 描述: {row[2]}, 状态: {status_text}")
        
        # 关闭连接
        source_conn.close()
        target_conn.close()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 同步失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_admin_users_structure():
    """检查admin_users表结构差异"""
    print("\n" + "=" * 60)
    print("检查admin_users表结构")
    print("=" * 60)
    
    # 使用统一的数据库路径配置
    from backend.database import DATABASE_PATH
    
    # 由于数据库路径已统一，只检查一个文件
    db_files = [
        ('统一数据库文件', str(DATABASE_PATH))
    ]
    
    for location, db_file in db_files:
        if os.path.exists(db_file):
            print(f"\n{location}: {db_file}")
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # 获取表结构
                cursor.execute('PRAGMA table_info(admin_users)')
                columns = cursor.fetchall()
                
                print(f"  表结构 ({len(columns)} 列):")
                column_names = []
                for col in columns:
                    column_names.append(col[1])
                    print(f"    {col[1]} ({col[2]})")
                
                # 检查是否有status列
                if 'status' in column_names:
                    print(f"  [OK] 包含status列")
                    cursor.execute('SELECT id, username, status FROM admin_users LIMIT 3')
                    rows = cursor.fetchall()
                    for row in rows:
                        print(f"    用户: {row[1]}, 状态: {row[2]}")
                else:
                    print(f"  [WARN] 不包含status列")
                
                conn.close()
                
            except Exception as e:
                print(f"  错误: {e}")
        else:
            print(f"\n[WARN] 数据库文件不存在: {db_file}")

def main():
    # 同步roles表数据
    success = sync_roles_data()
    
    # 检查admin_users表结构
    check_admin_users_structure()
    
    if success:
        print("\n" + "=" * 60)
        print("[OK] 同步完成！")
        print("=" * 60)
        print("\n建议: 重启后端服务后测试登录功能")
        print("注意: 数据库文件已统一，所有数据库访问通过 backend.database.DATABASE_PATH 配置")
        return 0
    else:
        print("\n[ERROR] 同步失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())