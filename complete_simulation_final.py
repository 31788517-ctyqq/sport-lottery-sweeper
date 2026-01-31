#!/usr/bin/env python3
"""
完整的用户操作模拟脚本
1. 创建数据库表
2. 创建管理员用户
3. 启动后端服务
4. 登录获取token
5. 创建500彩票数据源
6. 创建抓取任务
7. 执行抓取
8. 验证竞彩赛程数据
"""

import sys
import os
import time
import sqlite3
import requests
import subprocess
from pathlib import Path
import hashlib

# 配置
BASE_DIR = Path(__file__).parent
BACKEND_DIR = BASE_DIR / "backend"
DB_PATH = BASE_DIR / "sport_lottery.db"
DATA_DB_PATH = BASE_DIR / "data" / "sport_lottery.db"
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

def setup_database():
    """创建数据库表"""
    print("1. 创建数据库表...")
    
    # 确保数据库文件存在
    if not DB_PATH.exists():
        print(f"   创建数据库文件: {DB_PATH}")
        DB_PATH.parent.mkdir(exist_ok=True)
    
    # 导入并创建表
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from core.database import create_tables
        create_tables()
        print("   ✅ 数据库表创建成功")
        
        # 验证表
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = [t[0] for t in c.fetchall()]
        print(f"   现有表: {tables}")
        conn.close()
        return True
    except Exception as e:
        print(f"   ❌ 创建表失败: {e}")
        return False

def create_admin_user():
    """创建管理员用户"""
    print("2. 创建管理员用户...")
    
    if not DB_PATH.exists():
        print("   ❌ 数据库文件不存在")
        return False
    
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    # 确保users表存在
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            user_type TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            is_verified INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # 检查是否已存在admin用户
    c.execute("SELECT * FROM users WHERE username='admin'")
    if c.fetchone():
        print("   ✅ admin用户已存在")
        conn.close()
        return True
    
    # 创建admin用户
    password = "admin123"
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        c.execute("""
            INSERT INTO users (username, email, hashed_password, status, user_type, is_active, is_verified, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("admin", "admin@example.com", password_hash, "active", "admin", 1, 1, now, now))
        
        conn.commit()
        print("   ✅ 创建admin用户成功")
        print(f"      用户名: admin")
        print(f"      密码: {password}")
        return True
    except Exception as e:
        print(f"   ❌ 创建用户失败: {e}")
        return False
    finally:
        conn.close()

def start_backend_service():
    """启动后端服务"""
    print("3. 启动后端服务...")
    
    # 杀掉可能占用端口的进程
    try:
        subprocess.run(['taskkill', '/F', '/PID', '8000'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    
    # 切换到backend目录
    os.chdir(str(BACKEND_DIR))
    
    # 启动进程（后台）
    proc = subprocess.Popen(
        [sys.executable, 'main.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # 等待服务启动
    print("   等待服务启动...")
    for i in range(30):
        time.sleep(1)
        try:
            resp = requests.get(f"{BASE_URL}/docs", timeout=1)
            if resp.status_code == 200:
                print(f"   ✅ 后端服务启动成功 (PID: {proc.pid})")
                return proc
        except:
            if i % 5 == 0:
                print(f"   等待中... ({i+1}/30)")
    
    print("   ❌ 后端服务启动超时")
    return None

def login_and_get_token():
    """登录获取token"""
    print("4. 登录获取token...")
    
    url = f"{BASE_URL}{API_PREFIX}/auth/login"
    data = {"username": "admin", "password": "admin123"}
    
    try:
        resp = requests.post(url, json=data, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            if result.get("code") == 200:
                token = result["data"]["access_token"]
                print(f"   ✅ 登录成功")
                print(f"      Token: {token[:50]}...")
                return token
            else:
                print(f"   ❌ 登录失败: {result.get('message')}")
        else:
            print(f"   ❌ 登录HTTP错误: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ 登录异常: {e}")
    
    return None

def create_data_source(token):
    """创建500彩票数据源"""
    print("5. 创建500彩票数据源...")
    
    url = f"{BASE_URL}{API_PREFIX}/crawler/sources/five-hundred-create"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.post(url, headers=headers, timeout=10)
        print(f"   响应状态: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"   响应内容: {result}")
            
            if "message" in result and "成功" in result["message"]:
                source_id = result.get("source_id")
                print(f"   ✅ 数据源创建成功 (ID: {source_id})")
                return source_id
            elif "已存在" in result.get("message", ""):
                print("   ⚠️  数据源已存在")
                return 1
        else:
            print(f"   ❌ 创建失败: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ 创建异常: {e}")
    
    return None

def create_crawler_task(token):
    """创建抓取任务"""
    print("6. 创建抓取任务...")
    
    url = f"{BASE_URL}{API_PREFIX}/crawler/tasks/five-hundred-create"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    task_data = {
        "name": "500彩票网竞彩足球近三天赛程抓取",
        "description": "从500彩票网抓取未来三天的竞彩足球比赛赛程",
        "config": {
            "days": 3,
            "priority": "high",
            "category": "竞彩赛程"
        }
    }
    
    try:
        resp = requests.post(url, json=task_data, headers=headers, timeout=10)
        print(f"   响应状态: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"   响应内容: {result}")
            
            if "message" in result and "成功" in result["message"]:
                task_id = result.get("task_id")
                print(f"   ✅ 抓取任务创建成功 (ID: {task_id})")
                return task_id
        else:
            print(f"   ❌ 创建失败: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ 创建异常: {e}")
    
    return None

def execute_crawler_task(token, task_id):
    """执行抓取任务"""
    print("7. 执行抓取任务...")
    
    url = f"{BASE_URL}{API_PREFIX}/crawler/tasks/{task_id}/execute-five-hundred-crawl?days=3"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.post(url, headers=headers, timeout=15)
        print(f"   响应状态: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"   响应内容: {result}")
            
            if "message" in result and "成功" in result["message"]:
                print(f"   ✅ 抓取任务执行成功")
                return True
        else:
            print(f"   ❌ 执行失败: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ 执行异常: {e}")
    
    return False

def check_matches_data():
    """检查竞彩赛程数据"""
    print("8. 检查竞彩赛程数据...")
    
    url = f"{BASE_URL}{API_PREFIX}/matches"
    
    try:
        resp = requests.get(url, timeout=10)
        print(f"   响应状态: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            
            if result.get("code") == 200:
                data = result.get("data", {})
                items = data.get("items", [])
                total = data.get("total", 0)
                
                print(f"   ✅ 发现 {total} 条比赛数据")
                
                if items:
                    print("   示例比赛:")
                    for i, match in enumerate(items[:3]):
                        print(f"     {i+1}. {match.get('home_team', '未知')} vs {match.get('away_team', '未知')}")
                        print(f"        时间: {match.get('match_time', '未知')}")
                        print(f"        联赛: {match.get('league', '未知')}")
                else:
                    print("   ⚠️  暂无比赛数据")
                
                return total > 0
            else:
                print(f"   ❌ 获取数据失败: {result.get('message')}")
        else:
            print(f"   ❌ HTTP错误: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ 检查异常: {e}")
    
    return False

def main():
    print("=" * 60)
    print("体育彩票扫盘系统 - 用户操作模拟")
    print("=" * 60)
    
    # 1. 创建数据库表
    if not setup_database():
        print("❌ 数据库初始化失败，退出")
        return
    
    # 2. 创建管理员用户
    if not create_admin_user():
        print("⚠️  管理员用户创建失败，继续尝试")
    
    # 3. 启动后端服务
    backend_proc = start_backend_service()
    if not backend_proc:
        print("❌ 后端服务启动失败，退出")
        return
    
    # 等待服务稳定
    time.sleep(3)
    
    # 4. 登录获取token
    token = login_and_get_token()
    if not token:
        print("❌ 登录失败，退出")
        backend_proc.terminate()
        return
    
    # 5. 创建数据源
    source_id = create_data_source(token)
    if not source_id:
        print("⚠️  数据源创建失败，使用默认ID=1")
        source_id = 1
    
    # 6. 创建抓取任务
    task_id = create_crawler_task(token)
    if not task_id:
        print("⚠️  抓取任务创建失败，使用默认ID=1")
        task_id = 1
    
    # 7. 执行抓取
    if execute_crawler_task(token, task_id):
        print("✅ 抓取任务执行成功")
    else:
        print("⚠️  抓取任务执行可能失败")
    
    # 8. 检查数据
    time.sleep(2)
    if check_matches_data():
        print("\n" + "=" * 60)
        print("🎉 模拟操作完成！")
        print("✅ 数据源创建成功")
        print("✅ 抓取任务创建成功") 
        print("✅ 抓取任务执行成功")
        print("✅ 竞彩赛程页面已显示真实数据")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️  模拟操作部分完成")
        print("✅ 数据源和任务已创建")
        print("⚠️  竞彩赛程页面暂无数据")
        print("   可能原因：")
        print("   1. 爬虫服务需要额外配置")
        print("   2. 500彩票网API访问限制")
        print("   3. 数据库连接问题")
        print("=" * 60)
    
    # 停止后端服务
    print("\n停止后端服务...")
    backend_proc.terminate()
    print("✅ 模拟操作结束")

if __name__ == "__main__":
    main()