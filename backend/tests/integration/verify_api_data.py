"""
验证API返回的数据是否是从今天开始的三天比赛数据
"""
import requests
import json
from datetime import datetime, timedelta

def verify_api_data():
    print("验证API返回的比赛数据...")
    
    try:
        response = requests.get('http://localhost:8000/api/v1/public/matches/')
        
        if response.status_code == 200:
            print(f"API请求成功，状态码: {response.status_code}")
            
            # 直接获取JSON数据
            data = response.json()
            print(f"获取到 {len(data)} 条比赛数据\n")
            
            # 获取今天日期
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            day_after_tomorrow = today + timedelta(days=2)
            
            today_matches = []
            tomorrow_matches = []
            day_after_tomorrow_matches = []
            later_matches = []
            
            for match in data:
                match_time_str = match.get('match_time', '')
                try:
                    # 解析时间字符串
                    if 'T' in match_time_str:
                        match_date = datetime.fromisoformat(match_time_str.replace('Z', '+00:00')).date()
                    elif ':' in match_time_str and '-' in match_time_str:
                        # 处理 "YYYY-MM-DD HH:MM" 格式
                        if len(match_time_str.split()[0].split('-')[0]) == 4:
                            match_date = datetime.strptime(match_time_str.split()[0], "%Y-%m-%d").date()
                        else:
                            # 处理 "MM-DD HH:MM" 格式
                            year = today.year
                            date_part = f"{year}-{match_time_str.split()[0]}"
                            match_date = datetime.strptime(date_part, "%Y-%m-%d").date()
                    else:
                        # 只有日期
                        if '-' in match_time_str and len(match_time_str.split('-')[0]) == 4:
                            match_date = datetime.strptime(match_time_str, "%Y-%m-%d").date()
                        else:
                            # 假设是MM-DD格式
                            year = today.year
                            match_date = datetime.strptime(f"{year}-{match_time_str}", "%Y-%m-%d").date()
                    
                    # 分类比赛
                    if match_date == today:
                        today_matches.append(match)
                    elif match_date == tomorrow:
                        tomorrow_matches.append(match)
                    elif match_date == day_after_tomorrow:
                        day_after_tomorrow_matches.append(match)
                    elif match_date > day_after_tomorrow:
                        later_matches.append(match)
                        
                except Exception as e:
                    print(f"解析比赛时间失败: {match_time_str}, 错误: {str(e)}")
                    # 如果解析失败，暂时放到later_matches中
                    later_matches.append(match)
            
            print(f"今天 ({today.strftime('%Y-%m-%d')}) 的比赛: {len(today_matches)} 场")
            for i, match in enumerate(today_matches, 1):
                print(f"  {i}. {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')} - {match.get('league', 'N/A')}")
            
            print(f"\n明天 ({tomorrow.strftime('%Y-%m-%d')}) 的比赛: {len(tomorrow_matches)} 场")
            for i, match in enumerate(tomorrow_matches, 1):
                print(f"  {i}. {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')} - {match.get('league', 'N/A')}")
            
            print(f"\n后天 ({day_after_tomorrow.strftime('%Y-%m-%d')}) 的比赛: {len(day_after_tomorrow_matches)} 场")
            for i, match in enumerate(day_after_tomorrow_matches, 1):
                print(f"  {i}. {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')} - {match.get('league', 'N/A')}")
            
            if later_matches:
                print(f"\n之后日期的比赛: {len(later_matches)} 场")
                for i, match in enumerate(later_matches, 1):
                    print(f"  {i}. {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')} - {match.get('league', 'N/A')}")
            
            total_expected = len(today_matches) + len(tomorrow_matches) + len(day_after_tomorrow_matches)
            print(f"\n总计从今天起三天内的比赛: {total_expected} 场")
            
            # 检查是否包含了从今天开始的数据
            if total_expected > 0:
                print("\n✅ API成功返回了从今天开始的三天比赛数据")
                print("✅ 数据已准备好供前端使用")
            else:
                print("\n❌ API未返回从今天开始的三天比赛数据")
                
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"请求API时发生错误: {str(e)}")

if __name__ == "__main__":
    verify_api_data()