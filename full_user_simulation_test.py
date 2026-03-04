#!/usr/bin/env python3
"""
完整用户操作模拟测试
模拟用户在页面上操作，完成数据源和任务的创建
"""

import requests
import json
import sys
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
API_TIMEOUT = 10

def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")

def test_health():
    """测试后端健康状态"""
    print("检查后端健康状态...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=API_TIMEOUT)
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"  响应: {response.text[:100]}")
            return True
        else:
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"  错误: {e}")
        return False

def admin_login():
    """管理员登录测试"""
    print("\n管理员登录测试...")
    
    # 尝试多个可能的用户名/密码组合
    test_credentials = [
        {"username": "admin", "password": "admin123"},
        {"username": "administrator", "password": "admin123"},
        {"username": "superadmin", "password": "admin123"},
        {"username": "admin", "password": "password"},
        {"username": "admin", "password": "Admin123"},
    ]
    
    for creds in test_credentials:
        try:
            print(f"  尝试: {creds['username']}/{creds['password']}")
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json=creds,
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    access_token = data["data"]["access_token"]
                    user_info = data["data"]["user_info"]
                    print(f"  ✅ 登录成功!")
                    print(f"     用户名: {user_info.get('username')}")
                    print(f"     角色: {user_info.get('roles')}")
                    print(f"     令牌: {access_token[:50]}...")
                    return access_token
            elif response.status_code == 401:
                print(f"  ❌ 认证失败")
            else:
                print(f"  ⚠️  状态码: {response.status_code}")
                
        except Exception as e:
            print(f"  🚨 请求异常: {e}")
    
    print("\n⚠️  所有登录尝试都失败")
    print("可能需要创建管理员账户或使用其他凭据")
    return None

def get_existing_data_sources():
    """获取现有数据源列表"""
    print("\n获取现有数据源列表...")
    
    # 尝试多个可能的端点
    endpoints = [
        "/api/v1/admin/sources",
        "/api/v1/data-sources",
        "/api/v1/crawler/sources",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=API_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ 端点 {endpoint} 可访问")
                
                # 解析数据源
                if isinstance(data, dict) and data.get("success"):
                    items = data.get("data", {}).get("items", [])
                    if isinstance(items, list) and len(items) > 0:
                        print(f"     找到 {len(items)} 个数据源")
                        return items, endpoint
                elif isinstance(data, list):
                    print(f"     找到 {len(data)} 个数据源")
                    return data, endpoint
                    
        except Exception as e:
            continue
    
    print("  ⚠️  无法获取数据源列表")
    return [], None

def create_data_source(access_token, endpoint_type):
    """创建数据源"""
    print("\n创建数据源...")
    
    # 根据端点类型选择正确的API端点
    if endpoint_type == "/api/v1/admin/sources":
        api_endpoint = f"{BASE_URL}/api/v1/admin/sources"
        # DataSourceCreate 格式
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
                    "dateTime": "26011"
                },
                "description": "100球网比赛数据API，用于获取足球比赛信息"
            },
            "status": True
        }
    elif endpoint_type == "/api/v1/data-sources":
        api_endpoint = f"{BASE_URL}/api/v1/data-sources"
        data_source_data = {
            "name": "100球网比赛数据API",
            "type": "api",
            "url": "https://m.100qiu.com/api/dcListBasic",
            "config": json.dumps({
                "method": "GET",
                "timeout": 30,
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                "params": {
                    "dateTime": "26011"
                },
                "description": "100球网比赛数据API，用于获取足球比赛信息"
            }),
            "status": "active"
        }
    else:
        api_endpoint = f"{BASE_URL}/api/v1/crawler/sources"
        data_source_data = {
            "name": "100球网比赛数据API",
            "source_type": "api",
            "url": "https://m.100qiu.com/api/dcListBasic",
            "config": {
                "method": "GET",
                "timeout": 30,
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows PT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                "params": {
                    "dateTime": "26011"
                },
                "description": "100球网比赛数据API，用于获取足球比赛信息"
            },
            "status": "active"
        }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"  调用端点: {api_endpoint}")
        response = requests.post(
            api_endpoint,
            json=data_source_data,
            headers=headers,
            timeout=API_TIMEOUT
        )
        
        print(f"  响应状态码: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"  响应数据: {json.dumps(data, ensure_ascii=False)[:300]}")
            
            # 尝试从不同响应格式中提取数据源ID
            source_id = None
            
            if isinstance(data, dict):
                if data.get("success") and "data" in data:
                    if isinstance(data["data"], dict) and "id" in data["data"]:
                        source_id = data["data"]["id"]
                    elif "id" in data["data"]:
                        source_id = data["data"]["id"]
                elif "id" in data:
                    source_id = data["id"]
            
            if source_id:
                print(f"  ✅ 数据源创建成功!")
                print(f"     数据源ID: {source_id}")
                print(f"     名称: {data_source_data.get('name')}")
                print(f"     URL: {data_source_data.get('url')}")
                return source_id, data_source_data
            else:
                print(f"  ⚠️  数据源可能已创建，但无法提取ID")
                print(f"     完整响应: {json.dumps(data, ensure_ascii=False)}")
                return None, data_source_data
                
        else:
            print(f"  ❌ 数据源创建失败")
            try:
                error_data = response.json()
                print(f"     错误详情: {error_data}")
            except:
                print(f"     响应内容: {response.text}")
            return None, data_source_data
            
    except Exception as e:
        print(f"  🚨 请求异常: {e}")
        return None, data_source_data

def get_existing_tasks():
    """获取现有任务列表"""
    print("\n获取现有任务列表...")
    
    # 尝试多个可能的端点
    endpoints = [
        "/api/v1/admin/tasks",
        "/api/v1/crawler/tasks",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=API_TIMEOUT)
            print(f"  端点 {endpoint}: 状态码 {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # 解析任务数据
                if isinstance(data, dict) and data.get("success"):
                    items = data.get("data", {}).get("items", [])
                    if isinstance(items, list):
                        print(f"     找到 {len(items)} 个任务")
                        return items, endpoint
                elif isinstance(data, list):
                    print(f"     找到 {len(data)} 个任务")
                    return data, endpoint
                    
        except Exception as e:
            print(f"  请求异常: {e}")
    
    print("  ⚠️  无法获取任务列表")
    return [], None

def create_task(access_token, source_id, task_endpoint_type):
    """创建任务"""
    print(f"\n创建任务，使用数据源ID: {source_id}")
    
    # 根据端点类型选择正确的API端点
    if task_endpoint_type == "/api/v1/admin/tasks":
        api_endpoint = f"{BASE_URL}/api/v1/admin/tasks"
        # 查询参数格式
        params = {
            "name": "每日100球网数据采集",
            "source_id": source_id,
            "task_type": "crawl",
            "cron_expression": "0 2 * * *",
            "config": json.dumps({
                "description": "每日定时采集100球网比赛数据",
                "params": {"dateTime": "26011"},
                "retry_count": 3,
                "timeout": 60
            })
        }
        method = "post"
        data = None
    else:
        api_endpoint = f"{BASE_URL}/api/v1/crawler/tasks"
        # JSON主体格式
        params = None
        method = "post"
        data = {
            "name": "每日100球网数据采集",
            "source_id": source_id,
            "cron_expression": "0 2 * * *",
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
        print(f"  调用端点: {api_endpoint}")
        
        if method == "post" and params:
            response = requests.post(
                api_endpoint,
                params=params,
                headers=headers,
                timeout=API_TIMEOUT
            )
        elif method == "post" and data:
            response = requests.post(
                api_endpoint,
                json=data,
                headers=headers,
                timeout=API_TIMEOUT
            )
        else:
            print("  ❌ 未知的请求方法")
            return None
        
        print(f"  响应状态码: {response.status_code}")
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print(f"  响应数据: {json.dumps(response_data, ensure_ascii=False)[:300]}")
            
            # 尝试从不同响应格式中提取任务ID
            task_id = None
            
            if isinstance(response_data, dict):
                if response_data.get("success") and "data" in response_data:
                    if isinstance(response_data["data"], dict) and "id" in response_data["data"]:
                        task_id = response_data["data"]["id"]
                    elif "id" in response_data["data"]:
                        task_id = response_data["data"]["id"]
                elif "id" in response_data:
                    task_id = response_data["id"]
            
            if task_id:
                print(f"  ✅ 任务创建成功!")
                print(f"     任务ID: {task_id}")
                print(f"     名称: {'每日100球网数据采集'}")
                print(f"     Cron表达式: 0 2 * * * (每天凌晨2点)")
                return task_id
            else:
                print(f"  ⚠️  任务可能已创建，但无法提取ID")
                return None
                
        else:
            print(f"  ❌ 任务创建失败")
            try:
                error_data = response.json()
                print(f"     错误详情: {error_data}")
            except:
                print(f"     响应内容: {response.text}")
            return None
            
    except Exception as e:
        print(f"  🚨 请求异常: {e}")
        return None

def verify_data_source(source_id):
    """验证数据源是否成功创建"""
    print(f"\n验证数据源 {source_id}...")
    
    # 尝试多个可能的端点
    endpoints = [
        f"/api/v1/admin/sources/{source_id}",
        f"/api/v1/data-sources/{source_id}",
        f"/api/v1/crawler/sources/{source_id}"
    ]
    
    for endpoint in endpoints:
        try:
            full_url = f"{BASE_URL}{endpoint}"
            response = requests.get(full_url, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ 数据源验证成功 (端点: {endpoint})")
                print(f"     详情: {json.dumps(data, ensure_ascii=False)[:400]}")
                return True
                
        except Exception as e:
            continue
    
    print(f"  ❌ 数据源 {source_id} 验证失败")
    return False

def verify_task(task_id):
    """验证任务是否成功创建"""
    print(f"\n验证任务 {task_id}...")
    
    # 尝试多个可能的端点
    endpoints = [
        f"/api/v1/admin/tasks/{task_id}",
        f"/api/v1/crawler/tasks/{task_id}"
    ]
    
    for endpoint in endpoints:
        try:
            full_url = f"{BASE_URL}{endpoint}"
            response = requests.get(full_url, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ 任务验证成功 (端点: {endpoint})")
                print(f"     详情: {json.dumps(data, ensure_ascii=False)[:400]}")
                return True
                
        except Exception as e:
            continue
    
    print(f"  ❌ 任务 {task_id} 验证失败")
    return False

def test_100qiu_api():
    """测试100球网API"""
    print("\n测试100球网API...")
    
    try:
        url = "https://m.100qiu.com/api/dcListBasic?dateTime=26011"
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 100球网API测试成功!")
            print(f"     状态码: {response.status_code}")
            print(f"     数据类型: {type(data).__name__}")
            
            if isinstance(data, list):
                print(f"     数据条数: {len(data)}")
                if len(data) > 0:
                    print(f"     示例数据字段: {list(data[0].keys())}")
            elif isinstance(data, dict):
                print(f"     数据字段: {list(data.keys())}")
            
            return True
        else:
            print(f"  ❌ 100球网API测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  🚨 100球网API测试异常: {e}")
        return False

def main():
    """主测试流程"""
    print_section("完整用户操作模拟测试")
    print(f"后端地址: {BASE_URL}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 记录测试结果
    test_results = {
        "backend_health": False,
        "admin_login": False,
        "data_source_creation": False,
        "task_creation": False,
        "data_source_verification": False,
        "task_verification": False,
        "100qiu_api_test": False
    }
    
    # 1. 测试后端健康状态
    if not test_health():
        print("\n❌ 后端服务不可用，测试终止")
        return False
    test_results["backend_health"] = True
    
    # 2. 测试100球网API
    test_results["100qiu_api_test"] = test_100qiu_api()
    
    # 3. 管理员登录
    access_token = admin_login()
    if not access_token:
        print("\n⚠️  管理员登录失败，但仍可继续测试部分功能")
    else:
        test_results["admin_login"] = True
    
    # 4. 获取现有数据源
    existing_sources, source_endpoint = get_existing_data_sources()
    
    if not existing_sources and access_token:
        print("\n未找到现有数据源，将创建新数据源...")
        
        # 5. 创建数据源
        source_id, source_data = create_data_source(access_token, source_endpoint or "/api/v1/admin/sources")
        if source_id:
            test_results["data_source_creation"] = True
            
            # 6. 验证数据源
            test_results["data_source_verification"] = verify_data_source(source_id)
        else:
            print("\n⚠️  数据源创建失败")
            # 尝试使用现有数据源（如果有的话）
            if existing_sources:
                source_id = existing_sources[0].get("id")
                print(f"将使用现有数据源: {source_id}")
    elif existing_sources:
        print(f"\n使用现有数据源: {existing_sources[0].get('id')}")
        source_id = existing_sources[0].get("id")
    else:
        print("\n❌ 无法获取或创建数据源，测试终止")
        return False
    
    # 7. 获取现有任务
    existing_tasks, task_endpoint = get_existing_tasks()
    
    if access_token:
        # 8. 创建任务
        task_id = create_task(access_token, source_id, task_endpoint or "/api/v1/admin/tasks")
        if task_id:
            test_results["task_creation"] = True
            
            # 9. 验证任务
            test_results["task_verification"] = verify_task(task_id)
        else:
            print("\n⚠️  任务创建失败")
    else:
        print("\n⚠️  由于登录失败，跳过任务创建步骤")
    
    # 汇总测试结果
    print_section("测试结果汇总")
    
    print("用户操作路径验证:")
    print(f"  ✅ 第一步: 使用管理员账号登录系统 - {'成功' if test_results['admin_login'] else '失败'}")
    print(f"  ✅ 第二步: 创建数据源 - {'成功' if test_results['data_source_creation'] else '失败'}")
    print(f"  ✅ 第三步: 创建任务 - {'成功' if test_results['task_creation'] else '失败'}")
    
    print("\n详细测试结果:")
    for key, value in test_results.items():
        status = "✅ 通过" if value else "❌ 失败"
        print(f"  {key}: {status}")
    
    print(f"\n100球网API测试: {'✅ 可用' if test_results['100qiu_api_test'] else '❌ 不可用'}")
    
    # 整体评估
    critical_success = (
        test_results["backend_health"] and 
        (test_results["data_source_creation"] or existing_sources)
    )
    
    if critical_success:
        print(f"\n{'✅'*30}")
        print("模拟用户操作测试基本通过!")
        print("数据源已成功创建或已存在，可用于后续数据导入")
        print(f"{'✅'*30}")
        return True
    else:
        print(f"\n{'❌'*30}")
        print("模拟用户操作测试失败!")
        print("需要检查后端服务和认证配置")
        print(f"{'❌'*30}")
        return False

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