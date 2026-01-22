#!/usr/bin/env python3
import sqlite3
import datetime
import json
import subprocess
import time
import os

def repair_database():
    print("修复数据库...")
    conn = sqlite3.connect('sport_lottery.db')
    c = conn.cursor()
    
    # 修复admin用户的datetime字段
    now = datetime.datetime.now().isoformat()
    c.execute("UPDATE users SET created_at = ?, updated_at = ? WHERE username = 'admin'", (now, now))
    print(f"  更新created_at/updated_at: {now}")
    
    # 修复notification_preferences
    c.execute("SELECT notification_preferences FROM users WHERE username='admin'")
    pref = c.fetchone()[0]
    if pref:
        try:
            json.loads(pref)
            print(f"  notification_preferences已经是有效JSON")
        except:
            c.execute("UPDATE users SET notification_preferences = '{}' WHERE username = 'admin'")
            print(f"  修复notification_preferences为{{}}")
    else:
        c.execute("UPDATE users SET notification_preferences = '{}' WHERE username = 'admin'")
        print(f"  设置notification_preferences为{{}}")
    
    conn.commit()
    conn.close()
    print("✅ 数据库修复完成")

def start_backend():
    print("启动后端...")
    # 切换到backend目录
    os.chdir('backend')
    # 启动进程
    proc = subprocess.Popen(['python', 'main.py'], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE,
                          text=True)
    os.chdir('..')
    print(f"后端进程已启动，PID: {proc.pid}")
    # 等待几秒
    time.sleep(5)
    return proc

def test_login():
    print("测试登录...")
    import requests
    try:
        response = requests.post('http://localhost:8000/api/v1/admin/login',
                                json={'username': 'admin', 'password': 'admin123'},
                                timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 登录成功!")
            print(f"响应: {response.json()}")
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求错误: {e}")
        return False

if __name__ == "__main__":
    repair_database()
    time.sleep(2)
    proc = start_backend()
    time.sleep(5)
    success = test_login()
    if success:
        print("\n🎉 Admin登录测试通过!")
    else:
        print("\n⚠️  Admin登录测试失败，请检查日志")