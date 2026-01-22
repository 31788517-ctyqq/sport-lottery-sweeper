#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
500彩票网数据导入脚本
将抓取的比赛数据导入到数据库
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

from database import SessionLocal
from models.sporttery import MatchData
from sqlalchemy import text

def import_500_data():
    """导入500彩票网数据到数据库"""
    
    # 查找最新的抓取数据文件
    debug_dir = BASE_DIR / "debug"
    json_files = [f for f in os.listdir(debug_dir) if f.startswith('500_com_matches_') and f.endswith('.json')]
    
    if not json_files:
        print('❌ 未找到500彩票网抓取的数据文件')
        return False
    
    # 按时间排序，取最新的文件
    json_files.sort(reverse=True)
    latest_file = debug_dir / json_files[0]
    
    print(f'📂 读取数据文件: {latest_file}')
    
    # 读取JSON数据
    with open(latest_file, 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    print(f'📊 共发现 {len(matches)} 场比赛')
    
    # 连接数据库
    db = SessionLocal()
    try:
        inserted_count = 0
        skipped_count = 0
        
        for match in matches:
            # 跳过标题行
            if match.get('match_id') == '编号':
                continue
            
            # 检查比赛是否已存在
            existing = db.execute(
                text('SELECT id FROM match_data WHERE match_id = :match_id AND source = :source'),
                {'match_id': match['match_id'], 'source': match['source']}
            ).fetchone()
            
            if existing:
                print(f'⚠️  比赛已存在: {match["match_id"]} - {match["league"]}')
                skipped_count += 1
                continue
            
            # 解析比赛时间和日期
            match_date = None
            start_time = None
            
            if match['match_time'] != '开赛时间截止时间剩余时间':
                try:
                    # 解析格式如 "01-21 03:45"
                    time_parts = match['match_time'].split()
                    if len(time_parts) == 2:
                        date_part, time_part = time_parts
                        # 构造完整日期 (假设是2026年)
                        full_date = f"2026-{date_part.replace('-', '-')}"
                        match_date = datetime.strptime(full_date, '%Y-%m-%d').date()
                        start_time = datetime.strptime(time_part, '%H:%M').time()
                except Exception as e:
                    print(f'⚠️  时间解析失败 {match["match_time"]}: {e}')
            
            # 提取赔率数据
            odds_home_win = None
            odds_draw = None
            odds_away_win = None
            
            if match.get('odds_home_win', 0) > 0:
                odds_home_win = match['odds_home_win']
            if match.get('odds_draw', 0) > 0:
                odds_draw = match['odds_draw']
            if match.get('odds_away_win', 0) > 0:
                odds_away_win = match['odds_away_win']
            
            # 创建MatchData对象
            match_data = MatchData(
                match_id=match['match_id'],
                league=match['league'],
                home_team=match['home_team'],
                away_team=match['away_team'],
                match_date=match_date,
                start_time=start_time,
                handicap=str(match.get('handicap', '')) if match.get('handicap') else None,
                home_odds=odds_home_win,
                draw_odds=odds_draw,
                away_odds=odds_away_win,
                analysis=match.get('analysis', ''),
                raw_data=match,
                source=match['source'],
                status=match.get('status', 'scheduled'),
                score=match.get('score', '-:-')
            )
            
            db.add(match_data)
            inserted_count += 1
            
            # 每10条记录打印一次进度
            if inserted_count % 10 == 0:
                print(f'✅ 已插入 {inserted_count} 场比赛...')
        
        # 提交事务
        db.commit()
        print(f'\n🎉 数据导入完成！')
        print(f'   成功插入: {inserted_count} 场比赛')
        print(f'   跳过重复: {skipped_count} 场比赛')
        
        # 显示数据库统计
        total_matches = db.execute(text('SELECT COUNT(*) FROM match_data WHERE source = :source'), 
                                  {'source': '500彩票网'}).scalar()
        print(f'📈 500彩票网数据共计 {total_matches} 场比赛记录')
        
        # 显示今日和明日的比赛数量
        today = datetime.now().date()
        tomorrow = datetime.now().date().replace(day=today.day + 1) if today.day < 28 else today.replace(month=today.month + 1, day=1)
        
        today_count = db.execute(
            text('SELECT COUNT(*) FROM match_data WHERE source = :source AND match_date = :date'),
            {'source': '500彩票网', 'date': today}
        ).scalar()
        
        tomorrow_count = db.execute(
            text('SELECT COUNT(*) FROM match_data WHERE source = :source AND match_date = :date'),
            {'source': '500彩票网', 'date': tomorrow}
        ).scalar()
        
        print(f'📅 今日({today})比赛: {today_count} 场')
        print(f'📅 明日({tomorrow})比赛: {tomorrow_count} 场')
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f'❌ 数据导入失败: {str(e)}')
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == '__main__':
    print('🚀 开始导入500彩票网数据...')
    success = import_500_data()
    if success:
        print('✅ 导入成功！')
        sys.exit(0)
    else:
        print('❌ 导入失败！')
        sys.exit(1)