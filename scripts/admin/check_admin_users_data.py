#!/usr/bin/env python3
import sqlite3
import sys

def check_admin_users():
    db_path = "sport_lottery.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=== 检查admin_users表 ===")
    
    # 1. 显示所有字段
    cursor.execute("PRAGMA table_info(admin_users);")
    columns = cursor.fetchall()
    print(f"\n1. 表结构 ({len(columns)} 个字段):")
    for col in columns:
        print(f"   {col['cid']:2}. {col['name']:25} ({col['type']})")
    
    # 2. 显示所有数据
    cursor.execute("SELECT * FROM admin_users ORDER BY id;")
    rows = cursor.fetchall()
    print(f"\n2. 数据 ({len(rows)} 条记录):")
    
    for row in rows:
        print(f"\n   ID: {row['id']}")
        print(f"   用户名: {row.get('username', 'N/A')}")
        print(f"   邮箱: {row.get('email', 'N/A')}")
        
        # 检查是否有密码字段
        if 'password_hash' in row.keys():
            password_hash = row['password_hash']
            print(f"   密码哈希: {password_hash if password_hash else '空'}")
        elif 'password' in row.keys():
            password_hash = row['password']
            print(f"   密码字段: {password_hash if password_hash else '空'}")
        else:
            print("   密码字段: 未找到")
            
        print(f"   角色: {row.get('role', 'N/A')}")
        print(f"   状态: {row.get('status', 'N/A')}")
        print(f"   真实姓名: {row.get('real_name', row.get('full_name', 'N/A'))}")
    
    # 3. 检查是否有密码哈希
    print(f"\n3. 密码检查:")
    if rows:
        first_row = rows[0]
        if 'password_hash' in first_row.keys():
            password_hash = first_row['password_hash']
            if password_hash and len(password_hash) > 10:
                print(f"   ✓ 找到密码哈希字段，且有值")
            elif password_hash:
                print(f"   ⚠ 密码哈希字段有值但可能太短: {password_hash}")
            else:
                print(f"   ✗ 密码哈希字段为空")
        else:
            print(f"   ✗ 表中没有password_hash字段")
            
        # 检查字段名
        field_names = list(first_row.keys())
        password_fields = [f for f in field_names if 'password' in f.lower()]
        if password_fields:
            print(f"   可能的密码字段: {password_fields}")
        else:
            print(f"   没有任何密码相关字段")
    
    conn.close()
    print("\n=== 检查完成 ===")

if __name__ == "__main__":
    check_admin_users()