#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
任务功能测试脚本
用于验证任务相关的各项功能是否正常工作
"""

import requests
import json
import time
from datetime import datetime

# 定义API基础URL
BASE_URL = "http://localhost:8000/api/admin/crawler/tasks"

def test_task_endpoints():
    """测试任务相关的各个端点"""
    print("=" * 60)
    print("开始测试任务功能")
    print("=" * 60)
    
    # 1. 测试获取任务列表
    print("\n1. 测试获取任务列表...")
    try:
        response = requests.get(BASE_URL, params={"page": 1, "size": 10})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 成功获取任务列表，共 {data.get('data', {}).get('total', 0)} 个任务")
            if data.get('data', {}).get('items'):
                print(f"   - 第一个任务: {data['data']['items'][0].get('name', 'N/A')} (ID: {data['data']['items'][0].get('id', 'N/A')})")
        else:
            print(f"   ✗ 获取任务列表失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 获取任务列表时发生错误: {e}")
    
    # 2. 测试获取任务统计
    print("\n2. 测试获取任务统计...")
    try:
        stats_url = f"{BASE_URL}/statistics"
        response = requests.get(stats_url)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 成功获取任务统计数据")
            print(f"   - 总任务数: {data.get('data', {}).get('totalTasks', 0)}")
            print(f"   - 状态统计: {data.get('data', {}).get('statusStats', {})}")
        else:
            print(f"   ✗ 获取任务统计失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 获取任务统计时发生错误: {e}")
    
    # 3. 测试创建任务（使用测试数据源）
    print("\n3. 测试创建任务...")
    try:
        # 先获取一个数据源
        sources_response = requests.get("http://localhost:8000/api/v1/admin/sources?page=1&size=1")
        if sources_response.status_code == 200:
            sources_data = sources_response.json()
            if sources_data.get('data', {}).get('items'):
                source = sources_data['data']['items'][0]
                source_id = source['id']
                
                # 创建一个测试任务
                task_data = {
                    "name": f"Test Task {int(time.time())}",
                    "source_id": source_id,
                    "task_type": "DATA_COLLECTION",
                    "cron_expression": "*/5 * * * *",  # 每5分钟执行一次
                    "config": {"timeout": 30, "retry_count": 3}
                }
                
                response = requests.post(BASE_URL, json=task_data)
                if response.status_code == 200:
                    task = response.json()['data']
                    task_id = task['id']
                    print(f"   ✓ 成功创建任务: {task['name']} (ID: {task_id})")
                    
                    # 4. 测试触发任务
                    print(f"\n4. 测试触发任务 (ID: {task_id})...")
                    try:
                        trigger_response = requests.post(f"{BASE_URL}/{task_id}/trigger")
                        if trigger_response.status_code == 200:
                            result = trigger_response.json()
                            print(f"   ✓ 成功触发任务: {result.get('message', 'Unknown')}")
                        else:
                            print(f"   ✗ 触发任务失败，状态码: {trigger_response.status_code}")
                    except Exception as e:
                        print(f"   ✗ 触发任务时发生错误: {e}")
                    
                    # 5. 测试获取任务日志
                    print(f"\n5. 测试获取任务日志 (ID: {task_id})...")
                    try:
                        logs_response = requests.get(f"{BASE_URL}/{task_id}/logs", params={"page": 1, "size": 10})
                        if logs_response.status_code == 200:
                            logs_data = logs_response.json()
                            print(f"   ✓ 成功获取任务日志，共 {logs_data.get('data', {}).get('total', 0)} 条记录")
                        else:
                            print(f"   ✗ 获取任务日志失败，状态码: {logs_response.status_code}")
                    except Exception as e:
                        print(f"   ✗ 获取任务日志时发生错误: {e}")
                    
                    # 6. 测试停止任务
                    print(f"\n6. 测试停止任务 (ID: {task_id})...")
                    try:
                        stop_response = requests.post(f"{BASE_URL}/{task_id}/stop")
                        if stop_response.status_code == 200:
                            result = stop_response.json()
                            print(f"   ✓ 成功停止任务: {result.get('message', 'Unknown')}")
                        else:
                            print(f"   ✗ 停止任务失败，状态码: {stop_response.status_code}")
                    except Exception as e:
                        print(f"   ✗ 停止任务时发生错误: {e}")
                    
                    # 7. 测试删除任务
                    print(f"\n7. 测试删除任务 (ID: {task_id})...")
                    try:
                        delete_response = requests.delete(f"{BASE_URL}/{task_id}")
                        if delete_response.status_code == 200:
                            print(f"   ✓ 成功删除任务")
                        else:
                            print(f"   ✗ 删除任务失败，状态码: {delete_response.status_code}")
                    except Exception as e:
                        print(f"   ✗ 删除任务时发生错误: {e}")
                else:
                    print(f"   ✗ 创建任务失败，状态码: {response.status_code}")
            else:
                print("   ! 没有可用的数据源来创建测试任务")
        else:
            print(f"   ! 获取数据源失败，状态码: {sources_response.status_code}")
    except Exception as e:
        print(f"   ✗ 创建任务时发生错误: {e}")
    
    print("\n" + "=" * 60)
    print("任务功能测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_task_endpoints()