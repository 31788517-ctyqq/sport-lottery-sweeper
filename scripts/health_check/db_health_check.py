#!/usr/bin/env python
"""
数据库健康检查脚本
检查 Alembic 版本、表结构、示例数据导入情况
"""
import os
import sqlite3
import subprocess
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'data/sport_lottery.db')

def check_alembic_version():
    """检查 Alembic 当前版本"""
    try:
        result = subprocess.run(
            ['alembic', 'current'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return False, f"Alembic 命令执行失败: {result.stderr.strip()}"
        output = result.stdout.strip()
        if 'fd2e6eb3e2ee' in output and '(head)' in output:
            return True, f"Alembic 版本正常: {output}"
        else:
            return False, f"Alembic 版本异常: {output}"
    except Exception as e:
        return False, f"检查 Alembic 版本时出错: {e}"

def check_tables_exist():
    """检查必需的表是否存在"""
    required_tables = ['leagues', 'teams', 'matches']
    if not os.path.exists(DB_PATH):
        return False, f"数据库文件不存在: {DB_PATH}"
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ({}) ".format(
            ','.join(['?'] * len(required_tables))), required_tables))
        existing = [row[0] for row in cur.fetchall()]
        conn.close()
        missing = set(required_tables) - set(existing)
        if missing:
            return False, f"缺少表: {missing}"
        return True, f"所有必需表存在: {existing}"
    except Exception as e:
        return False, f"检查表时出错: {e}"

def check_sample_data():
    """检查示例数据是否已导入"""
    if not os.path.exists(DB_PATH):
        return False, f"数据库文件不存在: {DB_PATH}"
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM leagues")
        leagues_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM teams")
        teams_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM matches")
        matches_count = cur.fetchone()[0]
        conn.close()
        if leagues_count == 0 or teams_count == 0 or matches_count == 0:
            return False, f"数据未导入或不完整: leagues={leagues_count}, teams={teams_count}, matches={matches_count}"
        return True, f"示例数据已导入: leagues={leagues_count}, teams={teams_count}, matches={matches_count}"
    except Exception as e:
        return False, f"检查数据时出错: {e}"

def main():
    print("========================================")
    print("数据库健康检查报告")
    print("========================================\n")

    all_ok = True

    # 1. Alembic 版本
    ok, msg = check_alembic_version()
    print(f"[Alembic 版本] {'✅' if ok else '❌'} {msg}")
    if not ok:
        all_ok = False

    # 2. 表结构
    ok, msg = check_tables_exist()
    print(f"[表结构检查] {'✅' if ok else '❌'} {msg}")
    if not ok:
        all_ok = False

    # 3. 示例数据
    ok, msg = check_sample_data()
    print(f"[示例数据检查] {'✅' if ok else '❌'} {msg}")
    if not ok:
        all_ok = False

    print("\n========================================")
    if all_ok:
        print("🎉 数据库健康状态：正常")
        sys.exit(0)
    else:
        print("⚠️  数据库健康状态：存在问题，请检查上述项目")
        sys.exit(1)

if __name__ == '__main__':
    main()
