import requests
import json

def simulate_frontend_request():
    """
    模拟前端请求，检查登录API的行为
    """
    print("正在模拟前端请求...")
    
    # 模拟前端登录请求
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        print("发送登录请求...")
        response = requests.post(login_url, json=login_data)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"响应JSON内容: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
            
            if response.status_code == 200:
                print("\n✓ 登录请求成功")
                
                # 如果登录成功，尝试获取操作日志
                if 'data' in response_json and 'access_token' in response_json['data']:
                    token = response_json['data']['access_token']
                    print(f"\n获取到令牌: {token[:20]}...")
                    
                    # 使用令牌请求受保护的API
                    headers = {'Authorization': f'Bearer {token}'}
                    logs_url = "http://localhost:8000/api/v1/admin/system/logs/db/user?page=1&size=20"
                    
                    print("\n使用令牌请求操作日志...")
                    logs_response = requests.get(logs_url, headers=headers)
                    
                    print(f"日志API响应状态码: {logs_response.status_code}")
                    if logs_response.status_code == 200:
                        print("✓ 日志API请求成功")
                    else:
                        try:
                            logs_error = logs_response.json()
                            print(f"日志API错误响应: {logs_error}")
                        except:
                            print(f"日志API错误响应: {logs_response.text}")
                else:
                    print("✗ 响应中没有找到访问令牌")
            else:
                print("✗ 登录请求失败")
                print(f"错误详情: {response.text}")
                
        except ValueError:
            print(f"响应非JSON格式: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到后端服务，请确保后端服务正在运行")
    except Exception as e:
        print(f"✗ 请求过程中出现错误: {str(e)}")

if __name__ == "__main__":
    simulate_frontend_request()