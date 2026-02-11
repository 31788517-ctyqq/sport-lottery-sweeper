import requests
import json

def test_api():
    """
    测试API连通性，获取竞彩数据
    """
    url = "https://m.100qiu.com/api/dcListBasic"
    params = {
        "dateTime": "26011"
    }
    
    print("正在测试API连通性...")
    print(f"请求URL: {url}")
    print(f"请求参数: {params}")
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}...")
        
        if "data" in data and isinstance(data["data"], list):
            print(f"API返回数据条数: {len(data['data'])}")
            if len(data["data"]) > 0:
                print(f"第一条数据示例: {json.dumps(data['data'][0], indent=2, ensure_ascii=False)}")
            return True
        else:
            print("警告: API响应中没有有效数据")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"请求API失败: {e}")
        return False
    except ValueError as e:
        print(f"解析API响应失败: {e}")
        return False

if __name__ == "__main__":
    test_api()