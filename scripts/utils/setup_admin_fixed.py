#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建admin用户并测试登录
"""
import sqlite3
import bcrypt
import requests
import json
import sys
import os

def create_admin_user():
    """创建admin用户（如果不存在）"""
    conn = sqlite3.connect('sport_lottery.db')
    c = conn.cursor()
    
    # 检查admin用户是否已存在
    c.execute("SELECT id FROM users WHERE username='admin'")
    if c.fetchone():
        print("admin用户已存在")
        conn.close()
        return True
    
    # 获取users表的列信息
    c.execute('PRAGMA table_info(users)')
    columns = c.fetchall()
    print(f"users表有 {len(columns)} 列")
    
    # 准备插入数据
    password = 'admin123'
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 基本列值
    data = {
        'username': 'admin',
        'email': 'admin@example.com',
        'password_hash': password_hash,
        'first_name': '系统',
        'last_name': '管理员',
        'nickname': 'Admin',
        'role': 'admin',
        'status': 'active',
        'is_verified': 1,
        'is_online': 0,
        'user_type': 'admin',
        'timezone': 'UTC',
        'language': 'zh',
        'notification_preferences': '{}',
        'login_count': 0,
        'created_at': 'datetime("now")',
        'updated_at': 'datetime("now")'
    }
    
    # 构建INSERT语句
    columns_str = ', '.join([col[1] for col in columns if col[1] in data or col[1] == 'id'])
    placeholders = ', '.join(['?' for _ in range(len(columns_str.split(', ')))])
    
    # 准备值列表（按列顺序）
    values = []
    for col in columns:
        col_name = col[1]
        if col_name == 'id':
            continue  # 自增
        if col_name in data:
            values.append(data[col_name])
        else:
            # 可为空列，设为None
            values.append(None)
    
    try:
        sql = f'INSERT INTO users ({columns_str}) VALUES ({placeholders})'
        c.execute(sql, values)
        conn.commit()
        print("[OK] admin用户创建成功!")
        print(f"   用户名: admin, 密码: {password}")
        return True
    except Exception as e:
        print(f"[FAIL] 创建admin用户失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

def test_login():
    """测试admin登录"""
    url = "http://localhost:8000/api/v1/admin/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"\n登录测试结果:")
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  登录成功!")
            print(f"  访问令牌: {result.get('access_token', 'N/A')}")
            print(f"  令牌类型: {result.get('token_type', 'N/A')}")
            if 'user' in result:
                print(f"  用户信息: {result['user']}")
            return True
        else:
            print(f"  登录失败")
            print(f"  响应: {response.text}")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"  连接错误: {e}")
        return False
    except Exception as e:
        print(f"  意外错误: {e}")
        return False

def main():
    print("=== 设置admin用户并测试登录 ===")
    
    # 检查后端是否运行
    try:
        response = requests.get('http://localhost:8000/docs', timeout=2)
        print("后端正在运行")
    except:
        print("警告: 后端可能未运行，请确保后端已启动")
    
    # 创建admin用户
    if not create_admin_user():
        print("无法创建admin用户，退出")
        sys.exit(1)
    
    # 测试登录
    if test_login():
        print("\n[OK] 所有测试通过!")
    else:
        print("\n[FAIL] 登录测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()