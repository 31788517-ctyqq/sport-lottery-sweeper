"""
测试100qiu API响应结构
"""
import requests
import json

def test_api_response():
    try:
        response = requests.get('http://localhost:8000/api/v1/data-source-100qiu/latest-matches?limit=5&include_raw=true')
        print(f'Status: {response.status_code}')
        
        if response.status_code != 200:
            print(f'Error response: {response.text}')
            return
            
        data = response.json()
        print(f'Data keys: {list(data.keys())}')
        
        matches = data.get('data', {}).get('matches', [])
        print(f'Matches count: {len(matches)}')
        
        if matches:
            first_match = matches[0]
            print(f'First match keys: {list(first_match.keys())}')
            
            raw = first_match.get('source_attributes')
            print(f'Raw exists: {raw is not None}')
            
            if raw:
                print(f'Raw date_time: {raw.get("date_time", "Not found")}')
                print(f'Raw lineId: {raw.get("lineId", "Not found")}')
            else:
                print('No source_attributes in response')
        else:
            print('No matches returned')
            
    except Exception as e:
        print(f'Exception: {e}')

if __name__ == '__main__':
    test_api_response()

def test_api():
    url = "https://m.100qiu.com/api/dcListBasic"
    params = {"dateTime": "26011"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://m.100qiu.com/"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print("API响应结构:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 尝试找出比赛数据的位置
        print("\n寻找比赛数据...")
        if 'data' in data:
            if 'matches' in data['data']:
                print(f"找到 {len(data['data']['matches'])} 场比赛")
                if data['data']['matches']:
                    print("第一场比赛数据结构:")
                    print(json.dumps(data['data']['matches'][0], indent=2, ensure_ascii=False))
            else:
                print("'data'中没有'matches'字段")
                print("data的内容:", json.dumps(data['data'], indent=2, ensure_ascii=False))
        else:
            print("响应中没有'data'字段")
            print("响应的顶层键:", list(data.keys()))
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_api()