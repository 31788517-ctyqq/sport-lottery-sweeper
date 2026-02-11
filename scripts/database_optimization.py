#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库性能优化脚本
用于分析和优化数据库性能，包括索引优化和查询优化
"""

import os
import sys
from pathlib import Path
import sqlite3
import time
from typing import List, Dict, Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_database_path():
    """获取数据库路径"""
    # 检查环境变量或使用默认路径
    db_path = os.getenv("DATABASE_PATH", "sport_lottery.db")
    
    # 如果是相对路径，拼接项目根目录
    if not Path(db_path).is_absolute():
        db_path = Path.cwd() / db_path
    
    return str(db_path)


def analyze_database_performance(db_path: str):
    """分析数据库性能"""
    logger.info(f"开始分析数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        logger.info(f"发现 {len(tables)} 个表")
        
        table_info = {}
        for table in tables:
            table_name = table[0]
            
            # 获取表行数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            
            # 获取列信息
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # 获取索引信息
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}';")
            indexes = cursor.fetchall()
            
            table_info[table_name] = {
                'rows': row_count,
                'columns': len(columns),
                'indexes': len(indexes),
                'columns_details': [col[1] for col in columns]
            }
            
            logger.info(f"表 {table_name}: {row_count} 行, {len(columns)} 列, {len(indexes)} 索引")
        
        conn.close()
        return table_info
        
    except Exception as e:
        logger.error(f"分析数据库时出错: {str(e)}")
        return {}


def suggest_indexes(table_info: Dict):
    """建议添加索引"""
    suggestions = []
    
    for table_name, info in table_info.items():
        # 对于大型表，建议对经常查询的列添加索引
        if info['rows'] > 10000:
            for col in info['columns_details']:
                # 建议对ID、状态、时间戳等列添加索引
                if any(keyword in col.lower() for keyword in ['id', 'status', 'created', 'updated', 'time', 'date']):
                    index_name = f"idx_{table_name}_{col}"
                    suggestions.append({
                        'table': table_name,
                        'column': col,
                        'index_name': index_name,
                        'reason': f"大表({info['rows']}行)的{col}列可能需要索引"
                    })
    
    return suggestions


def optimize_database(db_path: str):
    """执行数据库优化"""
    logger.info("开始数据库优化...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 执行VACUUM优化
        logger.info("执行VACUUM优化...")
        cursor.execute("VACUUM;")
        logger.info("VACUUM优化完成")
        
        # 执行ANALYZE收集统计信息
        logger.info("收集统计信息...")
        cursor.execute("ANALYZE;")
        logger.info("统计信息收集完成")
        
        conn.commit()
        conn.close()
        
        logger.info("数据库优化完成")
        return True
        
    except Exception as e:
        logger.error(f"数据库优化失败: {str(e)}")
        return False


def create_optimized_indexes(db_path: str, suggestions: List[Dict]):
    """创建优化的索引"""
    logger.info(f"开始创建 {len(suggestions)} 个建议的索引")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        created_indexes = []
        for suggestion in suggestions:
            table = suggestion['table']
            column = suggestion['column']
            index_name = suggestion['index_name']
            
            # 检查索引是否已存在
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{index_name}';")
            if cursor.fetchone():
                logger.info(f"索引 {index_name} 已存在，跳过")
                continue
            
            # 创建索引
            sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table} ({column});"
            cursor.execute(sql)
            created_indexes.append(index_name)
            logger.info(f"已创建索引: {index_name}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"成功创建了 {len(created_indexes)} 个索引")
        return created_indexes
        
    except Exception as e:
        logger.error(f"创建索引失败: {str(e)}")
        return []


def run_database_optimization():
    """运行数据库优化流程"""
    print("=" * 60)
    print("数据库性能优化")
    print("=" * 60)
    
    db_path = get_database_path()
    
    if not Path(db_path).exists():
        logger.error(f"数据库文件不存在: {db_path}")
        return False
    
    print(f"数据库路径: {db_path}")
    
    # 分析数据库性能
    print("\n🔍 分析数据库结构...")
    table_info = analyze_database_performance(db_path)
    
    if not table_info:
        logger.error("无法分析数据库结构")
        return False
    
    # 提供建议
    print("\n💡 生成优化建议...")
    suggestions = suggest_indexes(table_info)
    
    print(f"共生成 {len(suggestions)} 个索引建议:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. 表 '{suggestion['table']}' 的 '{suggestion['column']}' 列 - {suggestion['reason']}")
    
    # 执行优化
    print("\n🔧 执行数据库优化...")
    optimize_success = optimize_database(db_path)
    
    if optimize_success and suggestions:
        print("\n🔨 创建建议的索引...")
        created_indexes = create_optimized_indexes(db_path, suggestions)
        print(f"成功创建了 {len(created_indexes)} 个索引")
    
    print("\n✅ 数据库优化完成!")
    
    return True


if __name__ == "__main__":
    success = run_database_optimization()
    sys.exit(0 if success else 1)