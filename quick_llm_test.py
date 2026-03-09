import requests
import sys

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
LLM_PROVIDERS_URL = f"{BASE_URL}/api/v1/llm-providers"

def test_login():
    """测试管理员登录"""
    try:
        response = requests.post(LOGIN_URL, json={"username": "admin", "password": "admin123"})
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "access_token" in data["data"]:
                token = data["data"]["access_token"]
                print(f"登录成功，令牌前20位: {token[:20]}...")
                return token
            else:
                print("响应中没有access_token字段")
                return None
        else:
            print(f"登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"登录异常: {e}")
        return None

def test_llm_providers(token):
    """测试LLM供应商端点"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(LLM_PROVIDERS_URL, headers=headers)
        if response.status_code == 200:
            providers = response.json()
            print(f"获取LLM供应商列表成功，数量: {len(providers) if isinstance(providers, list) else 'N/A'}")
            return True
        else:
            print(f"获取LLM供应商列表失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"测试LLM供应商端点异常: {e}")
        return False

def main():
    print("快速LLM供应商API测试")
    print("=" * 40)
    
    # 测试登录
    print("\n1. 测试管理员登录...")
    token = test_login()
    if not token:
        print("❌ 登录测试失败")
        return 1
    
    # 测试LLM供应商端点
    print("\n2. 测试LLM供应商端点...")
    success = test_llm_providers(token)
    if not success:
        print("❌ LLM供应商端点测试失败")
        return 1
    
    print("\n✅ 所有测试通过")
    return 0

if __name__ == "__main__":
    sys.exit(main())