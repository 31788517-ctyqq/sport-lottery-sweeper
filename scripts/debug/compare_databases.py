#!/usr/bin/env python3
"""对比两个数据库中的日志数据"""

import sqlite3
from pathlib import Path

def get_log_counts(db_path):
    """获取数据库中的日志统计信息"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='log_entries'")
        if not cursor.fetchone():
            conn.close()
            return {"error": "log_entries table not found"}
            
        # 获取总日志数
        cursor.execute("SELECT COUNT(*) FROM log_entries")
        total_logs = cursor.fetchone()[0]
        
        # 获取各模块日志数
        cursor.execute("SELECT module, COUNT(*) FROM log_entries GROUP BY module")
        module_counts = dict(cursor.fetchall())
        
        # 获取各级别日志数  
        cursor.execute("SELECT level, COUNT(*) FROM log_entries GROUP BY level")
        level_counts = dict(cursor.fetchall())
        
        # 获取最新日志时间
        cursor.execute("SELECT MAX(created_at) FROM log_entries")
        latest_log = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_logs": total_logs,
            "module_counts": module_counts,
            "level_counts": level_counts,
            "latest_log": latest_log
        }
    except Exception as e:
        return {"error": str(e)}

def compare_databases():
    """对比两个数据库"""
    project_root = Path(__file__).resolve().parent
    
    db1_path = project_root / "data/sport_lottery.db"
    db2_path = project_root / "test.db"
    
    print(f"=== 对比数据库 ===")
    print(f"主数据库: {db1_path}")
    print(f"测试数据库: {db2_path}")
    print()
    
    stats1 = get_log_counts(db1_path)
    stats2 = get_log_counts(db2_path)
    
    print("=== 主数据库 (sport_lottery.db) ===")
    if "error" in stats1:
        print(f"错误: {stats1['error']}")
    else:
        print(f"总日志数: {stats1['total_logs']}")
        print(f"模块分布: {stats1['module_counts']}")
        print(f"级别分布: {stats1['level_counts']}")
        print(f"最新日志: {stats1['latest_log']}")
    
    print()
    print("=== 测试数据库 (test.db) ===")
    if "error" in stats2:
        print(f"错误: {stats2['error']}")
    else:
        print(f"总日志数: {stats2['total_logs']}")
        print(f"模块分布: {stats2['module_counts']}")
        print(f"级别分布: {stats2['level_counts']}")
        print(f"最新日志: {stats2['latest_log']}")
    
    print()
    if "error" not in stats1 and "error" not in stats2:
        if stats1['total_logs'] == stats2['total_logs']:
            print("✅ 两个数据库的日志总数一致")
        else:
            print("❌ 两个数据库的日志总数不一致!")
            print(f"   sport_lottery.db: {stats1['total_logs']}")
            print(f"   test.db: {stats2['total_logs']}")

if __name__ == "__main__":
    compare_databases()