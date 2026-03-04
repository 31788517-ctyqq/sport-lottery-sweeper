"""
详细调试API响应的脚本
"""
import requests
import json
from pprint import pprint


def debug_api_detailed():
    print("开始详细调试API响应...")
    
    try:
        # 请求近三天的比赛数据
        response = requests.get('http://localhost:8000/api/v1/public/matches/')
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容长度: {len(response.content)}")
        
        try:
            data = response.json()
            print(f"JSON解析成功，数据类型: {type(data)}")
            print(f"数据长度: {len(data) if isinstance(data, (list, str)) else 'N/A'}")
            
            if isinstance(data, list) and len(data) > 0:
                print("\n第一条数据的完整详情:")
                first_item = data[0]
                pprint(first_item)
                
                print(f"\n字段列表: {list(first_item.keys())}")
                
                print("\n检查前端所需字段:")
                required_fields = ['id', 'match_id', 'home_team', 'away_team', 'league', 'match_date', 'match_time', 'odds_home_win', 'odds_draw', 'odds_away_win', 'status', 'popularity', 'predicted_result', 'prediction_confidence']
                for field in required_fields:
                    exists = field in first_item
                    value = first_item.get(field, 'NOT FOUND')
                    print(f"  {field}: {'✓' if exists else '✗'} ({value})")
            else:
                print(f"\n返回的数据内容: {data}")
        except ValueError:
            print(f"JSON解析失败，原始响应内容: {response.text[:1000]}")
            
    except Exception as e:
        print(f"测试API时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_api_detailed()