#!/usr/bin/env python
"""
修复admin登录问题 - 使用bcrypt哈希
"""
import sqlite3
import bcrypt
import hashlib
import sys

def create_bcrypt_hash(password: str) -> str:
    """生成bcrypt哈希"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_bcrypt_hash(password: str, hashed: str) -> bool:
    """验证bcrypt哈希"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def main():
    print("=== 修复admin登录问题 ===")
    
    conn = sqlite3.connect('sport_lottery.db')
    c = conn.cursor()
    
    # 1. 检查users表结构
    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    print("\n1. users表结构:")
    for col in columns:
        print(f"   {col[1]} ({col[2]})")
    
    # 2. 检查当前admin用户
    c.execute("SELECT id, username, password_hash FROM users WHERE username='admin'")
    admin_row = c.fetchone()
    
    if admin_row:
        print(f"\n2. 当前admin用户:")
        print(f"   ID: {admin_row[0]}, 用户名: {admin_row[1]}")
        print(f"   密码哈希: {admin_row[2][:60]}...")
        
        # 测试验证
        test_password = 'admin123'
        current_hash = admin_row[2]
        
        # 尝试bcrypt验证
        try:
            bcrypt_valid = verify_bcrypt_hash(test_password, current_hash)
            print(f"   Bcrypt验证: {'✅ 通过' if bcrypt_valid else '❌ 失败'}")
        except:
            print(f"   Bcrypt验证: ❌ 失败 (哈希格式不匹配)")
        
        # 尝试SHA256验证
        sha256_hash = hashlib.sha256(test_password.encode('utf-8')).hexdigest()
        sha256_valid = (current_hash == sha256_hash)
        print(f"   SHA256验证: {'✅ 通过' if sha256_valid else '❌ 失败'}")
        
        # 如果当前哈希不是bcrypt，更新为bcrypt
        if not bcrypt_valid:
            print("\n3. 更新密码哈希为bcrypt格式...")
            new_hash = create_bcrypt_hash(test_password)
            c.execute("UPDATE users SET password_hash = ? WHERE id = ?", 
                     (new_hash, admin_row[0]))
            conn.commit()
            print(f"   更新完成! 新哈希: {new_hash[:60]}...")
            
            # 验证新哈希
            test_result = verify_bcrypt_hash(test_password, new_hash)
            print(f"   新哈希验证: {'✅ 通过' if test_result else '❌ 失败'}")
    else:
        print("\n2. 未找到admin用户，正在创建...")
        # 创建admin用户
        password = 'admin123'
        password_hash = create_bcrypt_hash(password)
        
        c.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, nickname, 
                              role, status, is_verified, is_active, user_type, login_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@example.com', password_hash, '系统', '管理员', 'Admin', 
              'admin', 'active', 1, 1, 'admin', 0))
        
        conn.commit()
        print(f"   admin用户创建成功!")
        print(f"   密码哈希: {password_hash[:60]}...")
    
    # 3. 验证最终状态
    print("\n4. 最终验证:")
    c.execute("SELECT username, role, status FROM users WHERE username='admin'")
    final_row = c.fetchone()
    if final_row:
        print(f"   用户: {final_row[0]}")
        print(f"   角色: {final_row[1]}")
        print(f"   状态: {final_row[2]}")
        
        # 测试bcrypt验证
        c.execute("SELECT password_hash FROM users WHERE username='admin'")
        hash_val = c.fetchone()[0]
        test_valid = verify_bcrypt_hash('admin123', hash_val)
        print(f"   Bcrypt登录验证: {'✅ 通过' if test_valid else '❌ 失败'}")
    else:
        print("   ❌ admin用户不存在")
    
    conn.close()
    print("\n=== 修复完成 ===")

if __name__ == "__main__":
    main()