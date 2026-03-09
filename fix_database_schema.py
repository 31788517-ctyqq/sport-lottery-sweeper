import sqlite3
import os

def fix_database_schema():
    """修复数据库表结构，添加缺失的列"""
    db_path = "data/sport_lottery.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表的列信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # 需要修复的表和列
        tables_to_fix = {
            'llm_providers': [
                'created_by INTEGER',
                'updated_by INTEGER', 
                'deleted_by INTEGER'
            ],
            'admin_users': [
                'created_by INTEGER',
                'updated_by INTEGER',
                'deleted_by INTEGER'
            ],
            'users': [
                'created_by INTEGER',
                'updated_by INTEGER',
                'deleted_by INTEGER'
            ]
            # 可以根据需要添加更多表
        }
        
        print("开始修复数据库表结构...")
        
        for table_name, columns_to_add in tables_to_fix.items():
            if table_name not in tables:
                print(f"  跳过 {table_name}: 表不存在")
                continue
            
            # 获取现有列
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            added_columns = 0
            for column_def in columns_to_add:
                column_name = column_def.split()[0]
                if column_name not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_def}")
                        print(f"  ✓ 添加列 {column_name} 到表 {table_name}")
                        added_columns += 1
                    except sqlite3.OperationalError as e:
                        print(f"  ✗ 添加列 {column_name} 失败: {e}")
                else:
                    print(f"  - 列 {column_name} 已存在")
            
            if added_columns > 0:
                print(f"  表 {table_name} 修复完成 ({added_columns} 列已添加)")
            else:
                print(f"  表 {table_name} 无需修复")
        
        conn.commit()
        conn.close()
        print("\n数据库表结构修复完成！")
        
    except Exception as e:
        print(f"修复数据库时出错: {e}")

if __name__ == "__main__":
    fix_database_schema()