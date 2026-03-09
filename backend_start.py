#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端服务启动脚本
提供更可靠的后端服务启动机制
"""

import subprocess
import sys
import os
import signal
import time
import logging
from pathlib import Path
import psutil
import socket

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_port(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def kill_process_on_port(port):
    """终止占用指定端口的进程"""
    try:
        # 获取占用端口的进程ID
        if os.name == 'nt':  # Windows
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            pids_to_kill = []
            for line in lines:
                if f':{port}' in line or f'{port}' in line.split():
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[4]
                        if pid.isdigit() and pid != '0':
                            pids_to_kill.append(pid)
            
            for pid in pids_to_kill:
                try:
                    logger.info(f"Killing process {pid} on port {port}")
                    subprocess.run(['taskkill', '/F', '/PID', pid], check=True)
                    time.sleep(1)
                except subprocess.CalledProcessError:
                    logger.warning(f"Could not kill process {pid}, might not exist or insufficient permissions")
        else:  # Unix-like systems
            result = subprocess.run(['lsof', '-i', f':{port}'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line:
                        pid = line.split()[1]
                        try:
                            logger.info(f"Killing process {pid} on port {port}")
                            os.kill(int(pid), signal.SIGTERM)
                            time.sleep(1)
                        except ProcessLookupError:
                            logger.info(f"Process {pid} already terminated")
                        except PermissionError:
                            logger.error(f"Permission denied to kill process {pid}. Try running as administrator/root.")
    except Exception as e:
        logger.error(f"Error killing process on port {port}: {e}")

def safe_start_server(host="0.0.0.0", base_port=8001, max_attempts=5):
    """安全启动服务器，自动处理端口冲突"""
    for attempt in range(max_attempts):
        port = base_port + attempt
        
        if not check_port(port):
            logger.warning(f"Port {port} is occupied, trying next port...")
            kill_process_on_port(port)
            time.sleep(2)  # 等待端口释放
            
            # 再次检查端口是否已释放
            if not check_port(port):
                logger.error(f"Cannot free port {port} after attempting to kill process")
                continue
        else:
            logger.info(f"Port {port} is available")
        
        # 设置环境变量以使用可用端口
        env = os.environ.copy()
        env['SERVER_PORT'] = str(port)
        
        try:
            logger.info(f"Attempting to start server on {host}:{port}")
            
            # 导入并启动FastAPI应用
            from backend.main import app
            import uvicorn
            
            logger.info(f"Server starting on {host}:{port}")
            uvicorn.run(app, host=host, port=port, reload=False)
            return  # 成功启动，退出函数
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
            break
        except Exception as e:
            logger.error(f"Failed to start server on port {port}: {e}")
            if attempt == max_attempts - 1:
                logger.error("Max attempts reached, could not start server")
                break
            else:
                logger.info(f"Retrying with next port... (attempt {attempt + 2}/{max_attempts})")
                continue

def main():
    """主函数"""
    logger.info("Starting backend server with enhanced reliability...")
    
    # 获取端口参数，默认8001
    port = 8001
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            logger.error("Invalid port number provided, using default 8001")
    
    safe_start_server(base_port=port)

if __name__ == "__main__":
    main()