import sqlite3
import sys

def main():
    db_path = 'data/sport_lottery.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='football_matches'")
    if not cursor.fetchone():
        print("表 football_matches 不存在")
        return
    
    # 获取表结构
    cursor.execute('PRAGMA table_info(football_matches)')
    columns = cursor.fetchall()
    
    print("表 football_matches 结构:")
    for col in columns:
        cid, name, type_, notnull, dflt_value, pk = col
        nullable = "NULL" if notnull == 0 else "NOT NULL"
        default = f"DEFAULT {dflt_value}" if dflt_value is not None else ""
        print(f"  {cid}: {name} {type_} {nullable} {default}")
    
    conn.close()

if __name__ == '__main__':
    main()