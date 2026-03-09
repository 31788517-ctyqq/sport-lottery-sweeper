import requests
import json
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models.matches import FootballMatch
from backend.database import get_db

def process_100qiu_data():
    """
    获取并处理100球数据，将其保存到数据库
    """
    print("="*60)
    print("获取并处理100球数据")
    print("="*60)
    
    # 获取数据
    api_url = "https://m.100qiu.com/api/dcListBasic"
    params = {"dateTime": "26011"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://m.100qiu.com/"
    }
    
    try:
        print(f"正在从 {api_url} 获取数据...")
        response = requests.get(api_url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"API响应成功，数据类型: {type(data)}")
            
            # 根据API响应结构处理数据
            matches_data = []
            if isinstance(data, dict) and 'data' in data:
                matches_data = data['data']
            elif isinstance(data, list):
                matches_data = data
            else:
                print(f"未知的数据结构: {type(data)}")
                print(f"数据预览: {str(data)[:500]}")
                return
            
            print(f"获取到 {len(matches_data)} 条比赛数据")
            
            # 连接数据库并保存数据
            db = next(get_db())
            
            try:
                saved_count = 0
                duplicated_count = 0
                
                for idx, match_data in enumerate(matches_data):
                    # 检查是否为期望的数据结构
                    if not isinstance(match_data, dict):
                        print(f"跳过非字典类型数据: {type(match_data)}")
                        continue
                    
                    # 打印第一个比赛数据的结构以了解字段
                    if idx == 0:
                        print(f"示例比赛数据结构: {list(match_data.keys())}")
                    
                    # 提取比赛信息（字段名根据实际API响应调整）
                    line_id_str = str(match_data.get('lineId', '')).strip()
                    date_time_str = params.get('dateTime', '').strip()  # 从请求参数获取期号
                    home_team = match_data.get('homeTeam', match_data.get('home', ''))
                    away_team = match_data.get('guestTeam', match_data.get('away', ''))
                    league = match_data.get('gameShortName', match_data.get('league', ''))
                    match_time_str = match_data.get('matchTimeStr', match_data.get('time', ''))
                    
                    # 检查是否所有必要字段都存在
                    if not all([line_id_str, date_time_str, home_team, away_team]):
                        print(f"跳过缺少必要字段的比赛: lineId={line_id_str}, dateTime={date_time_str}")
                        continue
                    
                    # 转换期号和序号为整数
                    try:
                        date_time = int(date_time_str)
                        line_id_int = int(line_id_str)
                    except ValueError:
                        print(f"期号或序号格式错误: dateTime={date_time_str}, lineId={line_id_str}")
                        continue
                    
                    # 生成新的match_id格式：date_time_line_id（如：26024_001）
                    match_id = f"{date_time}_{line_id_int:03d}"
                    
                    # 尝试解析时间字符串
                    match_time = None
                    if match_time_str:
                        try:
                            # 尝试不同的时间格式
                            for fmt in ['%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                                try:
                                    match_time = datetime.strptime(match_time_str, fmt)
                                    break
                                except ValueError:
                                    continue
                        except:
                            print(f"无法解析时间: {match_time_str}")
                    
                    # 检查数据库中是否已存在该比赛（使用新的match_id格式）
                    existing_match = db.query(FootballMatch).filter(
                        FootballMatch.match_id == match_id
                    ).first()
                    
                    if not existing_match:
                        # 创建新的比赛记录
                        new_match = FootballMatch(
                            match_id=match_id,  # 新的格式：26024_001
                            date_time=date_time,  # 期号：26024
                            line_id=line_id_int,  # 序号：1
                            home_team=home_team,
                            away_team=away_team,
                            match_time=match_time,
                            league=league,
                            status='pending'  # 根据实际情况设置状态
                        )
                        
                        db.add(new_match)
                        saved_count += 1
                        print(f"添加比赛: {match_id} - {home_team} vs {away_team}")
                    else:
                        duplicated_count += 1
                        print(f"比赛已存在: {home_team} vs {away_team}")
                
                # 提交事务
                db.commit()
                print(f"\n成功保存 {saved_count} 条新比赛数据到数据库")
                print(f"发现 {duplicated_count} 条重复比赛数据")
                
                # 统计数据库中的总比赛数
                total_matches = db.query(FootballMatch).count()
                print(f"数据库中总比赛数: {total_matches}")
                
                # 显示最近保存的比赛
                recent_matches = db.query(FootballMatch).order_by(FootballMatch.created_at.desc()).limit(5).all()
                print(f"\n最近保存的5场比赛:")
                for match in recent_matches:
                    print(f"  - {match.home_team} vs {match.away_team} ({match.league})")
                
            except Exception as e:
                db.rollback()
                print(f"保存数据时出错: {e}")
                import traceback
                traceback.print_exc()
            finally:
                db.close()
                
        else:
            print(f"API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"获取数据时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    process_100qiu_data()