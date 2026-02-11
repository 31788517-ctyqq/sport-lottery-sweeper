import requests

def test_statistics_api():
    # 测试获取统计数据API
    url = "http://localhost:8001/api/admin/crawler/tasks/statistics"

    print(f"发送请求到: {url}")

    try:
        response = requests.get(url)
        print(f"响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"返回统计数据: {data}")
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    test_statistics_api()