#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
任务监控API测试脚本
用于验证task-monitor相关API端点是否正常工作
"""

import requests
import json
import time
from datetime import datetime

# 定义API基础URL
BASE_URL = "http://localhost:8000"

def test_task_monitor_endpoints():
    """测试任务监控相关的各个端点"""
    print("=" * 60)
    print("开始测试任务监控API")
    print("=" * 60)
    
    # 1. 测试获取任务执行列表
    print("\n1. 测试获取任务执行列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/task-monitor/executions", params={"page": 1, "page_size": 10})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 成功获取任务执行列表，共 {data.get('data', {}).get('total', 0)} 个执行记录")
            if data.get('data', {}).get('items'):
                print(f"   - 第一个执行: {data['data']['items'][0].get('task_name', 'N/A')} (ID: {data['data']['items'][0].get('id', 'N/A')})")
        else:
            print(f"   ✗ 获取任务执行列表失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 获取任务执行列表时发生错误: {e}")
    
    # 2. 测试获取实时概览
    print("\n2. 测试获取实时概览...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/task-monitor/realtime/overview")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 成功获取实时概览")
            overview = data.get('data', {})
            print(f"   - 运行中任务: {overview.get('running_tasks', 0)}")
            print(f"   - 今日总计: {overview.get('today_total', 0)}")
            print(f"   - 成功率: {overview.get('success_rate', 0)}%")
        else:
            print(f"   ✗ 获取实时概览失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 获取实时概览时发生错误: {e}")
    
    # 3. 测试获取每日统计
    print("\n3. 测试获取每日统计...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/task-monitor/statistics/daily")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 成功获取每日统计数据，共 {len(data.get('data', []))} 天的数据")
        else:
            print(f"   ✗ 获取每日统计失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 获取每日统计时发生错误: {e}")
    
    # 4. 测试获取主要问题排行
    print("\n4. 测试获取主要问题排行...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/task-monitor/statistics/top-issues")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 成功获取问题排行数据，共 {len(data.get('data', []))} 个问题")
        else:
            print(f"   ✗ 获取问题排行失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 获取问题排行时发生错误: {e}")
    
    print("\n" + "=" * 60)
    print("任务监控API测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_task_monitor_endpoints()