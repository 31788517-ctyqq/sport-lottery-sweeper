#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动时调试 - 测试数据加载
"""
import sys
import logging
logger = logging.getLogger(__name__)
import os

# 设置路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger.debug("=" * 70)
logger.debug("启动时调试 - 测试数据加载")
logger.debug("=" * 70)
logger.debug(f"项目根目录: {project_root}")
logger.debug()

# 直接测试数据加载
try:
    from pathlib import Path
    import json
    
    # 方法1: 使用绝对路径
    debug_dir = Path(r"c:\Users\11581\Downloads\sport-lottery-sweeper\debug")
    logger.debug(f"测试路径: {debug_dir}")
    logger.debug(f"路径存在: {debug_dir.exists()}")
    
    if debug_dir.exists():
        files = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_")]
        logger.debug(f"找到文件: {files}")
        
        if files:
            file_path = debug_dir / files[0]
            logger.debug(f"读取文件: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"成功加载 {len(data)} 条数据")
            
            if data:
                logger.debug(f"第一条: {data[0]}")
    else:
        logger.debug(f"错误: debug目录不存在")
        
except Exception as e:
    logger.debug(f"错误: {e}")
    import traceback
    traceback.print_exc()

logger.debug("\n" + "=" * 70)
logger.debug("调试完成")
logger.debug("=" * 70)
