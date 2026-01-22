"""
测试API端点的脚本
"""
import requests
import json
from datetime import datetime, timedelta


def test_api():
    print("开始测试API端点...")
    
    try:
        # 请求近三天的比赛数据
        response = requests.get('http://localhost:8000/api/v1/public/matches/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功获取到 {len(data) if isinstance(data, list) else 0} 条数据")
            
            if isinstance(data, list) and len(data) > 0:
                print("\n前5条比赛数据如下：")
                for i, item in enumerate(data[:5]):
                    print(f"\n比赛 {i+1}:")
                    print(f"  主队: {item.get('home_team', 'N/A')}")
                    print(f"  客队: {item.get('away_team', 'N/A')}")
                    print(f"  联赛: {item.get('league', 'N/A')}")
                    print(f"  时间: {item.get('match_time', 'N/A')}")
                    print(f"  赔率(主胜): {item.get('odds_home_win', 'N/A')}")
                    print(f"  赔率(平局): {item.get('odds_draw', 'N/A')}")
                    print(f"  赔率(客胜): {item.get('odds_away_win', 'N/A')}")
                    print(f"  ID: {item.get('match_id', 'N/A')}")
            else:
                print("返回的数据为空或格式不正确")
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"测试API时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_api()