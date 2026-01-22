"""测试API集成"""
import json
import os
from pathlib import Path

# 获取最新的数据文件
debug_dir = Path(__file__).parent / "debug"
files = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_")]

print(f"找到 {len(files)} 个数据文件")

if files:
    latest_file = sorted(files)[-1]
    file_path = debug_dir / latest_file
    
    print(f"最新文件: {latest_file}")
    
    # 读取数据
    with open(file_path, 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    print(f"总比赛数: {len(matches)}")
    
    # 过滤表头
    matches = [m for m in matches if m.get('match_id') != '编号']
    print(f"过滤后: {len(matches)}")
    
    # 筛选周一比赛
    monday_matches = [m for m in matches if m.get('match_id', '').startswith('周一')]
    print(f"\n周一比赛数: {len(monday_matches)}")
    
    if monday_matches:
        print("\n周一5场比赛:")
        for match in monday_matches:
            print(f"  [{match['match_id']}] {match['league']} | {match['home_team']} vs {match['away_team']} | {match['match_time']}")
    else:
        print("❌ 没有找到周一的比赛！")
        print("\n所有比赛编号:")
        for m in matches[:10]:
            print(f"  - {m.get('match_id')}")
