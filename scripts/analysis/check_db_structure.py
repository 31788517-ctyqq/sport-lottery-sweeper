import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine
from sqlalchemy import inspect

def check_db_structure():
    insp = inspect(engine)
    tables = insp.get_table_names()
    print('数据库中存在的表:')
    for table in tables:
        print(f'- {table}')
    
    # 检查特定表的结构
    if 'football_matches' in tables:
        print('\nfootball_matches表结构:')
        columns = insp.get_columns('football_matches')
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")

    if 'crawler_task_logs' in tables:
        print('\ncrawler_task_logs表结构:')
        columns = insp.get_columns('crawler_task_logs')
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")

    if 'crawler_tasks' in tables:
        print('\ncrawler_tasks表结构:')
        columns = insp.get_columns('crawler_tasks')
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")

    if 'data_sources' in tables:
        print('\ndata_sources表结构:')
        columns = insp.get_columns('data_sources')
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")

if __name__ == '__main__':
    check_db_structure()