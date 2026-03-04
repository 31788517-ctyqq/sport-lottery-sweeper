#!/usr/bin/env python3
"""
模拟用户操作测试脚本
目标：按照用户指定的操作路径，模拟用户完成数据源和任务的创建流程
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# 配置
BASE_URL = "http://localhost:8000"
API_TIMEOUT = 10

def print_step(step_num: int, title: str):
    """打印步骤标题"""
    print(f"\n{'='*60}")
    print(f"步骤 {step_num}: {title}")
    print(f"{'='*60}")

def check_backend_status():
    """检查后端服务状态"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=API_TIMEOUT)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            return True
        else:
            print(f"❌ 后端服务状态异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到后端服务: {e}")
        print(f"请确保后端服务正在运行在 {BASE_URL}")
        return False

def admin_login():
    """管理员登录"""
    print("尝试使用默认管理员账户登录...")
    
    # 首先检查数据库是否存在管理员账户
    try:
        response = requests.get(f"{BASE_URL}/api/v1/users", timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"用户列表: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print("无法获取用户列表")
    
    # 尝试默认管理员账户
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                access_token = data["data"]["access_token"]
                user_info = data["data"]["user_info"]
                print(f"✅ 管理员登录成功!")
                print(f"   用户名: {user_info.get('username')}")
                print(f"   角色: {user_info.get('roles')}")
                print(f"   访问令牌: {access_token[:50]}...")
                return access_token
            else:
                print(f"❌ 登录失败: {data.get('message')}")
        else:
            print(f"❌ 登录请求失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误详情: {error_data}")
            except:
                print(f"   响应内容: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ 登录请求异常: {e}")
    
    return None

def create_data_source(access_token: str) -> Optional[int]:
    """创建数据源"""
    print("\n准备创建数据源...")
    
    # 数据源信息 - 使用100球网的API地址
    data_source_data = {
        "name": "100球网比赛数据API",
        "type": "api",
        "url": "https://m.100qiu.com/api/dcListBasic",
        "config": {
            "method": "GET",
            "timeout": 30,
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            "params": {
                "dateTime": "26011"  # 示例参数
            },
            "description": "100球网比赛数据API，用于获取足球比赛信息"
        },
        "status": True
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # 注意：API端点可能需要调整，根据之前的搜索结果有多个端点
        # 尝试使用 /api/v1/admin/sources 端点
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/sources",
            json=data_source_data,
            headers=headers,
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            if data.get("success") or response.status_code == 201:
                source_id = data.get("data", {}).get("id")
                if source_id:
                    print(f"✅ 数据源创建成功!")
                    print(f"   数据源ID: {source_id}")
                    print(f"   数据源名称: {data_source_data['name']}")
                    print(f"   数据源URL: {data_source_data['url']}")
                    return source_id
                else:
                    print(f"⚠️  数据源可能创建成功，但未返回ID: {data}")
                    # 尝试从响应中解析
                    if "data" in data and isinstance(data["data"], dict):
                        source_id = data["data"].get("id")
                        if source_id:
                            return source_id
            else:
                print(f"❌ 数据源创建失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ 数据源创建请求失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误详情: {error_data}")
            except:
                print(f"   响应内容: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ 数据源创建请求异常: {e}")
    
    # 如果主端点失败，尝试其他端点
    print("\n尝试使用备用端点创建数据源...")
    try:
        # 尝试 /api/v1/data-sources 端点
        response = requests.post(
            f"{BASE_URL}/api/v1/data-sources",
            json=data_source_data,
            headers=headers,
            timeout=API_TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"备用端点响应: {json.dumps(data, ensure_ascii=False)}")
            
            # 尝试从响应中获取ID
            if "id" in data:
                source_id = data["id"]
                print(f"✅ 使用备用端点创建数据源成功! ID: {source_id}")
                return source_id
            elif "data" in data and "id" in data["data"]:
                source_id = data["data"]["id"]
                print(f"✅ 使用备用端点创建数据源成功! ID: {source_id}")
                return source_id
                
    except Exception as e:
        print(f"备用端点也失败: {e}")
    
    return None

def create_task(access_token: str, source_id: int) -> Optional[int]:
    """创建任务"""
    print(f"\n准备创建任务，使用数据源ID: {source_id}")
    
    # 任务信息
    task_data = {
        "name": "每日100球网数据采集",
        "source_id": source_id,
        "task_type": "crawl",
        "cron_expression": "0 2 * * *",  # 每天凌晨2点执行
        "config": json.dumps({
            "description": "每日定时采集100球网比赛数据",
            "params": {"dateTime": "26011"},
            "retry_count": 3,
            "timeout": 60
        })
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # 尝试 /api/v1/admin/tasks 端点
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/tasks",
            params=task_data,
            headers=headers,
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                task_id = data.get("data", {}).get("id")
                if task_id:
                    print(f"✅ 任务创建成功!")
                    print(f"   任务ID: {task_id}")
                    print(f"   任务名称: {task_data['name']}")
                    print(f"   Cron表达式: {task_data['cron_expression']}")
                    return task_id
            else:
                print(f"❌ 任务创建失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ 任务创建请求失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误详情: {error_data}")
            except:
                print(f"   响应内容: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ 任务创建请求异常: {e}")
    
    # 尝试备用端点
    print("\n尝试使用备用端点创建任务...")
    try:
        # 尝试 /api/v1/crawler/tasks 端点
        response = requests.post(
            f"{BASE_URL}/api/v1/crawler/tasks",
            json={
                "name": task_data["name"],
                "source_id": task_data["source_id"],
                "cron_expression": task_data["cron_expression"],
                "config": task_data["config"]
            },
            headers=headers,
            timeout=API_TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"备用端点响应: {json.dumps(data, ensure_ascii=False)}")
            
            # 尝试从响应中获取ID
            if "id" in data:
                task_id = data["id"]
                print(f"✅ 使用备用端点创建任务成功! ID: {task_id}")
                return task_id
            elif "data" in data and isinstance(data["data"], dict) and "id" in data["data"]:
                task_id = data["data"]["id"]
                print(f"✅ 使用备用端点创建任务成功! ID: {task_id}")
                return task_id
                
    except Exception as e:
        print(f"备用端点也失败: {e}")
    
    return None

def verify_data_source_exists(source_id: int) -> bool:
    """验证数据源是否存在"""
    print(f"\n验证数据源 {source_id} 是否存在...")
    
    try:
        # 尝试多个端点
        endpoints = [
            f"{BASE_URL}/api/v1/admin/sources/{source_id}",
            f"{BASE_URL}/api/v1/data-sources/{source_id}",
            f"{BASE_URL}/api/v1/crawler/sources/{source_id}"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=API_TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 数据源验证成功 (端点: {endpoint})")
                    print(f"   数据源详情: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    return True
            except:
                continue
        
        print("❌ 数据源验证失败，所有端点都无响应")
        return False
        
    except Exception as e:
        print(f"❌ 数据源验证异常: {e}")
        return False

def verify_task_exists(task_id: int) -> bool:
    """验证任务是否存在"""
    print(f"\n验证任务 {task_id} 是否存在...")
    
    try:
        # 尝试多个端点
        endpoints = [
            f"{BASE_URL}/api/v1/admin/tasks/{task_id}",
            f"{BASE_URL}/api/v1/crawler/tasks/{task_id}"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=API_TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 任务验证成功 (端点: {endpoint})")
                    print(f"   任务详情: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    return True
            except:
                continue
        
        print("❌ 任务验证失败，所有端点都无响应")
        return False
        
    except Exception as e:
        print(f"❌ 任务验证异常: {e}")
        return False

def test_100qiu_api():
    """测试100球网API是否可访问"""
    print("\n测试100球网API...")
    
    try:
        response = requests.get(
            "https://m.100qiu.com/api/dcListBasic?dateTime=26011",
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 100球网API测试成功!")
            print(f"   状态码: {response.status_code}")
            print(f"   响应类型: {type(data)}")
            
            # 检查数据结构
            if isinstance(data, list):
                print(f"   数据条数: {len(data)}")
                if len(data) > 0:
                    print(f"   示例数据字段: {list(data[0].keys())}")
            elif isinstance(data, dict):
                print(f"   数据字段: {list(data.keys())}")
            
            return True
        else:
            print(f"❌ 100球网API测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 100球网API测试异常: {e}")
        return False

def main():
    """主测试流程"""
    print(f"{'#'*70}")
    print("模拟用户操作测试")
    print(f"测试目标: 模拟用户完成数据源和任务的创建流程")
    print(f"后端地址: {BASE_URL}")
    print(f"{'#'*70}")
    
    # 检查后端状态
    if not check_backend_status():
        print("\n❌ 后端服务不可用，测试终止")
        return False
    
    # 测试100球网API
    if not test_100qiu_api():
        print("\n⚠️  100球网API不可访问，但继续测试本地API")
    
    # 管理员登录
    print_step(1, "管理员登录")
    access_token = admin_login()
    if not access_token:
        print("\n❌ 管理员登录失败，测试终止")
        return False
    
    # 创建数据源
    print_step(2, "创建数据源")
    source_id = create_data_source(access_token)
    if not source_id:
        print("\n❌ 数据源创建失败，测试终止")
        return False
    
    # 验证数据源
    if not verify_data_source_exists(source_id):
        print("⚠️  数据源存在性验证失败，但继续测试")
    
    # 创建任务
    print_step(3, "创建任务")
    task_id = create_task(access_token, source_id)
    if not task_id:
        print("\n❌ 任务创建失败")
        return False
    
    # 验证任务
    if not verify_task_exists(task_id):
        print("⚠️  任务存在性验证失败")
    
    # 最终汇总
    print_step(4, "测试结果汇总")
    print("✅ 模拟用户操作测试完成!")
    print(f"   创建的数据源ID: {source_id}")
    print(f"   创建的任务ID: {task_id}")
    print(f"   数据源API地址: https://m.100qiu.com/api/dcListBasic?dateTime=26011")
    print(f"\n用户操作路径验证:")
    print("   ✅ 第一步: 管理员登录成功")
    print(f"   ✅ 第二步: 创建数据源成功 (ID: {source_id})")
    print(f"   ✅ 第三步: 创建任务成功 (ID: {task_id})")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试发生未预期异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)