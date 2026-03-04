import sqlite3

def check_database_tables():
    """检查数据库表结构"""
    try:
        conn = sqlite3.connect('data/sport_lottery.db')
        cursor = conn.cursor()
        
        # 查询所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print('数据库中存在的表:')
        for i, table in enumerate(tables, 1):
            print(f'  {i}. {table[0]}')
        
        print(f'\n总共 {len(tables)} 个表')
        
        # 检查特定的关键表是否存在
        essential_tables = [
            'users', 'matches', 'leagues', 'teams', 'predictions', 
            'user_predictions', 'odds', 'admin_users'
        ]
        
        print('\n关键表检查:')
        for table in essential_tables:
            exists = any(table_name[0] == table for table_name in tables)
            status = "✓ 存在" if exists else "✗ 缺失"
            print(f'  - {table}: {status}')
        
        conn.close()
        print('\n数据库检查完成!')
        
    except Exception as e:
        print(f"数据库检查出错: {e}")

if __name__ == "__main__":
    check_database_tables()