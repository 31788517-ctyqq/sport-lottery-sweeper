#!/usr/bin/env python3
"""
查询数据库中特定数据源的脚本
"""

import sys
import os
import sqlite3
from backend.config import settings

def find_specific_data_sources():
    """查询数据库中特定的数据源"""
    try:
        # 获取数据库URL并提取路径
        db_url = settings.DATABASE_URL
        if db_url.startswith('sqlite:///'):
            db_path = db_url[10:]  # 移除 'sqlite:///' 前缀
            
            # 连接到SQLite数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 查询data_sources表的记录
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
                    return
                
                # 搜索特定的数据源
                keywords = ['500', '彩票', '100qiu', '体彩']
                
                print("正在搜索特定数据源...")
                print("=" * 60)
                
                # 搜索包含关键词的数据源
                for keyword in keywords:
                    cursor.execute("""
                        SELECT id, name, type, 
                               CASE WHEN status THEN '启用' ELSE '禁用' END, 
                               url 
                        FROM data_sources 
                        WHERE name LIKE ? OR url LIKE ?
                    """, (f'%{keyword}%', f'%{keyword}%'))
                    
                    rows = cursor.fetchall()
                    
                    if rows:
                        print(f"找到包含 '{keyword}' 的数据源:")
                        for idx, row in enumerate(rows, 1):
                            print(f"  {idx}. ID: {row[0]}, 名称: {row[1]}, 类型: {row[2]}, "
                                  f"状态: {row[3]}, URL: {row[4]}")
                    else:
                        print(f"未找到包含 '{keyword}' 的数据源")
                    print("-" * 40)
                
                # 查询所有数据源以便全面了解
                cursor.execute("""
                    SELECT id, name, type, 
                           CASE WHEN status THEN '启用' ELSE '禁用' END, 
                           url 
                    FROM data_sources
                """)
                
                all_rows = cursor.fetchall()
                
                print("完整的数据源列表:")
                for idx, row in enumerate(all_rows, 1):
                    print(f"{idx}. ID: {row[0]}, 名称: {row[1]}, 类型: {row[2]}, "
                          f"状态: {row[3]}, URL: {row[4]}")
                
                print("=" * 60)
                
                # 检查是否包含特定的数据源
                found_sources = []
                for row in all_rows:
                    name = row[1].lower()
                    url = row[4].lower() if row[4] else ""
                    
                    if '500' in name or '500' in url:
                        if '彩票' in name or '彩票' in url:
                            found_sources.append(f"500彩票网相关: {row[1]} (ID: {row[0]})")
                    
                    if '体彩' in name or '体彩' in url or '体育彩票' in name or '体育彩票' in url:
                        found_sources.append(f"中国体育彩票相关: {row[1]} (ID: {row[0]})")
                    
                    if '100qiu' in name or '100qiu' in url:
                        found_sources.append(f"100qiu相关: {row[1]} (ID: {row[0]})")
                
                if found_sources:
                    print("找到的特定数据源:")
                    for source in found_sources:
                        print(f"  - {source}")
                else:
                    print("数据库中未找到 500彩票网、中国体育彩票官网、100qiu 等特定数据源")
                
                conn.close()
                
            except sqlite3.Error as e:
                print(f"数据库查询错误: {str(e)}")
                conn.close()
        else:
            print(f"不支持的数据库类型: {db_url}")
            
    except Exception as e:
        print(f"查询数据源时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    find_specific_data_sources()