import sqlite3
import re
from datetime import datetime

def migrate_100_ball_data():
    # 读取示例数据文件
    with open('data/seed/sport_lottery_sample_data.sql', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取matches的INSERT语句
    matches_pattern = r"INSERT OR IGNORE INTO matches\s*\([^)]+\)\s*VALUES\s*(.+?);"
    matches_match = re.search(matches_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not matches_match:
        print("No matches INSERT statement found")
        return
    
    values_text = matches_match.group(1).strip()
    
    # 解析值组
    value_groups = []
    current_group = ""
    paren_count = 0
    in_string = False
    
    for char in values_text:
        if char == "'" and (not current_group or current_group[-1] != '\\'):
            in_string = not in_string
            
        if char == '(' and not in_string:
            paren_count += 1
            current_group += char
        elif char == ')' and not in_string:
            paren_count -= 1
            current_group += char
            if paren_count == 0:
                value_groups.append(current_group[1:-1])
                current_group = ""
        else:
            current_group += char
    
    print(f"Found {len(value_groups)} match records to migrate")
    
    # 连接数据库
    conn = sqlite3.connect('sport_lottery.db')
    cursor = conn.cursor()
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    migrated_count = 0
    
    for group in value_groups:
        try:
            # 解析值
            values = []
            current_value = ""
            in_str = False
            
            for char in group + ",":
                if char == "'" and (not current_value or current_value[-1] != '\\'):
                    in_str = not in_str
                    current_value += char
                elif char == "," and not in_str:
                    val = current_value.strip()
                    if val.startswith("'") and val.endswith("'"):
                        values.append(val[1:-1])
                    elif val.lower() == 'null':
                        values.append(None)
                    elif val == '':
                        values.append(None)
                    else:
                        try:
                            if '.' in val:
                                values.append(float(val))
                            else:
                                values.append(int(val))
                        except ValueError:
                            values.append(val)
                    current_value = ""
                else:
                    current_value += char
            
            # 确保有正确的值数量（13个来自示例数据）
            if len(values) >= 13:
                # 构建完整的记录，添加必需的默认值
                full_record = (
                    values[0],  # match_identifier
                    values[1],  # match_date  
                    values[2],  # match_time
                    values[3],  # scheduled_kickoff
                    values[4],  # status
                    values[5],  # importance
                    values[6],  # home_team_id
                    values[7],  # away_team_id
                    values[8],  # league_id
                    values[9],  # home_score
                    values[10], # away_score
                    values[11], # is_published
                    values[12], # type
                    # 添加必需的默认值
                    0,          # is_featured
                    1,          # priority
                    0,          # popularity
                    '{}',       # config
                    now,        # created_at
                    now,        # updated_at
                    0           # is_deleted
                )
                
                cursor.execute("""
                INSERT OR IGNORE INTO matches (
                    match_identifier, match_date, match_time, scheduled_kickoff,
                    status, importance, home_team_id, away_team_id, league_id,
                    home_score, away_score, is_published, type, is_featured,
                    priority, popularity, config, created_at, updated_at, is_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, full_record)
                
                migrated_count += 1
                
        except Exception as e:
            print(f"Error migrating match record: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"100 ball data migration completed! Migrated {migrated_count} records")

if __name__ == "__main__":
    migrate_100_ball_data()