#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动 Redis 服务以支持 MCP Server
此脚本将检查 Docker 状态并启动 Redis 容器
"""

import subprocess
import sys
import time
import socket


def check_docker_running():
    """检查 Docker 是否正在运行"""
    try:
        result = subprocess.run(['docker', 'info'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True, 
                                timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def start_redis_container():
    """启动 Redis 容器"""
    print("正在启动 Redis 容器...")
    try:
        # 检查是否已有名为 mcp-redis 的容器
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=mcp-redis'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True)
        
        if 'mcp-redis' in result.stdout:
            # 如果容器存在，检查其状态
            container_status = subprocess.run(['docker', 'ps', '--filter', 'name=mcp-redis', '--format', '{{.Status}}'], 
                                              stdout=subprocess.PIPE, 
                                              text=True)
            
            if 'Up' in container_status.stdout:
                print("Redis 容器已在运行中")
                return True
            else:
                # 容器存在但未运行，启动它
                print("启动已存在的 Redis 容器...")
                start_result = subprocess.run(['docker', 'start', 'mcp-redis'], 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE, 
                                              text=True)
                if start_result.returncode != 0:
                    print(f"启动现有容器失败: {start_result.stderr}")
                    return False
        else:
            # 创建并启动新的 Redis 容器
            print("创建并启动新的 Redis 容器...")
            run_result = subprocess.run([
                'docker', 'run', 
                '--name', 'mcp-redis', 
                '-p', '6379:6379', 
                '-d', 'redis:7-alpine'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if run_result.returncode != 0:
                print(f"启动 Redis 容器失败: {run_result.stderr}")
                return False
        
        # 等待几秒钟让 Redis 准备就绪
        print("等待 Redis 服务准备就绪...")
        time.sleep(5)
        
        # 验证 Redis 是否可以连接
        if verify_redis_connection():
            print("✓ Redis 服务已成功启动并可以连接")
            return True
        else:
            print("✗ Redis 容器已启动，但服务尚未准备好")
            return False
            
    except Exception as e:
        print(f"启动 Redis 容器时出错: {e}")
        return False


def verify_redis_connection():
    """验证 Redis 连接"""
    # 尝试使用 telnet 连接到 Redis 端口
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 6379))
        sock.close()
        return result == 0
    except Exception:
        return False


def main():
    print("检查 Docker 状态...")
    
    if not check_docker_running():
        print("Docker 未运行或未安装，请:")
        print("1. 确保已安装 Docker Desktop")
        print("2. 启动 Docker Desktop 应用程序")
        print("3. 等待 Docker 服务完全启动")
        print("")
        print("启动 Docker Desktop 后，请重新运行此脚本")
        return False
    
    print("✓ Docker 正在运行")
    
    # 启动 Redis 容器
    if start_redis_container():
        print("")
        print("Redis 服务已准备就绪！")
        print("现在您可以运行 MCP Server Redis:")
        print("npx -y @modelcontextprotocol/server-redis redis://localhost:6379")
        return True
    else:
        print("无法启动 Redis 服务")
        return False


if __name__ == "__main__":
    main()