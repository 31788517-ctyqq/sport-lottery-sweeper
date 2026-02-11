import requests
import json

def test_advanced_filter():
    url = 'http://localhost:8000/api/v1/beidan-filter/advanced-filter'
    
    # 测试请求体
    payload = {
        "date_time": "26023",
        "strength_filter": {
            "min_strength": -3,
            "max_strength": 3
        },
        "win_pan_filter": {
            "min_win_pan": -4,
            "max_win_pan": 4
        },
        "stability_filter": {
            "min_stability": 0,
            "max_stability": 10
        },
        "p_level_filter": {
            "levels": [1, 2, 3, 4, 5]
        },
        "leagues": [],
        "date_range": None,
        "sortBy": "p_level",
        "sortOrder": "desc",
        "include_derating": True
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f'Status: {response.status_code}')
        
        if response.status_code != 200:
            print(f'Error response: {response.text}')
            return
            
        data = response.json()
        print(f'Data keys: {list(data.keys())}')
        
        matches = data.get('matches', [])
        print(f'Matches count: {len(matches)}')
        
        if matches:
            first_match = matches[0]
            print(f'First match keys: {list(first_match.keys())}')
            
            raw_data = first_match.get('raw_data')
            print(f'Raw data exists: {raw_data is not None}')
            
            if raw_data:
                print(f'Raw date_time: {raw_data.get("date_time", "Not found")}')
                print(f'Raw lineId: {raw_data.get("lineId", "Not found")}')
                print(f'Match ID: {first_match.get("match_id", "Not found")}')
            else:
                print('No raw_data in response')
        else:
            print('No matches returned')
            
    except Exception as e:
        print(f'Exception: {e}')

if __name__ == '__main__':
    test_advanced_filter()