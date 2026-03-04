#!/usr/bin/env python3
"""
将数据库中的比赛数据导出到debug目录，供前端API读取
"""
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

print("正在将数据库数据导出到debug目录...")

# 连接数据库
db_path = 'data/sport_lottery.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查询比赛数据
cursor.execute("""
SELECT match_id, home_team, away_team, match_time, league, status,
       odds_home_win, odds_draw, odds_away_win, popularity
FROM football_matches ORDER BY match_time
""")
matches = cursor.fetchall()

print(f"从数据库获取到 {len(matches)} 场比赛")

# 准备导出数据
exported_matches = []
weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

for idx, match in enumerate(matches):
    match_id, home_team, away_team, match_time, league, status, odds_hw, odds_draw, odds_aw, popularity = match
    
    # 解析日期获取星期
    dt = datetime.strptime(match_time, '%Y-%m-%d %H:%M:%S')
    weekday_idx = dt.weekday()
    weekday_prefix = weekdays[weekday_idx]
    
    # 生成格式化的match_id（类似500彩票网的格式）
    formatted_match_id = f"{weekday_prefix}{idx+1:02d}"
    
    exported_match = {
        "match_id": formatted_match_id,
        "league": league,
        "home_team": home_team,
        "away_team": away_team,
        "match_time": match_time,
        "odds_home_win": float(odds_hw) if odds_hw else 0.0,
        "odds_draw": float(odds_draw) if odds_draw else 0.0,
        "odds_away_win": float(odds_aw) if odds_aw else 0.0,
        "status": status,
        "score": "-:-",
        "popularity": popularity if popularity else 7000
    }
    exported_matches.append(exported_match)

# 确保debug目录存在
project_root = Path(__file__).parent
debug_dir = project_root / "debug"
debug_dir.mkdir(exist_ok=True)

# 生成文件名
filename = f"500_com_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
filepath = debug_dir / filename

# 写入文件
with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(exported_matches, f, ensure_ascii=False, indent=2)

print(f"✓ 数据已导出到: {filepath}")
print(f"✓ 共导出 {len(exported_matches)} 场比赛")

# 同时创建一个latest链接文件
latest_filepath = debug_dir / "500_com_matches_latest.json"
with open(latest_filepath, 'w', encoding='utf-8') as f:
    json.dump(exported_matches, f, ensure_ascii=False, indent=2)

print(f"✓ Latest文件已更新: {latest_filepath}")

# 显示导出的数据概览
print("\n导出数据概览：")
print("ID      主队        客队        时间              联赛    胜   平   负   热度")
print("-" * 85)
for match in exported_matches[:5]:  # 只显示前5条
    print(f"{match['match_id']}  {match['home_team']:<10} {match['away_team']:<10} {match['match_time']}  {match['league']:<6} {match['odds_home_win']:.2f} {match['odds_draw']:.2f} {match['odds_away_win']:.2f} {match['popularity']}")

if len(exported_matches) > 5:
    print(f"... 还有 {len(exported_matches) - 5} 条记录")

conn.close()
print("\n✅ 导出完成！现在重启后端服务后刷新页面即可看到数据")
