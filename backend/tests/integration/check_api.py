"""
检查API返回数据的编码问题
"""
import requests
import json

def check_api_response():
    print("正在检查API响应数据...")
    
    try:
        response = requests.get('http://localhost:8000/api/v1/public/matches/')
        
        if response.status_code == 200:
            print(f"API请求成功，状态码: {response.status_code}")
            print(f"响应头Content-Type: {response.headers.get('content-type')}")
            
            # 直接获取JSON数据，requests会自动处理编码
            data = response.json()
            print(f"\n获取到 {len(data)} 条比赛数据")
            
            print("\n前5场比赛数据:")
            for i, match in enumerate(data[:5]):
                print(f"\n比赛 {i+1}:")
                print(f"  ID: {match.get('id', 'N/A')}")
                print(f"  主队: {match.get('home_team', 'N/A')}")
                print(f"  客队: {match.get('away_team', 'N/A')}")
                print(f"  联赛: {match.get('league', 'N/A')}")
                print(f"  时间: {match.get('match_time', 'N/A')}")
                print(f"  赔率: 主胜 {match.get('odds_home_win', 'N/A')}, 平局 {match.get('odds_draw', 'N/A')}, 客胜 {match.get('odds_away_win', 'N/A')}")
                
                # 检查是否存在乱码
                for key, value in match.items():
                    if isinstance(value, str):
                        # 检查是否包含乱码字符
                        if any(ord(c) < 32 or 127 < ord(c) < 160 for c in value):
                            print(f"  ⚠️  {key} 字段可能存在乱码: {repr(value)}")
                        elif '\\u' in value:
                            # 存在Unicode转义序列，可能需要解码
                            decoded_value = value.encode().decode('unicode_escape')
                            print(f"  ℹ️  {key} 解码后: {decoded_value}")
            
            # 保存原始响应到文件用于调试
            with open('api_response_raw.json', 'wb') as f:
                f.write(response.content)
            print(f"\n原始响应已保存到 api_response_raw.json")
            
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"请求API时发生错误: {str(e)}")

if __name__ == "__main__":
    check_api_response()