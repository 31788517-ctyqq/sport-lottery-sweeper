"""
简化版数据导入脚本
"""
import sys
import os
from datetime import datetime
import asyncio
import json
from datetime import datetime as dt

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.models.matches import FootballMatch
from backend.models.data_sources import DataSource
from backend.services.sp_management_service import SPManagementService


def create_hundred_qiu_data_source():
    """创建100qiu数据源配置"""
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # 检查是否已存在同名数据源
        existing_source = db.query(DataSource).filter(
            DataSource.name == '100qiu竞彩基础数据'
        ).first()
        
        if existing_source:
            print("数据源已存在，ID:", existing_source.id)
            return existing_source.id
        
        # 创建数据源配置
        sp_service = SPManagementService(db)
        
        from backend.schemas.sp_management import DataSourceCreate
        data_source_data = DataSourceCreate(
            name="100qiu竞彩基础数据",
            type="api",
            url="https://m.100qiu.com/api/dcListBasic",
            status=True,
            config={
                "params": {
                    "dateTime": "26011"
                },
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "application/json, text/plain, */*",
                    "Referer": "https://m.100qiu.com/"
                },
                "method": "GET",
                "data_source_type": "hundred_qiu",
                "cron_expression": "0 2 * * *"  # 每天凌晨2点执行
            }
        )
        
        created_source = sp_service.create_data_source(data_source_data, created_by=1)
        print(f"成功创建数据源，ID: {created_source.id}")
        return created_source.id
        
    except Exception as e:
        print(f"创建数据源失败: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def test_data_source_connection(source_id: int):
    """测试数据源连接"""
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        sp_service = SPManagementService(db)
        result = sp_service.test_data_source(source_id)
        print(f"数据源连接测试结果: {result}")
        return result
    except Exception as e:
        print(f"测试数据源连接失败: {e}")
        return None
    finally:
        db.close()


def import_data_directly():
    """直接从API获取数据并保存到数据库"""
    import requests
    
    # 准备数据库连接
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # 发送请求到API
        url = "https://m.100qiu.com/api/dcListBasic"
        params = {"dateTime": "26011"}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://m.100qiu.com/"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        matches = data.get('data', [])
        
        print(f"从API获取到 {len(matches)} 条比赛数据")
        
        count = 0
        for match_data in matches:
            # 处理单个比赛数据
            processed_match = {
                'match_id': match_data.get('lineId'),  # 使用lineId作为比赛ID
                'league': match_data.get('gameShortName', ''),  # 联赛名称
                'home_team': match_data.get('homeTeam', ''),  # 主队
                'away_team': match_data.get('guestTeam', ''),  # 客队
                'match_time': match_data.get('matchTimeStr', ''),  # 比赛时间
                'status': 'scheduled',  # 默认状态
                'home_odds': match_data.get('homeWinAward', 0.0),  # 主胜赔率
                'away_odds': match_data.get('guestWinAward', 0.0),  # 客胜赔率
                'draw_odds': match_data.get('drawAward', 0.0),  # 平局赔率
                'handicap': match_data.get('rq', 0),  # 让球数
                'raw_data': match_data,  # 保存原始数据
            }
            
            # 尝试将match_time字符串转换为datetime对象
            match_datetime = None
            if processed_match['match_time']:
                try:
                    # 假设match_time格式为"2026-01-02"，需要转换为datetime
                    match_datetime = dt.strptime(processed_match['match_time'], "%Y-%m-%d")
                except ValueError:
                    # 如果格式不对，跳过这条记录
                    print(f"无法解析比赛时间: {processed_match['match_time']}，跳过该记录")
                    continue
            
            # 检查是否已存在该比赛 - 使用match_id作为唯一标识
            existing_match = db.query(FootballMatch).filter(
                FootballMatch.match_id == f"hundred_qiu_{processed_match['match_id']}"
            ).first()
            
            if existing_match:
                # 如果存在，则更新
                existing_match.league = processed_match['league']
                existing_match.home_team = processed_match['home_team']
                existing_match.away_team = processed_match['away_team']
                if match_datetime:
                    existing_match.match_time = match_datetime
                existing_match.status = processed_match['status']
                existing_match.updated_at = dt.now()
            else:
                # 如果不存在，则创建
                new_match = FootballMatch(
                    match_id=f"hundred_qiu_{processed_match['match_id']}",  # 使用组合ID
                    home_team=processed_match['home_team'],
                    away_team=processed_match['away_team'],
                    match_time=match_datetime,  # 使用转换后的datetime对象
                    league=processed_match['league'],
                    status=processed_match['status']
                )
                db.add(new_match)
            
            count += 1
        
        db.commit()
        print(f"成功保存 {count} 条比赛数据到数据库")
        return count
        
    except Exception as e:
        db.rollback()
        print(f"导入数据失败: {e}")
        import traceback
        traceback.print_exc()
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    print("开始配置100qiu数据源...")
    
    # 创建数据源
    source_id = create_hundred_qiu_data_source()
    
    if source_id:
        print("\n数据源创建成功!")
        print(f"数据源ID: {source_id}")
        
        # 测试数据源连接
        print("\n正在测试数据源连接...")
        test_result = test_data_source_connection(source_id)
        
        if test_result and test_result.get("success"):
            print("连接测试成功!")
        else:
            print("连接测试可能失败，请检查网络连接和API可用性")
        
        # 导入数据
        print("\n正在从API获取数据并保存到数据库...")
        count = import_data_directly()
        
        if count > 0:
            print(f"\n成功导入 {count} 条比赛数据!")
            print("数据源配置和数据导入已完成！")
        else:
            print("\n数据导入可能失败，请检查网络连接和API可用性")
    else:
        print("数据源创建失败，请检查数据库连接和配置")