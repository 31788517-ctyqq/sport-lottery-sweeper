import requests
import json
from datetime import datetime

def test_api_structure():
    url = "https://m.100qiu.com/api/dcListBasic"
    params = {
        "dateTime": "26011"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        print("API响应状态码:", response.status_code)
        print("API响应数据结构:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 分析数据结构
        if isinstance(data, dict):
            print("\n键名列表:")
            for key in data.keys():
                print(f"- {key}: {type(data[key]).__name__}")
                
            if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                print(f"\n数据列表第一个元素的键名:")
                first_item = data['data'][0]
                if isinstance(first_item, dict):
                    for key in first_item.keys():
                        value = first_item[key]
                        print(f"- {key}: {type(value).__name__} (示例值: {str(value)[:100]})")
        
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")

if __name__ == "__main__":
    test_api_structure()