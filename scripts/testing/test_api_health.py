import requests

def test_api_health():
    try:
        # 测试API健康状态
        response = requests.get('http://localhost:3000/api/admin/crawler/tasks?page=1&size=10')
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text[:500]}...")  # 只打印前500个字符
        
        if response.status_code == 200:
            print("API正常运行")
        else:
            print("API出现问题")
            
    except requests.exceptions.ConnectionError:
        print("无法连接到API服务")
    except Exception as e:
        print(f"测试API时出现错误: {e}")

if __name__ == "__main__":
    test_api_health()