#!/usr/bin/env python
"""
Seed 数据运行器
功能：在数据库为空时导入 data/seed/sport_lottery_sample_data.sql
避免重复插入数据
"""
import os
import sqlite3
import sys

# 项目根目录
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'data/sport_lottery.db')
SQL_SEED_PATH = os.path.join(PROJECT_ROOT, 'data', 'seed', 'sport_lottery_sample_data.sql')

def db_has_data(conn):
    """检查 leagues 或 teams 表是否已有数据"""
    cur = conn.cursor()
    # 检查 leagues
    cur.execute("SELECT COUNT(*) FROM leagues")
    leagues_count = cur.fetchone()[0]
    if leagues_count > 0:
        return True
    # 检查 teams
    cur.execute("SELECT COUNT(*) FROM teams")
    teams_count = cur.fetchone()[0]
    return teams_count > 0

def run_seed():
    if not os.path.exists(SQL_SEED_PATH):
        print(f"❌ 未找到种子数据文件: {SQL_SEED_PATH}")
        sys.exit(1)

    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    if db_has_data(conn):
        print("[INFO] 数据库中已有数据，跳过种子数据导入")
        conn.close()
        return

    print("[INFO] 正在导入种子数据...")
    with open(SQL_SEED_PATH, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    cur = conn.cursor()
    # 用 executescript 执行多条 SQL（注意事务性）
    try:
        cur.executescript(sql_script)
        conn.commit()
        print("[INFO] 种子数据导入完成")
    except Exception as e:
        conn.rollback()
        print(f"❌ 导入种子数据失败: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    run_seed()
