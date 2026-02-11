#!/usr/bin/env python3
"""
简单查询数据库中数据源数量的脚本，绕过模型冲突问题
"""

import sys
import os
import sqlite3
from backend.config import settings

def count_data_sources():
    """直接连接数据库并查询数据源表"""
    try:
        # 获取数据库URL并提取路径
        db_url = settings.DATABASE_URL
        if db_url.startswith('sqlite:///'):
            db_path = db_url[10:]  # 移除 'sqlite:///' 前缀
            
            # 连接到SQLite数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 查询data_sources表的记录数
            try:
                # 首先检查表是否存在
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='data_sources';
                """)
                
                table_exists = cursor.fetchone()
                if not table_exists:
                    print("数据表 'data_sources' 不存在")
                    conn.close()
                    return 0
                
                # 计算数据源总数
                cursor.execute("SELECT COUNT(*) FROM data_sources")
                total_count = cursor.fetchone()[0]
                
                # 检查表结构来决定如何计算启用/禁用数量
                cursor.execute("PRAGMA table_info(data_sources)")
                columns_info = [col[1] for col in cursor.fetchall()]
                
                print(f"数据源表列结构: {columns_info}")
                
                # 根据不同的列名计算启用/禁用数量
                if 'is_active' in columns_info:
                    # SP数据源表结构
                    cursor.execute("SELECT COUNT(*) FROM data_sources WHERE is_active = 1")
                    active_count = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(*) FROM data_sources WHERE is_active = 0")
                    inactive_count = cursor.fetchone()[0]
                    
                    active_col = 'is_active'
                    status_desc = "SP数据源表结构 (使用 is_active)"
                elif 'status' in columns_info:
                    # 普通数据源表结构
                    cursor.execute("SELECT COUNT(*) FROM data_sources WHERE status = 1")
                    active_count = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(*) FROM data_sources WHERE status = 0")
                    inactive_count = cursor.fetchone()[0]
                    
                    active_col = 'status'
                    status_desc = "普通数据源表结构 (使用 status)"
                else:
                    # 无状态列的情况
                    active_count = "N/A"
                    inactive_count = "N/A"
                    active_col = None
                    status_desc = "无状态列"
                
                print("=" * 60)
                print(f"数据库中数据源统计信息 ({status_desc}):")
                print(f"总数据源数量: {total_count}")
                print(f"启用的数据源: {active_count}")
                print(f"禁用的数据源: {inactive_count}")
                print("=" * 60)
                
                # 显示所有数据源的详细信息
                if total_count > 0:
                    print("\n数据源详情:")
                    
                    if 'source_id' in columns_info:  # SP数据源表结构
                        cursor.execute("""
                            SELECT id, source_id, name, source_type, category, 
                                   CASE WHEN is_active THEN '启用' ELSE '禁用' END, 
                                   api_url 
                            FROM data_sources
                        """)
                        rows = cursor.fetchall()
                        for idx, row in enumerate(rows, 1):
                            print(f"{idx}. ID: {row[0]}, 源ID: {row[1]}, 名称: {row[2]}, "
                                  f"类型: {row[3]}, 分类: {row[4]}, 状态: {row[5]}, URL: {row[6]}")
                    elif 'status' in columns_info:  # 普通数据源表结构
                        cursor.execute("""
                            SELECT id, name, type, 
                                   CASE WHEN status THEN '启用' ELSE '禁用' END, 
                                   url 
                            FROM data_sources
                        """)
                        rows = cursor.fetchall()
                        for idx, row in enumerate(rows, 1):
                            print(f"{idx}. ID: {row[0]}, 名称: {row[1]}, 类型: {row[2]}, "
                                  f"状态: {row[3]}, URL: {row[4]}")
                    else:  # 不包含状态列的情况
                        cursor.execute("SELECT * FROM data_sources LIMIT 10")
                        rows = cursor.fetchall()
                        for idx, row in enumerate(rows, 1):
                            print(f"{idx}. {row}")
                
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
        print(f"查询数据源时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


if __name__ == "__main__":
    count = count_data_sources()
    print(f"\n系统中共有 {count} 条数据源")