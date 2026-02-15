#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from collections import defaultdict

def check_latest_100qiu_matches():
    conn = sqlite3.connect('data/sport_lottery.db')
    cursor = conn.cursor()
    
    # 获取所有100qiu数据的source_attributes
    cursor.execute('SELECT source_attributes FROM football_matches WHERE data_source = "100qiu" AND source_attributes IS NOT NULL AND source_attributes != "{}"')
    results = cursor.fetchall()
    
    print(f'总共获取到 {len(results)} 条100qiu数据')
    
    # 按matchTimeStr分组统计
    dates_count = defaultdict(int)
    date_details = defaultdict(list)
    
    for row in results:
        try:
            attrs = json.loads(row[0])
            match_date = attrs.get('matchTimeStr')
            if match_date:
                dates_count[match_date] += 1
                # 保存一些详细信息用于显示
                if len(date_details[match_date]) < 2:  # 每个日期只保存前2条作为示例
                    date_details[match_date].append({
                        'homeTeam': attrs.get('homeTeam', ''),
                        'guestTeam': attrs.get('guestTeam', ''),
                        'league': attrs.get('gameShortName', '')
                    })
        except json.JSONDecodeError:
            continue
    
    # 按日期降序排列
    sorted_dates = sorted(dates_count.items(), key=lambda x: x[0], reverse=True)
    
    print('\n100qiu数据按日期分布:')
    for date, count in sorted_dates:
        print(f'  {date}: {count}场')
        # 显示该日期的前几场比赛作为示例
        for match in date_details[date][:3]:
            print(f'    {match["homeTeam"]} vs {match["guestTeam"]} ({match["league"]})')
        if len(date_details[date]) > 3:
            print(f'    ... 还有 {len(date_details[date]) - 3} 场')
    
    if sorted_dates:
        latest_date, latest_count = sorted_dates[0]
        print(f'\n[最新一期] {latest_date} 共有 {latest_count} 场比赛')
    
    conn.close()

if __name__ == '__main__':
    check_latest_100qiu_matches()
