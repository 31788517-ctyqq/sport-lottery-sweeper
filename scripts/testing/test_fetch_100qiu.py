import requests
import json

# 测试100qiu数据源获取功能
def test_fetch_100qiu_data():
    # 假设有一个100qiu数据源，ID为1
    source_id = 1
    
    # API端点
    url = f"http://localhost:8000/api/v1/data-source-100qiu/{source_id}/fetch"
    
    try:
        response = requests.post(url)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"解析后的JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    test_fetch_100qiu_data()