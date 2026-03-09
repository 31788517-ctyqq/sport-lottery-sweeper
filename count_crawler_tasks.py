#!/usr/bin/env python3
"""
查询数据库中爬虫任务数量的脚本
"""

import sys
import os
import sqlite3
from backend.config import settings

def count_crawler_tasks():
    """直接连接数据库并查询爬虫任务表"""
    try:
        # 获取数据库URL并提取路径
        db_url = settings.DATABASE_URL
        if db_url.startswith('sqlite:///'):
            db_path = db_url[10:]  # 移除 'sqlite:///' 前缀
            
            # 连接到SQLite数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 检查crawler_tasks表是否存在
            try:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='crawler_tasks';
                """)
                
                table_exists = cursor.fetchone()
                if not table_exists:
                    print("数据表 'crawler_tasks' 不存在")
                    
                    # 检查另一个可能的表名
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='crawler_task';
                    """)
                    
                    alt_table_exists = cursor.fetchone()
                    if not alt_table_exists:
                        print("数据表 'crawler_task' 也不存在")
                        conn.close()
                        return 0
                    else:
                        print("发现备用表 'crawler_task'")
                        table_name = 'crawler_task'
                else:
                    table_name = 'crawler_tasks'
                
                # 计算爬虫任务总数
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                total_count = cursor.fetchone()[0]
                
                # 查询启用的任务数量
                if table_name == 'crawler_tasks':
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE is_active = 1")
                    active_count = cursor.fetchone()[0]
                    
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE is_active = 0")
                    inactive_count = cursor.fetchone()[0]
                    
                    status_col = 'is_active'
                else:  # crawler_task表
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE status = 'running'")
                    active_count = cursor.fetchone()[0]
                    
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE status = 'idle' OR status = 'paused'")
                    inactive_count = cursor.fetchone()[0]
                    
                    status_col = 'status'
                
                print("=" * 60)
                print(f"数据库中爬虫任务统计信息 (表: {table_name}):")
                print(f"总任务数量: {total_count}")
                print(f"活跃/启用的任务: {active_count}")
                print(f"非活跃/禁用的任务: {inactive_count}")
                print("=" * 60)
                
                # 显示所有爬虫任务的详细信息
                if total_count > 0:
                    print("\n爬虫任务详情:")
                    
                    if table_name == 'crawler_tasks':
                        cursor.execute("""
                            SELECT id, name, source_id, task_type, cron_expression, 
                                   is_active, status, last_run_time, next_run_time,
                                   run_count, success_count, error_count
                            FROM crawler_tasks
                        """)
                        rows = cursor.fetchall()
                        for idx, row in enumerate(rows, 1):
                            print(f"{idx}. ID: {row[0]}, 名称: {row[1]}, 源ID: {row[2]}, "
                                  f"类型: {row[3]}, Cron: {row[4]}, 启用: {row[5]}, "
                                  f"状态: {row[6]}, 上次运行: {row[7]}, 下次运行: {row[8]}, "
                                  f"运行次数: {row[9]}, 成功: {row[10]}, 错误: {row[11]}")
                    else:  # crawler_task表
                        cursor.execute("""
                            SELECT id, name, source_id, cron_expr, next_run_time, status, created_at
                            FROM crawler_task
                        """)
                        rows = cursor.fetchall()
                        for idx, row in enumerate(rows, 1):
                            print(f"{idx}. ID: {row[0]}, 名称: {row[1]}, 源ID: {row[2]}, "
                                  f"Cron: {row[3]}, 下次运行: {row[4]}, 状态: {row[5]}, 创建时间: {row[6]}")
                
                conn.close()
                return total_count
                
            except sqlite3.Error as e:
                print(f"数据库查询错误: {str(e)}")
                conn.close()
                return 0
        else:
            print(f"不支持的数据库类型: {db_url}")
            return 0
            
    except Exception as e:
        print(f"查询爬虫任务时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


if __name__ == "__main__":
    count = count_crawler_tasks()
    print(f"\n系统中共有 {count} 个爬虫任务")