"""
测试后端API端点是否正常工作
"""
import requests
import json

def test_backend_api():
    """测试后端API端点"""
    base_url = "http://localhost:8000"
    
    print("="*60)
    print("测试后端API端点")
    print("="*60)
    
    # 测试登录API
    login_url = f"{base_url}/api/v1/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        print("正在测试登录API...")
        response = requests.post(
            login_url,
            json=login_data,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("登录API测试成功!")
            data = response.json()
            if 'data' in data and 'access_token' in data['data']:
                print("成功获取到访问令牌")
                
                # 获取访问令牌用于后续认证请求
                headers = {
                    'Authorization': f'Bearer {data["data"]["access_token"]}'
                }
                
                # 测试需要认证的API - 操作日志
                logs_url = f"{base_url}/api/v1/admin/system/logs/db/user?page=1&size=20"
                print("\n正在测试操作日志API...")
                logs_response = requests.get(logs_url, headers=headers, timeout=10)
                
                print(f"日志API状态码: {logs_response.status_code}")
                print(f"日志API响应内容: {logs_response.text}")
                
                if logs_response.status_code == 200:
                    print("操作日志API测试成功!")
                else:
                    print("操作日志API测试失败")
                
                # 继续测试其他API端点（使用认证）
                print("\n3. 测试数据源API端点:")
                sources_url = f"{base_url}/api/v1/admin/sources"
                sources_response = requests.get(sources_url, headers=headers, timeout=10)
                print(f"   状态码: {sources_response.status_code}")
                
                if sources_response.status_code == 200:
                    data = sources_response.json()
                    print(f"   响应数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
                    print(f"   数据源数量: {len(data.get('data', {}).get('items', []))}")
                else:
                    print(f"   错误信息: {sources_response.text}")
                    
                # 测试爬虫任务API
                print("\n4. 测试爬虫任务API端点:")
                tasks_url = f"{base_url}/api/v1/crawler/tasks"
                tasks_response = requests.get(tasks_url, headers=headers, timeout=10)
                print(f"   状态码: {tasks_response.status_code}")
                
                if tasks_response.status_code == 200:
                    data = tasks_response.json()
                    print(f"   响应数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
                    print(f"   任务数量: {len(data) if isinstance(data, list) else 'N/A'}")
                else:
                    print(f"   错误信息: {tasks_response.text}")
                    
            else:
                print("登录API返回格式不正确")
        else:
            print("登录API测试失败")
            
    except requests.exceptions.ConnectionError:
        print("无法连接到后端服务，请确保后端服务正在运行")
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
    
    print("\n" + "="*60)
    print("API测试完成")
    print("如果端点不可用，请确保后端服务已启动")
    print("="*60)

if __name__ == "__main__":
    test_backend_api()