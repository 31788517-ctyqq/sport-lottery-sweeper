#!/usr/bin/env python3
"""
快速创建数据源和任务脚本
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"

def create_data_source():
    """创建500彩票数据源"""
    url = f"{BASE_URL}/crawler/sources"
    data = {
        "name": "500万彩票",
        "category": "竞彩赛程",
        "url": "https://trade.500.com/jczq/",
        "config": {
            "crawler_type": "500_com",
            "enabled": True,
            "priority": 1
        },
        "status": "active",
        "createTime": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        print(f"创建数据源: {data['name']}")
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print(f"数据源创建成功: {response.json()}")
            return response.json()['data']['id']
        else:
            print(f"数据源创建失败: {response.status_code} - {response.text}")
            # 尝试获取现有数据源
            list_url = f"{BASE_URL}/crawler/sources"
            list_resp = requests.get(list_url)
            if list_resp.status_code == 200:
                sources = list_resp.json()['data']
                for source in sources:
                    if source.get('name') == '500万彩票':
                        return source.get('id')
            return None
    except Exception as e:
        print(f"创建数据源异常: {e}")
        return None

def create_crawler_task(source_id):
    """创建抓取任务"""
    url = f"{BASE_URL}/crawler/tasks"
    data = {
        "task_name": "抓取近三天比赛赛程",
        "source": "500wan",
        "schedule": "0 */2 * * *",  # 每2小时执行一次
        "enabled": True,
        "config": {
            "days": 3,
            "category": "竞彩赛程",
            "priority": "high"
        }
    }
    
    try:
        print(f"创建抓取任务: {data['task_name']}")
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print(f"任务创建成功: {response.json()}")
            return response.json()['data']['id']
        else:
            print(f"任务创建失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"创建任务异常: {e}")
        return None

def execute_crawler(task_id):
    """执行抓取任务"""
    url = f"{BASE_URL}/crawler/tasks/{task_id}/execute"
    
    try:
        print(f"执行抓取任务 ID: {task_id}")
        response = requests.post(url)
        if response.status_code == 200:
            print(f"任务执行成功: {response.json()}")
            return True
        else:
            print(f"任务执行失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"执行任务异常: {e}")
        return False

def check_lottery_data():
    """检查竞彩数据是否可用"""
    url = f"{BASE_URL}/lottery/matches-final"
    params = {
        "source": "500",
        "page": 1,
        "size": 10
    }
    
    try:
        print("检查竞彩数据...")
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            matches = data.get('data', {}).get('data', [])
            if matches:
                print(f"成功获取 {len(matches)} 场比赛数据")
                for match in matches[:3]:
                    print(f"  {match.get('home_team')} vs {match.get('away_team')} - {match.get('match_time')}")
                return True
            else:
                print("未找到比赛数据")
                return False
        else:
            print(f"检查数据失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"检查数据异常: {e}")
        return False

def main():
    print("=== 快速创建数据源和任务 ===")
    
    # 检查服务是否运行
    try:
        health_resp = requests.get("http://localhost:8000/health/live", timeout=5)
        if health_resp.status_code != 200:
            print("后端服务未运行，请先启动服务")
            return
    except:
        print("后端服务未运行，请先启动服务")
        return
    
    # 创建数据源
    source_id = create_data_source()
    if not source_id:
        print("数据源创建失败，使用现有数据源或跳过")
    
    # 创建任务
    task_id = create_crawler_task(source_id)
    
    # 执行抓取
    if task_id:
        execute_crawler(task_id)
    
    # 等待数据加载
    print("等待数据加载...")
    time.sleep(3)
    
    # 检查数据
    if check_lottery_data():
        print("✅ 数据已准备就绪，可以在竞彩赛程页面查看")
    else:
        print("❌ 数据加载失败，请检查爬虫服务")
    
    print("=== 完成 ===")

if __name__ == "__main__":
    main()