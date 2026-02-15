import sqlite3
import re

def parse_insert_statement(insert_sql):
    """解析INSERT语句，返回表名、列名和值列表"""
    # 提取表名和列名
    table_match = re.search(r'INSERT.*?INTO\s+(\w+)\s*\(([^)]+)\)', insert_sql, re.IGNORECASE)
    if not table_match:
        return None, None, []
    
    table_name = table_match.group(1)
    columns = [col.strip() for col in table_match.group(2).split(',')]
    
    # 提取VALUES部分
    values_match = re.search(r'VALUES\s*(.+);', insert_sql, re.IGNORECASE | re.DOTALL)
    if not values_match:
        return table_name, columns, []
    
    values_text = values_match.group(1).strip()
    
    # 分割多个值组（处理括号内的逗号）
    value_groups = []
    current_group = ""
    paren_count = 0
    in_string = False
    escape_next = False
    
    for char in values_text:
        if escape_next:
            current_group += char
            escape_next = False
            continue
            
        if char == '\\' and in_string:
            escape_next = True
            current_group += char
            continue
            
        if char == "'" and not escape_next:
            in_string = not in_string
            
        if char == '(' and not in_string:
            paren_count += 1
            current_group += char
        elif char == ')' and not in_string:
            paren_count -= 1
            current_group += char
            if paren_count == 0:
                value_groups.append(current_group[1:-1])  # 去掉外层括号
                current_group = ""
        else:
            current_group += char
    
    # 解析每个值组
    parsed_values = []
    for group in value_groups:
        values = []
        current_value = ""
        in_str = False
        escape = False
        
        for char in group + ",":  # 添加逗号以便处理最后一个值
            if escape:
                current_value += char
                escape = False
                continue
                
            if char == '\\' and in_str:
                escape = True
                current_value += char
                continue
                
            if char == "'" and not escape:
                in_str = not in_str
                current_value += char
            elif char == "," and not in_str:
                # 处理当前值
                val = current_value.strip()
                if val.startswith("'") and val.endswith("'"):
                    values.append(val[1:-1])
                elif val.lower() == 'null':
                    values.append(None)
                elif val == '':
                    values.append(None)
                else:
                    # 尝试转换为数字
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
        
        if values:
            parsed_values.append(values)
    
    return table_name, columns, parsed_values

def migrate_traditional_data():
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
            table_name, columns, values_list = parse_insert_statement(insert_block)
            
            if not table_name or not columns or not values_list:
                print(f"Skipping block {i+1}: Could not parse")
                continue
            
            print(f"Processing {table_name}: {len(values_list)} records")
            
            # 构建INSERT语句
            placeholders = ','.join(['?' for _ in columns])
            columns_str = ','.join(columns)
            insert_sql = f"INSERT OR IGNORE INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # 执行批量插入
            for values in values_list:
                try:
                    target_cursor.execute(insert_sql, values)
                    total_migrated += 1
                except Exception as e:
                    print(f"Error inserting into {table_name}: {e}")
                    print(f"Values: {values}")
                    continue
            
        except Exception as e:
            print(f"Error processing block {i+1}: {e}")
            continue
    
    target_conn.commit()
    target_conn.close()
    
    print(f"Migration completed! Total migrated: {total_migrated} records")

if __name__ == "__main__":
    migrate_traditional_data()