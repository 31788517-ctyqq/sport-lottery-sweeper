import sqlite3
import os

def add_missing_columns():
    """
    添加缺失的数据库列
    """
    # 使用相对路径构建数据库路径
    db_path = os.path.join(os.path.dirname(__file__), 'sport_lottery.db')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查并添加缺失的列
        columns_to_add = [
            ("last_error", "TEXT", "上次错误信息"),
            ("last_error_time", "DATETIME", "上次错误时间"),
        ]
        
        for col_name, col_type, col_comment in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE data_sources ADD COLUMN {col_name} {col_type};")
                print(f'成功添加 {col_name} 列 ({col_comment})')
            except sqlite3.OperationalError as e:
                if 'duplicate column name' in str(e):
                    print(f'{col_name} 列已存在')
                else:
                    print(f'添加 {col_name} 列时出错: {e}')
        
        conn.commit()
        print("数据库表结构更新完成")
        return True
    except Exception as e:
        print(f"更新数据库表结构时出错: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("开始更新数据库表结构...")
    add_missing_columns()
    print("更新完成")