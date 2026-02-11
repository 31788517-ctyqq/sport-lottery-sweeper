import requests
import sys
import json

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
LLM_PROVIDERS_URL = f"{BASE_URL}/api/v1/llm-providers/"

def test_login_and_providers():
    print("测试LLM供应商认证流程")
    print("=" * 50)
    
    # 1. 登录获取令牌
    print("\n1. 尝试登录...")
    try:
        response = requests.post(LOGIN_URL, json={"username": "admin", "password": "admin123"})
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 提取令牌
            if "data" in data and "access_token" in data["data"]:
                token = data["data"]["access_token"]
                print(f"✓ 登录成功，令牌前20位: {token[:20]}...")
            elif "access_token" in data:
                token = data["access_token"]
                print(f"✓ 登录成功（旧格式），令牌前20位: {token[:20]}...")
            else:
                print("✗ 响应中没有access_token字段")
                return False
        else:
            print(f"✗ 登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 登录异常: {e}")
        return False
    
    # 2. 测试LLM供应商端点
    print("\n2. 测试LLM供应商端点...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(LLM_PROVIDERS_URL, headers=headers)
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            providers = response.json()
            print(f"✓ 获取LLM供应商列表成功")
            print(f"  返回数据类型: {type(providers)}")
            if isinstance(providers, list):
                print(f"  供应商数量: {len(providers)}")
                if providers:
                    print(f"  第一个供应商: {providers[0].get('name') if isinstance(providers[0], dict) else '未知'}")
            else:
                print(f"  返回数据: {providers}")
            return True
        else:
            print(f"✗ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 测试LLM供应商端点异常: {e}")
        return False

if __name__ == "__main__":
    success = test_login_and_providers()
    sys.exit(0 if success else 1)