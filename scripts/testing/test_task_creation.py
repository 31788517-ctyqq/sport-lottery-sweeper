#!/usr/bin/env python3
"""
测试任务创建功能
"""
import requests
import json

base_url = "http://localhost:8000"

def get_auth_token():
    """获取管理员令牌"""
    login_data = {"username": "admin", "password": "admin123"}
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("access_token")
        else:
            print(f"登录失败: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"登录请求异常: {e}")
        return None

def create_task(token, name, source_id, task_type, cron_expression, config):
    """创建任务"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 注意：API使用查询参数，不是请求体
    params = {
        "name": name,
        "source_id": source_id,
        "task_type": task_type,
        "cron_expression": cron_expression,
        "config": json.dumps(config)  # 需要序列化为JSON字符串
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/admin/tasks", params=params, headers=headers, timeout=10)
        print(f"创建任务响应: 状态码 {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            task_id = data.get("data", {}).get("id")
            print(f"✅ 任务创建成功! 任务ID: {task_id}")
            return task_id
        else:
            print(f"❌ 任务创建失败")
            return None
    except Exception as e:
        print(f"🚨 创建任务请求异常: {e}")
        return None

def list_tasks(token):
    """获取任务列表"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{base_url}/api/v1/admin/tasks", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            items = data.get("data", {}).get("items", [])
            print(f"任务列表: 共 {len(items)} 个任务")
            for task in items:
                print(f"  - ID: {task.get('id')}, 名称: {task.get('name')}, 状态: {task.get('status')}")
            return items
        else:
            print(f"获取任务列表失败: {response.status_code} - {response.text[:200]}")
            return []
    except Exception as e:
        print(f"获取任务列表异常: {e}")
        return []

def main():
    print("="*60)
    print("任务创建功能测试")
    print("="*60)
    
    # 1. 获取令牌
    print("\n1. 获取管理员令牌...")
    token = get_auth_token()
    if not token:
        print("❌ 无法获取令牌，测试终止")
        return
    
    print(f"✅ 令牌获取成功: {token[:50]}...")
    
    # 2. 查看现有任务
    print("\n2. 查看现有任务列表...")
    existing_tasks = list_tasks(token)
    
    # 3. 创建新任务
    print("\n3. 创建新任务...")
    task_config = {
        "description": "每日采集100球网比赛数据",
        "params": {
            "dateTime": "26011"
        },
        "retry_count": 3,
        "timeout": 60
    }
    
    task_id = create_task(
        token=token,
        name="采集100球网数据",
        source_id=7,  # 使用之前创建的100球网数据源ID
        task_type="crawl",
        cron_expression="0 2 * * *",
        config=task_config
    )
    
    # 4. 验证任务创建
    if task_id:
        print("\n4. 验证任务创建结果...")
        # 等待一下让数据库更新
        import time
        time.sleep(1)
        
        updated_tasks = list_tasks(token)
        if len(updated_tasks) > len(existing_tasks):
            print(f"✅ 任务已成功添加到列表! 新增 {len(updated_tasks) - len(existing_tasks)} 个任务")
        else:
            print("⚠️  任务列表未更新，可能需要检查数据库")
    else:
        print("\n⚠️ 任务创建失败，跳过验证")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()