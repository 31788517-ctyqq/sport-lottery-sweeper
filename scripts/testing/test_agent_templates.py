#!/usr/bin/env python3
"""
测试智能体模板管理API
"""
import sys
import os
import requests
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:8000/api/v1/agents"

def test_api_health():
    """测试API健康检查"""
    try:
        # 测试基础健康检查
        health_url = "http://localhost:8000/api/v1/health"
        response = requests.get(health_url, timeout=5)
        print(f"API健康检查: {response.status_code}")
        if response.status_code == 200:
            print(f"响应: {response.json()}")
            return True
        else:
            print(f"API健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"API健康检查异常: {e}")
        return False

def test_agent_templates_endpoints():
    """测试智能体模板API端点"""
    
    # 首先尝试登录获取token（如果需要）
    auth_token = None
    try:
        login_url = "http://localhost:8000/api/v1/auth/login"
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(login_url, json=login_data, timeout=5)
        if response.status_code == 200:
            auth_token = response.json().get("access_token")
            print(f"获取到认证token: {auth_token[:20]}...")
    except Exception as e:
        print(f"登录测试失败（可能不需要认证）: {e}")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    print("\n=== 测试智能体模板管理API ===")
    
    # 1. 获取模板列表
    print("1. 获取智能体模板列表...")
    try:
        response = requests.get(f"{BASE_URL}/templates", headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            templates = response.json()
            print(f"获取到 {templates.get('total', 0)} 个模板")
            print("模板列表测试通过")
            return True
        elif response.status_code == 403:
            print("没有权限访问API（正常情况，需要认证）")
        elif response.status_code == 404:
            print("API端点不存在（需要检查路由注册）")
        else:
            print(f"未预期的状态码: {response.status_code}")
            print(f"响应: {response.text[:200]}")
    except Exception as e:
        print(f"获取模板列表异常: {e}")
    
    return False

def test_create_agent_template():
    """测试创建智能体模板"""
    print("\n2. 测试创建智能体模板...")
    
    headers = {"Content-Type": "application/json"}
    
    template_data = {
        "name": "test_monitor_template",
        "display_name": "测试监控模板",
        "description": "这是一个测试智能体模板",
        "template_type": "monitor",
        "template_config": {"interval": 300, "alert_threshold": 0.1},
        "agent_config": {"max_retries": 3, "timeout": 5000},
        "chain_config": {"nodes": ["collector", "analyzer", "reporter"]},
        "tool_config": {"logging": True, "notifications": ["email", "slack"]},
        "tags": ["测试", "监控", "模板"],
        "category": "监控",
        "difficulty": "easy",
        "published": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/templates",
            json=template_data,
            headers=headers,
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        if response.status_code in [200, 201]:
            created_template = response.json()
            print(f"创建模板成功: {created_template.get('name')} (ID: {created_template.get('id')})")
            return created_template.get('id')
        else:
            print(f"创建模板失败: {response.text[:200]}")
    except Exception as e:
        print(f"创建模板异常: {e}")
    
    return None

def main():
    """主测试函数"""
    print("开始测试智能体模板管理API...")
    
    # 检查API是否健康
    if not test_api_health():
        print("API健康检查失败，请确保后端服务正在运行")
        print("启动命令: python backend/main.py")
        sys.exit(1)
    
    # 测试模板API端点
    if test_agent_templates_endpoints():
        print("\n✅ 智能体模板API端点测试通过")
        
        # 测试创建模板
        template_id = test_create_agent_template()
        if template_id:
            print(f"\n✅ 成功创建智能体模板，ID: {template_id}")
            
            # 测试获取模板详情
            print(f"\n3. 获取模板详情 (ID: {template_id})...")
            try:
                response = requests.get(f"{BASE_URL}/templates/{template_id}", timeout=10)
                if response.status_code == 200:
                    template_detail = response.json()
                    print(f"获取模板详情成功: {template_detail.get('name')}")
                    print(f"描述: {template_detail.get('description')}")
                    print("✅ 模板详情测试通过")
            except Exception as e:
                print(f"获取模板详情异常: {e}")
    else:
        print("\n❌ 智能体模板API端点测试失败")
        
        # 检查路由是否注册
        print("\n检查路由注册情况...")
        try:
            # 检查基础路由是否存在
            response = requests.get(BASE_URL, timeout=5)
            print(f"基础智能体路由状态: {response.status_code}")
        except Exception as e:
            print(f"基础智能体路由不可访问: {e}")
    
    print("\n测试完成")

if __name__ == "__main__":
    main()