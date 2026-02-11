#!/usr/bin/env python3
"""
为数据源表添加source_id字段
"""

import sys
import os
import sqlite3
from pathlib import Path


def add_source_id_column():
    """为数据源表添加source_id字段并更新现有记录"""
    try:
        # 使用项目根目录下的数据库文件
        project_root = Path(__file__).parent
        db_path = project_root / "sport_lottery.db"
        
        if not db_path.exists():
            print(f"数据库文件不存在: {db_path}")
            return
        
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print(f"为数据库表添加source_id字段: {db_path}")
        print("=" * 60)
        
        # 检查是否已存在source_id列
        cursor.execute("PRAGMA table_info(data_sources);")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'source_id' not in columns:
            print("source_id列不存在，正在添加...")
            
            # 添加source_id列
            cursor.execute("ALTER TABLE data_sources ADD COLUMN source_id VARCHAR(10);")
            
            # 为现有的数据源记录生成source_id
            cursor.execute("SELECT id, name FROM data_sources;")
            existing_sources = cursor.fetchall()
            
            for source_id, name in existing_sources:
                # 生成source_id，格式为DS+3位数字ID
                formatted_id = f"DS{source_id:03d}"
                cursor.execute(
                    "UPDATE data_sources SET source_id = ? WHERE id = ?;",
                    (formatted_id, source_id)
                )
                print(f"  更新数据源 {source_id} ({name}) 的 source_id 为 {formatted_id}")
            
            # 为新创建的数据源（ID为8）也更新source_id
            cursor.execute(
                "UPDATE data_sources SET source_id = ? WHERE id = ?;",
                ("DS008", 8)
            )
            print(f"  更新数据源 8 (100球网比赛数据-新) 的 source_id 为 DS008")
            
            conn.commit()
            print("✅ 成功添加source_id列并更新了现有记录")
        else:
            print("source_id列已存在")
        
        # 验证更新结果
        print("\n验证更新结果:")
        cursor.execute("SELECT id, name, source_id FROM data_sources ORDER BY id DESC LIMIT 10;")
        updated_sources = cursor.fetchall()
        
        for source_id, name, source_id_value in updated_sources:
            print(f"  ID: {source_id}, Name: {name}, Source ID: {source_id_value}")
        
        conn.close()
                
    except Exception as e:
        print(f"更新数据库结构时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    add_source_id_column()