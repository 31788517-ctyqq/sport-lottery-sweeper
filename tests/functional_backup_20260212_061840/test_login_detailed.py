import requests
import json

def test_login():
    url = "http://localhost:8000/api/v1/admin/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        print(f"发送 POST 请求到 {url}")
        print(f"数据: {json.dumps(data)}")
        response = requests.post(url, json=data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        try:
            result = response.json()
            print(f"响应 JSON: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except:
            print(f"响应文本: {response.text[:500]}")
        
        if response.status_code == 200:
            print("登录成功")
            return True
        else:
            print("登录失败")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"连接错误: {e}")
        return False
    except Exception as e:
        print(f"意外错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_login()