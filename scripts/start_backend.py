#!/usr/bin/env python
"""
统一启动脚本，整合所有启动功能
支持开发、测试、生产环境的启动
"""
import sys
import os
import argparse
import subprocess
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_port(port: int) -> bool:
    """检查端口是否可用"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('localhost', port))
        return result != 0  # True if port is available

def kill_process_on_port(port: int):
    """终止占用指定端口的进程"""
    import platform
    system = platform.system()
    
    try:
        if system == "Windows":
            # Windows系统
            result = subprocess.run(
                f"netstat -ano | findstr :{port}",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[4]  # PID列
                        logger.info(f"终止PID {pid} 上的进程...")
                        subprocess.run(f"taskkill /PID {pid} /F", shell=True)
        else:
            # Unix-like系统
            result = subprocess.run(
                f"lsof -i :{port} | grep LISTEN",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout:
                pid = result.stdout.split()[1]
                logger.info(f"终止PID {pid} 上的进程...")
                subprocess.run(f"kill -9 {pid}", shell=True)
    except Exception as e:
        logger.error(f"终止端口 {port} 上的进程时出错: {e}")

def start_backend(env: str = "development", port: int = 8000, host: str = "0.0.0.0"):
    """启动后端服务"""
    logger.info(f"正在启动后端服务，环境: {env}, 端口: {port}")
    
    # 设置环境变量
    os.environ['BACKEND_ENV'] = env
    
    # 确保在backend目录中
    backend_dir = Path(__file__).parent.parent / "backend"
    os.chdir(backend_dir)
    
    # 检查端口
    if not check_port(port):
        logger.warning(f"端口 {port} 已被占用，尝试终止占用进程...")
        kill_process_on_port(port)
        import time
        time.sleep(2)  # 等待端口释放
    
    # 构建启动命令
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", host,
        "--port", str(port)
    ]
    
    # 根据环境决定是否使用热重载
    if env == "development":
        cmd.append("--reload")
    
    try:
        logger.info(f"执行启动命令: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"启动后端服务失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n后端服务已停止")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='统一启动脚本')
    parser.add_argument(
        '--env', 
        choices=['development', 'testing', 'production'], 
        default='development',
        help='运行环境 (默认: development)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=8000,
        help='服务端口 (默认: 8000)'
    )
    parser.add_argument(
        '--host', 
        default='0.0.0.0',
        help='服务主机 (默认: 0.0.0.0)'
    )
    
    args = parser.parse_args()
    
    logger.info("启动后端服务...")
    start_backend(args.env, args.port, args.host)

if __name__ == "__main__":
    main()