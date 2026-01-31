import requests
import json
import time
import sys
import os
import subprocess
from typing import Optional

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

class CrawlerSimulator:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.headers = {}
        
    def login(self, username="admin", password="admin123"):
        """登录获取token"""
        url = f"{BASE_URL}{API_PREFIX}/auth/login"
        data = {
            "username": username,
            "password": password
        }
        
        print(f"登录 {url}...")
        try:
            response = self.session.post(url, json=data)
            print(f"登录响应状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    self.token = result["data"]["access_token"]
                    self.headers = {
                        "Authorization": f"Bearer {self.token}",
                        "Content-Type": "application/json"
                    }
                    print("✅ 登录成功")
                    print(f"Token: {self.token[:50]}...")
                    return True
                else:
                    print(f"❌ 登录失败: {result.get('message')}")
            else:
                print(f"❌ 登录HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"❌ 登录异常: {e}")
        return False
    
    def create_data_source(self):
        """创建数据源：500万彩票"""
        url = f"{BASE_URL}{API_PREFIX}/crawler/sources/five-hundred-create"
        
        print(f"创建数据源 {url}...")
        try:
            response = self.session.post(url, headers=self.headers)
            print(f"创建数据源响应状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                if "message" in result and "成功" in result["message"]:
                    print("✅ 数据源创建成功")
                    return result.get("source_id")
                else:
                    print("⚠️ 数据源可能已存在")
                    return None
            else:
                print(f"❌ 创建数据源失败: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"❌ 创建数据源异常: {e}")
        return None
    
    def create_crawler_task(self):
        """创建爬虫任务：从500抓取近三天比赛赛程"""
        url = f"{BASE_URL}{API_PREFIX}/crawler/tasks/five-hundred-create"
        
        task_data = {
            "name": "500彩票网竞彩足球近三天赛程抓取",
            "description": "从500彩票网抓取未来三天的竞彩足球比赛赛程",
            "config": {
                "days": 3,
                "priority": "high"
            }
        }
        
        print(f"创建爬虫任务 {url}...")
        try:
            response = self.session.post(url, json=task_data, headers=self.headers)
            print(f"创建任务响应状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                if "message" in result and "成功" in result["message"]:
                    print("✅ 爬虫任务创建成功")
                    return result.get("task_id")
                else:
                    print("❌ 爬虫任务创建失败")
            else:
                print(f"❌ 创建任务失败: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"❌ 创建任务异常: {e}")
        return None
    
    def execute_crawler_task(self, task_id: int):
        """执行爬虫任务"""
        url = f"{BASE_URL}{API_PREFIX}/crawler/tasks/{task_id}/execute-five-hundred-crawl"
        
        print(f"执行爬虫任务 {url}...")
        try:
            response = self.session.post(url, headers=self.headers)
            print(f"执行任务响应状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                if "message" in result and "成功" in result["message"]:
                    print("✅ 爬虫任务执行成功")
                    return True
                else:
                    print("❌ 爬虫任务执行失败")
            else:
                print(f"❌ 执行任务失败: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"❌ 执行任务异常: {e}")
        return False
    
    def check_matches(self):
        """检查竞彩赛程页面数据"""
        url = f"{BASE_URL}{API_PREFIX}/matches"
        
        print(f"检查比赛数据 {url}...")
        try:
            response = self.session.get(url)
            print(f"检查数据响应状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
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
                print(f"❌ 获取比赛数据HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"❌ 检查比赛数据异常: {e}")
        return False

def start_backend():
    """启动后端服务"""
    print("启动后端服务...")
    # 切换到backend目录
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    # 启动进程
    proc = subprocess.Popen([sys.executable, 'main.py'], 
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          text=True)
    
    # 等待服务启动
    time.sleep(8)
    
    # 检查进程是否存活
    if proc.poll() is None:
        print(f"✅ 后端服务启动成功，PID: {proc.pid}")
        return proc
    else:
        # 读取输出
        stdout, _ = proc.communicate()
        print("❌ 后端服务启动失败")
        print("输出:", stdout[:1000])
        return None

def main():
    print("=" * 60)
    print("模拟用户操作：数据源管理 + 任务台管理 + 执行抓取")
    print("=" * 60)
    
    # 启动后端服务
    backend_proc = start_backend()
    if not backend_proc:
        print("❌ 无法启动后端服务，请手动检查")
        return
    
    simulator = CrawlerSimulator()
    
    # 1. 登录
    if not simulator.login():
        print("❌ 登录失败，终止操作")
        return
    
    # 2. 创建数据源
    source_id = simulator.create_data_source()
    
    # 3. 创建任务
    task_id = simulator.create_crawler_task()
    if not task_id:
        print("❌ 创建任务失败，尝试使用默认任务ID=1")
        task_id = 1
    
    # 4. 执行抓取
    if simulator.execute_crawler_task(task_id):
        print("✅ 抓取任务执行成功")
    else:
        print("⚠️ 抓取任务执行可能失败，继续检查数据")
    
    # 5. 检查竞彩赛程页面数据
    print("\n" + "=" * 60)
    print("检查竞彩赛程页面数据...")
    if simulator.check_matches():
        print("✅ 成功在竞彩赛程页面看到真实数据！")
    else:
        print("❌ 竞彩赛程页面没有数据，可能需要手动抓取或检查爬虫")
    
    # 停止后端服务
    if backend_proc:
        backend_proc.terminate()
        print("后端服务已停止")

if __name__ == "__main__":
    main()