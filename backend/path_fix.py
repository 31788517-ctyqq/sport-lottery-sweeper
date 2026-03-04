#!/usr/bin/env python3
"""
Python路径修复模块
在导入任何项目模块之前调用此模块
"""

import sys
import logging
logger = logging.getLogger(__name__)
import os
from pathlib import Path

# 获取项目根目录（backend的父目录）
backend_dir = Path(__file__).parent
project_root = backend_dir.parent

# 确保项目根目录在Python路径中
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    logger.debug(f"[PATH FIX] Added project root to sys.path: {project_root}")

# 确保backend目录在Python路径中
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
    logger.debug(f"[PATH FIX] Added backend dir to sys.path: {backend_dir}")

# 现在可以安全导入项目模块
logger.debug("[PATH FIX] Python path configuration completed")