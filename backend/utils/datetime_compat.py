#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DateTime兼容工具模块
解决datetime.utcnow()弃用警告的临时方案
"""

import datetime
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def utcnow():
    """兼容版本的utcnow()，返回timezone-aware的UTC时间"""
    return datetime.datetime.now(datetime.timezone.utc)

def utcnow_naive():
    """返回naive的UTC时间（兼容旧代码）"""
    return datetime.datetime.utcnow()

def patch_datetime():
    """为datetime模块打补丁，减少修改范围"""
    # 保存原始方法
    original_utcnow = getattr(datetime.datetime, 'utcnow', None)
    
    # 检查是否可以修改（在某些Python版本中，datetime类是不可变的）
    try:
        # 尝试替换方法
        def patched_utcnow():
            return datetime.datetime.now(datetime.timezone.utc)
        
        # 只有当original_utcnow不是None时才使用wraps
        if original_utcnow:
            patched_utcnow = wraps(original_utcnow)(patched_utcnow)
        
        # 尝试设置新方法，如果失败则跳过
        datetime.datetime.utcnow = patched_utcnow
        logger.info("datetime补丁已应用")
        return original_utcnow
    except (AttributeError, TypeError):
        # 如果无法修改，静默处理
        logger.warning("无法应用datetime补丁（通常是Python版本兼容性问题，不影响功能）")
        return original_utcnow

# 使用示例：
# from utils.datetime_compat import utcnow, patch_datetime
# patch_datetime()  # 在程序开始时调用一次