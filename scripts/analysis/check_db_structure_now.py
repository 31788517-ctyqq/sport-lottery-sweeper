import sqlite3
import os

def check_table_structure():
    # 检查数据库文件是否存在
    db_path = './backend/sport_lottery.db'  # 使用正确的数据库路径
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询data_sources表结构
    try:
        cursor.execute("PRAGMA table_info(data_sources);")
        columns = cursor.fetchall()
        
        print("data_sources表结构:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] == 1 else ''} - Default: {col[4]}")
        
        print("\n检查field_mapping列是否存在...")
        field_mapping_exists = any(col[1] == 'field_mapping' for col in columns)
        print(f"field_mapping列存在: {field_mapping_exists}")
        
        if not field_mapping_exists:
            print("\n需要添加field_mapping列到data_sources表")
            # 尝试添加field_mapping列
            try:
                cursor.execute("ALTER TABLE data_sources ADD COLUMN field_mapping TEXT;")
                print("成功添加field_mapping列")
            except Exception as e:
                print(f"添加field_mapping列失败: {e}")
        
        # 检查source_id列
        source_id_exists = any(col[1] == 'source_id' for col in columns)
        print(f"source_id列存在: {source_id_exists}")
        
        if not source_id_exists:
            print("\n需要添加source_id列到data_sources表")
            try:
                cursor.execute("ALTER TABLE data_sources ADD COLUMN source_id TEXT;")
                print("成功添加source_id列")
            except Exception as e:
                print(f"添加source_id列失败: {e}")
        
        conn.commit()
        
    except Exception as e:
        print(f"查询表结构失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_table_structure()