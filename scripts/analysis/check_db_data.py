import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

# 设置环境变量以使用正确的数据库
os.environ.setdefault("DATABASE_URL", "sqlite:///./sport_lottery.db")

from backend.database import engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

def check_db_data():
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 检查crawler_tasks表中的数据
        print("=== 爬虫任务数据 ===")
        try:
            tasks = db.execute(text("SELECT id, name, status FROM crawler_tasks LIMIT 10")).fetchall()
            if len(tasks) == 0:
                print("暂无爬虫任务数据")
            else:
                for task in tasks:
                    print(f"任务ID: {task[0]}, 名称: {task[1]}, 状态: {task[2]}")
        except Exception as e:
            print(f"爬虫任务表不存在或查询失败: {e}")
        
        # 检查crawler_task_logs表中的数据
        print("\n=== 爬虫任务日志数据 ===")
        try:
            logs = db.execute(text("SELECT id, task_id, status, records_processed, records_success, records_failed, created_at FROM crawler_task_logs ORDER BY created_at DESC LIMIT 10")).fetchall()
            if len(logs) == 0:
                print("暂无爬虫任务日志数据")
            else:
                for log in logs:
                    print(f"日志ID: {log[0]}, 任务ID: {log[1]}, 状态: {log[2]}, 处理: {log[3]}, 成功: {log[4]}, 失败: {log[5]}, 时间: {log[6]}")
        except Exception as e:
            print(f"爬虫任务日志表不存在或查询失败: {e}")
        
        # 检查football_matches表中的数据
        print("\n=== 比赛数据 ===")
        try:
            matches = db.execute(text("SELECT id, match_id, home_team, away_team, league, status FROM football_matches ORDER BY created_at DESC LIMIT 10")).fetchall()
            if len(matches) == 0:
                print("暂无比赛数据")
            else:
                for match in matches:
                    print(f"比赛ID: {match[0]}, 比赛ID: {match[1]}, 主队: {match[2]}, 客队: {match[3]}, 联赛: {match[4]}, 状态: {match[5]}")
        except Exception as e:
            print(f"比赛数据表不存在或查询失败: {e}")
        
        # 检查data_sources表中的数据
        print("\n=== 数据源数据 ===")
        try:
            sources = db.execute(text("SELECT id, name, type, status, url FROM data_sources LIMIT 10")).fetchall()
            if len(sources) == 0:
                print("暂无数据源数据")
            else:
                for source in sources:
                    print(f"数据源ID: {source[0]}, 名称: {source[1]}, 类型: {source[2]}, 状态: {source[3]}, URL: {source[4]}")
        except Exception as e:
            print(f"数据源表不存在或查询失败: {e}")
        
        # 统计各表数据量
        print("\n=== 数据量统计 ===")
        try:
            tables = ['crawler_tasks', 'crawler_task_logs', 'football_matches', 'data_sources']
            for table in tables:
                count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()[0]
                print(f"{table}: {count} 条记录")
        except Exception as e:
            print(f"数据量统计查询失败: {e}")
    
    finally:
        db.close()

if __name__ == '__main__':
    check_db_data()