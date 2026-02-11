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
from backend.models.match import Match, Team, League
from backend.database import get_db

def execute_task_and_save_data():
    """
    执行任务ID 32并保存100球数据到数据库
    """
    print("="*60)
    print("执行任务ID 32并保存100球数据到数据库")
    print("="*60)
    
    # 首先触发任务ID 32
    task_url = "http://localhost:3000/api/admin/crawler/tasks/32/trigger"
    
    print("步骤1: 触发任务ID 32...")
    try:
        response = requests.post(task_url)
        print(f"触发任务响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"触发任务结果: {result}")
        else:
            print(f"触发任务失败: {response.text}")
            return
    except Exception as e:
        print(f"请求失败: {e}")
        return
    
    # 等待一段时间让任务执行
    print("\n步骤2: 等待任务执行...")
    time.sleep(15)  # 等待15秒让任务执行
    
    # 检查任务状态
    print("\n步骤3: 检查任务执行状态...")
    status_url = "http://localhost:3000/api/admin/crawler/tasks/32"
    try:
        status_response = requests.get(status_url)
        if status_response.status_code == 200:
            task_data = status_response.json()
            print(f"任务状态: {task_data.get('data', {}).get('status', 'Unknown')}")
            print(f"运行次数: {task_data.get('data', {}).get('run_count', 0)}")
            print(f"成功次数: {task_data.get('data', {}).get('success_count', 0)}")
            print(f"错误次数: {task_data.get('data', {}).get('error_count', 0)}")
        else:
            print(f"获取任务状态失败: {status_response.text}")
    except Exception as e:
        print(f"检查任务状态失败: {e}")
    
    # 获取任务日志
    print("\n步骤4: 获取任务执行日志...")
    logs_url = "http://localhost:3000/api/admin/crawler/tasks/32/logs"
    try:
        logs_response = requests.get(logs_url)
        if logs_response.status_code == 200:
            logs_data = logs_response.json()
            print(f"日志总数: {logs_data.get('data', {}).get('total', 0)}")
            
            items = logs_data.get('data', {}).get('items', [])
            if items:
                latest_log = items[0]  # 最新的日志
                print(f"最新日志状态: {latest_log.get('status')}")
                print(f"处理记录数: {latest_log.get('records_processed', 0)}")
                print(f"成功记录数: {latest_log.get('records_success', 0)}")
                print(f"失败记录数: {latest_log.get('records_failed', 0)}")
                if latest_log.get('error_message'):
                    print(f"错误信息: {latest_log.get('error_message')}")
        else:
            print(f"获取任务日志失败: {logs_response.text}")
    except Exception as e:
        print(f"获取日志失败: {e}")
    
    # 现在手动获取100球的数据并保存到数据库
    print("\n步骤5: 手动获取100球数据并保存到数据库...")
    
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
            if isinstance(data, dict) and 'result' in data:
                matches_data = data['result']
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
                
                for match_data in matches_data:
                    # 检查是否为期望的数据结构
                    if not isinstance(match_data, dict):
                        continue
                        
                    # 尝试提取比赛信息（字段名根据实际API响应调整）
                    match_id = match_data.get('lineId', match_data.get('id', f"100qiu_{int(time.time())}"))
                    home_team = match_data.get('homeTeam', match_data.get('home', ''))
                    away_team = match_data.get('guestTeam', match_data.get('away', ''))
                    league = match_data.get('gameShortName', match_data.get('league', ''))
                    match_time_str = match_data.get('matchTimeStr', match_data.get('time', ''))
                    
                    # 尝试解析时间字符串
                    match_time = None
                    if match_time_str:
                        try:
                            # 尝试不同的时间格式
                            for fmt in ['%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M', '%Y-%m-%d %H:%M:%S']:
                                try:
                                    match_time = datetime.strptime(match_time_str, fmt)
                                    break
                                except ValueError:
                                    continue
                        except:
                            print(f"无法解析时间: {match_time_str}")
                    
                    # 检查数据库中是否已存在该比赛
                    existing_match = db.query(FootballMatch).filter(
                        FootballMatch.match_id == f"100qiu_{match_id}"
                    ).first()
                    
                    if not existing_match:
                        # 创建新的比赛记录
                        new_match = FootballMatch(
                            match_id=f"100qiu_{match_id}",
                            home_team=home_team,
                            away_team=away_team,
                            match_time=match_time,
                            league=league,
                            status='pending'  # 根据实际情况设置状态
                        )
                        
                        db.add(new_match)
                        saved_count += 1
                    else:
                        print(f"比赛已存在: {match_id}")
                
                # 提交事务
                db.commit()
                print(f"成功保存 {saved_count} 条新比赛数据到数据库")
                
                # 统计数据库中的总比赛数
                total_matches = db.query(FootballMatch).count()
                print(f"数据库中总比赛数: {total_matches}")
                
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
    execute_task_and_save_data()