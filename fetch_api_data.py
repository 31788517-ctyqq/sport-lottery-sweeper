import requests
import json
from datetime import datetime

def fetch_api_data():
    url = "https://m.100qiu.com/api/dcListBasic?dateTime=26011"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        
        data = response.json()
        
        print("API Response Status:", response.status_code)
        print("API Response Headers:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
        
        print("\nAPI Response Data Structure:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 分析数据结构
        if isinstance(data, dict):
            if 'data' in data:
                print(f"\nData type: {type(data['data'])}")
                if isinstance(data['data'], list) and len(data['data']) > 0:
                    print(f"Number of records: {len(data['data'])}")
                    print(f"Sample record keys: {list(data['data'][0].keys()) if isinstance(data['data'][0], dict) else 'Not a dict'}")
                    
                    # 打印第一个记录的所有字段
                    if isinstance(data['data'][0], dict):
                        print("\nFirst record fields and values:")
                        for key, value in data['data'][0].items():
                            print(f"  {key}: {value} ({type(value).__name__})")
                else:
                    print("Data is not a list or is empty")
            else:
                print("No 'data' key found in response")
                print(f"Available keys: {list(data.keys()) if isinstance(data, dict) else 'Response is not a dict'}")
        else:
            print(f"Response is not a dictionary, it's {type(data)}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
    except Exception as e:
        print(f"Other error: {e}")

if __name__ == "__main__":
    fetch_api_data()