import subprocess
import sys
import os
import time
import requests
import json
import sqlite3
from pathlib import Path

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

def kill_port(port=8000):
    """杀掉占用端口的进程"""
    try:
        # Windows
        subprocess.run(f'netstat -ano | findstr :{port}', shell=True, capture_output=True)
        subprocess.run(f'taskkill /F /PID {port}', shell=True, capture_output=True)
    except:
        pass

def start_backend():
    """启动后端服务"""
    kill_port(8000)
    
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    # 启动进程
    proc = subprocess.Popen([sys.executable, 'main.py'], 
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           text=True)
    
    # 等待启动
    for i in range(30):
        time.sleep(1)
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=1)
            if resp.status_code == 200:
                print(f"✅ 后端服务启动成功，PID: {proc.pid}")
                return proc
        except:
            pass
    
    # 超时
    stdout, _ = proc.communicate()
    print("❌ 后端服务启动超时")
    print("输出:", stdout[:2000])
    proc.terminate()
    return None

def create_admin_user():
    """创建管理员用户"""
    db_path = "data/sport_lottery.db"
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在:", db_path)
        return False
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 检查users表是否存在
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not c.fetchone():
        print("❌ users表不存在")
        return False
    
    # 检查admin用户是否存在
    c.execute("SELECT * FROM users WHERE username='admin'")
    if c.fetchone():
        print("✅ admin用户已存在")
        return True
    
    # 创建admin用户 (简单哈希)
    import hashlib
    password = "admin123"
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    c.execute("""
        INSERT INTO users (username, email, hashed_password, status, user_type, is_active, is_verified, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "admin", "admin@example.com", password_hash, "active", "admin", 1, 1, 
        time.strftime("%Y-%m-%d %H:%M:%S"), time.strftime("%Y-%m-%d %H:%M:%S")
    ))
    
    conn.commit()
    conn.close()
    print("✅ 创建admin用户成功")
    return True

def login():
    """登录获取token"""
    url = f"{BASE_URL}{API_PREFIX}/auth/login"
    data = {"username": "admin", "password": "admin123"}
    
    try:
        resp = requests.post(url, json=data, timeout=5)
        print(f"登录响应: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            if result.get("code") == 200:
                token = result["data"]["access_token"]
                print(f"✅ 登录成功，token: {token[:50]}...")
                return token
            else:
                print(f"❌ 登录失败: {result.get('message')}")
        else:
            print(f"❌ 登录HTTP错误: {resp.status_code}, 内容: {resp.text[:200]}")
    except Exception as e:
        print(f"❌ 登录异常: {e}")
    
    return None

def create_data_source(token):
    """创建500彩票数据源"""
    url = f"{BASE_URL}{API_PREFIX}/crawler/sources/five-hundred-create"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        resp = requests.post(url, headers=headers, timeout=5)
        print(f"创建数据源响应: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            if "message" in result:
                print("✅ 数据源创建成功")
                return result.get("source_id")
        else:
            print(f"❌ 创建数据源失败: {resp.status_code}, 内容: {resp.text[:200]}")
    except Exception as e:
        print(f"❌ 创建数据源异常: {e}")
    
    return None

def create_crawler_task(token):
    """创建爬虫任务"""
    url = f"{BASE_URL}{API_PREFIX}/crawler/tasks/five-hundred-create"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    data = {
        "name": "500彩票网竞彩足球近三天赛程抓取",
        "description": "从500彩票网抓取未来三天的竞彩足球比赛赛程",
        "config": {"days": 3, "priority": "high"}
    }
    
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=5)
        print(f"创建任务响应: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            if "message" in result and "成功" in result["message"]:
                print("✅ 爬虫任务创建成功")
                return result.get("task_id")
        else:
            print(f"❌ 创建任务失败: {resp.status_code}, 内容: {resp.text[:200]}")
    except Exception as e:
        print(f"❌ 创建任务异常: {e}")
    
    return None

def execute_crawler_task(token, task_id):
    """执行爬虫任务"""
    url = f"{BASE_URL}{API_PREFIX}/crawler/tasks/{task_id}/execute-five-hundred-crawl"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        resp = requests.post(url, headers=headers, timeout=10)
        print(f"执行任务响应: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            if "message" in result and "成功" in result["message"]:
                print("✅ 爬虫任务执行成功")
                return True
        else:
            print(f"❌ 执行任务失败: {resp.status_code}, 内容: {resp.text[:200]}")
    except Exception as e:
        print(f"❌ 执行任务异常: {e}")
    
    return False

def check_matches():
    """检查比赛数据"""
    url = f"{BASE_URL}{API_PREFIX}/matches"
    
    try:
        resp = requests.get(url, timeout=5)
        print(f"检查比赛数据响应: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            if result.get("code") == 200:
                matches = result.get("data", {}).get("items", [])
                print(f"✅ 发现 {len(matches)} 条比赛数据")
                if matches:
                    print("示例比赛:")
                    for match in matches[:3]:
                        print(f"  - {match.get('home_team')} vs {match.get('away_team')} ({match.get('match_time')})")
                return len(matches) > 0
            else:
                print(f"❌ 获取比赛数据失败: {result.get('message')}")
        else:
            print(f"❌ 获取比赛数据HTTP错误: {resp.status_code}")
    except Exception as e:
        print(f"❌ 检查比赛数据异常: {e}")
    
    return False

def main():
    print("=" * 60)
    print("模拟用户操作：数据源管理 + 任务台管理 + 执行抓取")
    print("=" * 60)
    
    # 启动后端
    print("\n1. 启动后端服务...")
    backend_proc = start_backend()
    if not backend_proc:
        print("❌ 后端服务启动失败，退出")
        return
    
    # 等待服务稳定
    time.sleep(3)
    
    # 创建管理员用户
    print("\n2. 创建管理员用户...")
    if not create_admin_user():
        print("⚠️ 管理员用户创建失败，可能已存在")
    
    # 登录
    print("\n3. 登录获取token...")
    token = login()
    if not token:
        print("❌ 登录失败，退出")
        backend_proc.terminate()
        return
    
    # 创建数据源
    print("\n4. 在数据源管理页面新增数据源...")
    source_id = create_data_source(token)
    
    # 创建任务
    print("\n5. 在任务台管理页面新增任务...")
    task_id = create_crawler_task(token)
    if not task_id:
        task_id = 1  # 默认任务ID
    
    # 执行抓取
    print("\n6. 执行抓取任务...")
    if execute_crawler_task(token, task_id):
        print("✅ 抓取任务执行成功")
    else:
        print("⚠️ 抓取任务执行可能失败")
    
    # 检查竞彩赛程页面数据
    print("\n7. 检查竞彩赛程页面数据...")
    time.sleep(2)
    if check_matches():
        print("\n🎉 成功！在竞彩赛程页面看到真实数据！")
    else:
        print("\n⚠️ 竞彩赛程页面没有数据，可能需要检查爬虫或手动抓取")
    
    # 停止后端
    print("\n8. 停止后端服务...")
    backend_proc.terminate()
    print("✅ 模拟操作完成")

if __name__ == "__main__":
    main()