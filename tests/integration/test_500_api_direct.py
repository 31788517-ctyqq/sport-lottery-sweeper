"""直接测试500彩票网API逻辑"""
import json
import os
from pathlib import Path

# 模拟API逻辑
debug_dir = Path(__file__).parent / "debug"
source = "500"

files = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_")]
print(f"找到文件数: {len(files)}")

if files:
    latest_file = sorted(files)[-1]
    print(f"最新文件: {latest_file}")
    
    file_path = debug_dir / latest_file
    
    with open(file_path, 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    print(f"读取比赛数: {len(matches)}")
    
    # 过滤表头
    matches = [m for m in matches if m.get('match_id') != '编号']
    print(f"过滤后: {len(matches)}")
    
    # 筛选周一
    monday_matches = [m for m in matches if m.get('match_id', '').startswith('周一')]
    print(f"周一比赛: {len(monday_matches)}")
    
    if monday_matches:
        matches = monday_matches
        print("\n周一5场比赛:")
        for match in matches:
            print(f"  [{match['match_id']}] {match['league']} | {match['home_team']} vs {match['away_team']}")
        
        # 测试数据转换
        formatted = {
            "success": True,
            "data": matches,
            "total": len(matches),
            "message": f"成功获取{len(matches)}场比赛数据"
        }
        print(f"\n返回结果:")
        print(f"  success: {formatted['success']}")
        print(f"  total: {formatted['total']}")
        print(f"  message: {formatted['message']}")
    else:
        print("[ERROR] 没有周一比赛！")
else:
    print("[ERROR] 没有数据文件！")
