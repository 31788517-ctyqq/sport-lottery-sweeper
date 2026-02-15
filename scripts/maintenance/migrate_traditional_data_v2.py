import sqlite3
import re
from datetime import datetime

def get_table_columns(conn, table_name):
    """获取表的所有列名"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return columns

def migrate_traditional_data_v2():
    # 读取示例数据文件
    with open('data/seed/sport_lottery_sample_data.sql', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 连接目标数据库
    target_conn = sqlite3.connect('data/sport_lottery.db')
    target_cursor = target_conn.cursor()
    
    # 提取所有INSERT语句
    insert_blocks = re.findall(r'(INSERT.*?;)', content, re.DOTALL | re.IGNORECASE)
    
    print(f"Found {len(insert_blocks)} INSERT blocks")
    
    total_migrated = 0
    for i, insert_block in enumerate(insert_blocks):
        try:
            # 解析INSERT语句
            table_match = re.search(r'INSERT.*?INTO\s+(\w+)\s*\(([^)]+)\)', insert_block, re.IGNORECASE)
            if not table_match:
                continue
                
            table_name = table_match.group(1)
            provided_columns = [col.strip() for col in table_match.group(2).split(',')]
            
            # 获取目标表的实际列
            actual_columns = get_table_columns(target_conn, table_name)
            
            # 找出共同的列
            common_columns = [col for col in provided_columns if col in actual_columns]
            
            if not common_columns:
                print(f"Skipping {table_name}: no common columns")
                continue
            
            print(f"Processing {table_name}: mapping {len(provided_columns)} → {len(common_columns)} columns")
            
            # 提取VALUES
            values_match = re.search(r'VALUES\s*(.+);', insert_block, re.IGNORECASE | re.DOTALL)
            if not values_match:
                continue
                
            values_text = values_match.group(1).strip()
            
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
            
            # 构建INSERT语句（只使用共同列）
            placeholders = ','.join(['?' for _ in common_columns])
            columns_str = ','.join(common_columns)
            insert_sql = f"INSERT OR IGNORE INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # 映射值到共同列
            for group in value_groups:
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
                
                if len(values) == len(provided_columns):
                    # 只保留共同列对应的值
                    mapped_values = []
                    for col in common_columns:
                        idx = provided_columns.index(col)
                        mapped_values.append(values[idx])
                    
                    try:
                        target_cursor.execute(insert_sql, mapped_values)
                        total_migrated += 1
                    except Exception as e:
                        print(f"Error inserting into {table_name}: {e}")
                        continue
            
        except Exception as e:
            print(f"Error processing block {i+1}: {e}")
            continue
    
    target_conn.commit()
    target_conn.close()
    
    print(f"Migration completed! Total migrated: {total_migrated} records")

if __name__ == "__main__":
    migrate_traditional_data_v2()