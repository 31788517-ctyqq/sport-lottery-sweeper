import codecs

# 尝试不同编码
encodings = ['utf-8', 'gbk', 'latin1']

for encoding in encodings:
    try:
        with open('data/seed/sport_lottery_sample_data.sql', 'r', encoding=encoding) as f:
            content = f.read()
            print(f"Successfully read with {encoding} encoding")
            
            # 查找联赛相关数据
            lines = content.split('\n')
            league_lines = [line for line in lines if 'leagues' in line.lower() and 'insert' in line.lower()]
            team_lines = [line for line in lines if 'teams' in line.lower() and 'insert' in line.lower()]
            
            print(f"League INSERT statements: {len(league_lines)}")
            print(f"Team INSERT statements: {len(team_lines)}")
            
            if league_lines:
                print("Sample league data:")
                for i, line in enumerate(league_lines[:3]):
                    print(f"  {i+1}: {line.strip()}")
                    
            break
            
    except UnicodeDecodeError:
        print(f"Failed to read with {encoding} encoding")
        continue