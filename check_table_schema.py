import sqlite3
import sys

def check_table_schema():
    conn = sqlite3.connect('data/sport_lottery.db')
    cursor = conn.cursor()
    
    # 检查football_matches表结构
    cursor.execute("PRAGMA table_info(football_matches)")
    columns = cursor.fetchall()
    
    print("football_matches表结构:")
    print("-" * 80)
    for col in columns:
        cid, name, type_, notnull, dflt_value, pk = col
        notnull_str = "NOT NULL" if notnull else "NULL"
        print(f"{cid}: {name} ({type_}) {notnull_str} default={dflt_value} pk={pk}")
    
    # 特别检查date_time和line_id字段
    print("\n特别检查date_time和line_id字段:")
    for col in columns:
        if col[1] in ['date_time', 'line_id']:
            cid, name, type_, notnull, dflt_value, pk = col
            print(f"{name}: notnull={notnull}, type={type_}, default={dflt_value}")
    
    # 检查数据库中已有的100qiu数据
    print("\n数据库中已有的100qiu数据样本:")
    cursor.execute("SELECT match_id, date_time, line_id FROM football_matches WHERE data_source='100qiu' LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"match_id: {row[0]}, date_time: {row[1]}, line_id: {row[2]}")
    
    # 检查数据源ID 9的配置
    print("\n数据源ID 9的配置:")
    cursor.execute("SELECT id, name, type, config FROM data_sources WHERE id = 9")
    row = cursor.fetchone()
    if row:
        id, name, type, config_str = row
        print(f"ID: {id}, 名称: {name}, 类型: {type}")
        print(f"配置: {config_str}")
    
    conn.close()

if __name__ == "__main__":
    check_table_schema()