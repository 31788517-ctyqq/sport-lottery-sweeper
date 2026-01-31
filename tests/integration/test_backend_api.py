import json
import os
from datetime import datetime

# 模拟后端API的逻辑
def test_api():
    print("=== Testing Backend API Logic ===\n")
    
    # 1. 检查debug目录
    debug_dir = os.path.join(os.path.dirname(__file__), "debug")
    print(f"Debug directory: {debug_dir}")
    print(f"Directory exists: {os.path.exists(debug_dir)}\n")
    
    # 2. 查找文件
    if os.path.exists(debug_dir):
        files = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_")]
        print(f"Found {len(files)} files matching '500_com_matches_*':")
        for f in files:
            print(f"  - {f}")
        print()
        
        if files:
            # 3. 获取最新文件
            latest_file = sorted(files)[-1]
            file_path = os.path.join(debug_dir, latest_file)
            print(f"Latest file: {latest_file}")
            print(f"Full path: {file_path}\n")
            
            # 4. 读取数据
            with open(file_path, 'r', encoding='utf-8') as f:
                matches = json.load(f)
            
            print(f"Total matches in file: {len(matches)}")
            
            # 5. 过滤表头
            matches = [m for m in matches if m.get('match_id') != '编号']
            print(f"After filtering header: {len(matches)}")
            
            # 6. 筛选周一比赛
            monday_matches = [m for m in matches if m.get('match_id', '').startswith('周一')]
            print(f"Monday matches found: {len(monday_matches)}\n")
            
            if monday_matches:
                print("Monday matches:")
                for match in monday_matches:
                    print(f"  - {match['match_id']} | {match['league']} | {match['home_team']} vs {match['away_team']} | {match['match_time']}")
            else:
                print("[WARNING] No Monday matches found!")
                print("\nShowing all match IDs:")
                for match in matches[:10]:
                    print(f"  - {match.get('match_id', 'NO_ID')}")
        else:
            print("[WARNING] No files found matching pattern!")
    else:
        print("[ERROR] Debug directory does not exist!")

if __name__ == "__main__":
    test_api()
