#!/usr/bin/env python3
"""
检查数据源和任务之间的关联关系
"""

import sys
import os
import sqlite3
from pathlib import Path

def check_source_task_mapping():
    """检查数据源和任务之间的映射关系"""
    try:
        # 使用项目根目录下的数据库文件
        project_root = Path(__file__).parent
        db_path = project_root / "data/sport_lottery.db"
        
        if not db_path.exists():
            print(f"数据库文件不存在: {db_path}")
            return
        
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print(f"检查数据库: {db_path}")
        print("数据源和任务关联关系检查")
        print("=" * 60)
        
        # 检查数据源表
        cursor.execute("SELECT id, name, url FROM data_sources ORDER BY id")
        sources = cursor.fetchall()
        
        print(f"数据源总数: {len(sources)}")
        for source in sources:
            print(f"ID: {source[0]}, 名称: {source[1]}, URL: {source[2]}")
        
        print("-" * 60)
        
        # 检查任务表
        cursor.execute("SELECT id, name, source_id, status FROM crawler_tasks ORDER BY id")
        tasks = cursor.fetchall()
        
        print(f"爬虫任务总数: {len(tasks)}")
        for task in tasks:
            print(f"ID: {task[0]}, 名称: {task[1]}, 源ID: {task[2]}, 状态: {task[3]}")
        
        print("-" * 60)
        
        # 检查是否存在与"100球网比赛数据"相关的任务
        target_source_ids = []
        for source in sources:
            if "100球网" in source[1]:
                target_source_ids.append(source[0])
        
        if target_source_ids:
            print(f"找到与'100球网'相关的数据源ID: {target_source_ids}")
            
            for sid in target_source_ids:
                cursor.execute("SELECT id, name, source_id, status FROM crawler_tasks WHERE source_id = ?", (sid,))
                related_tasks = cursor.fetchall()
                
                if related_tasks:
                    print(f"与数据源ID {sid} 关联的任务:")
                    for task in related_tasks:
                        print(f"  - 任务ID: {task[0]}, 名称: {task[1]}, 状态: {task[3]}")
                else:
                    print(f"数据源ID {sid} 没有关联的任务，需要手动创建")
        else:
            print("未找到与'100球网'相关的数据源")
        
        conn.close()
                
    except Exception as e:
        print(f"检查数据源任务关联时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_source_task_mapping()