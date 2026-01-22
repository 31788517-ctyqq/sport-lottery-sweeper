#!/usr/bin/env python
"""
Simple script to start the backend service
"""
import sys
import os

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')
sys.path.insert(0, current_dir)

# 设置PYTHONPATH，让模块可以正确导入
os.chdir(backend_dir)

# 更改工作目录到backend，这样相对导入可以正常工作
import subprocess
subprocess.run([sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'])