#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MCP Server Redis 解决方案
提供多种方法来启动 Redis 服务以支持 MCP Server
"""

import os
import platform
import subprocess
import sys
import time
import socket


def check_redis_installed():
    """检查系统是否已安装 Redis"""
    try:
        # 检查 redis-server 是否在 PATH 中
        result = subprocess.run(['where', 'redis-server'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                shell=True)
        return result.returncode == 0
    except Exception:
        return False


def start_redis_windows():
    """在 Windows 上启动 Redis 服务（如果已安装）"""
    print("尝试启动本地 Redis 服务...")
    
    try:
        # 尝试启动 Redis 服务（如果作为 Windows 服务安装）
        result = subprocess.run(['redis-server', '--version'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True)
        
        if result.returncode == 0:
            print("Redis 已安装，版本信息:", result.stdout.strip())
            
            # 启动 Redis 服务器
            print("启动 Redis 服务器...")
            redis_process = subprocess.Popen(['redis-server'])
            
            # 等待几秒让服务启动
            time.sleep(3)
            
            # 验证服务是否运行
            if check_redis_running():
                print("✓ 本地 Redis 服务已启动")
                return redis_process
            else:
                print("✗ 本地 Redis 服务启动失败")
                return None
        else:
            print("Redis 未安装或不在 PATH 中")
            return None
    except FileNotFoundError:
        print("Redis 未安装或不在 PATH 中")
        return None
    except Exception as e:
        print(f"启动本地 Redis 时出错: {e}")
        return None


def check_redis_running():
    """检查 Redis 是否正在运行"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 6379))
        sock.close()
        return result == 0
    except Exception:
        return False


def run_docker_redis_alternative():
    """使用 Docker 运行 Redis 的替代方法"""
    print("尝试使用 Docker 运行 Redis...")
    
    # 先尝试拉取镜像
    print("正在拉取 Redis 镜像...")
    try:
        # 尝试使用更通用的 Redis 镜像
        pull_result = subprocess.run(['docker', 'pull', 'redis:latest'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True)
        
        if pull_result.returncode != 0:
            print(f"拉取 Redis 镜像失败: {pull_result.stderr}")
            return False
        
        print("Redis 镜像拉取成功")
        
        # 检查是否有已停止的容器
        ps_result = subprocess.run(['docker', 'ps', '-a', '-q', '-f', 'name=mcp-redis'], 
                                   stdout=subprocess.PIPE, 
                                   text=True)
        
        if ps_result.stdout.strip():
            # 移除旧容器
            print("移除现有容器...")
            subprocess.run(['docker', 'rm', '-f', 'mcp-redis'], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
        
        # 运行 Redis 容器
        print("启动 Redis 容器...")
        run_result = subprocess.run([
            'docker', 'run', 
            '--name', 'mcp-redis',
            '-p', '6379:6379', 
            '-d', 'redis:latest',
            '--requirepass', ''  # 不设置密码
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if run_result.returncode != 0:
            print(f"启动 Redis 容器失败: {run_result.stderr}")
            return False
        
        # 等待服务启动
        print("等待 Redis 服务启动...")
        time.sleep(5)
        
        # 验证 Redis 是否可连接
        if check_redis_running():
            print("✓ Docker Redis 服务已启动并可连接")
            return True
        else:
            print("✗ Docker Redis 服务启动失败")
            return False
            
    except Exception as e:
        print(f"运行 Docker Redis 时出错: {e}")
        return False


def provide_manual_steps():
    """提供手动安装 Redis 的步骤"""
    print("\n=== 手动安装 Redis 的步骤 ===")
    print("\n选项 1: 使用 WSL2 (推荐)")
    print("  1. 安装 WSL2: wsl --install")
    print("  2. 安装 Ubuntu: 从 Microsoft Store 安装")
    print("  3. 在 WSL2 中运行: sudo apt update && sudo apt install redis-server")
    print("  4. 启动 Redis: sudo service redis-server start")
    
    print("\n选项 2: 使用 Redis for Windows")
    print("  1. 访问: https://github.com/tporadowski/redis/releases")
    print("  2. 下载最新版本的 Redis for Windows")
    print("  3. 解压到一个目录")
    print("  4. 运行 redis-server.exe")
    
    print("\n选项 3: 修复 Docker 问题")
    print("  1. 重启 Docker Desktop")
    print("  2. 在 Docker 设置中重置 Kubernetes 集群")
    print("  3. 清理 Docker 构建缓存")
    print("  4. 更换网络或使用国内镜像源")


def main():
    print("开始解决 MCP Server Redis 连接问题...")
    print("目标: 启动 Redis 服务以便 MCP Server 可以连接")
    
    # 检查本地是否已安装 Redis
    print("\n检查本地是否已安装 Redis...")
    if check_redis_installed():
        print("✓ 检测到本地已安装 Redis")
        redis_process = start_redis_windows()
        if redis_process:
            print("\n✓ 本地 Redis 服务已启动")
            print("现在您可以运行 MCP Server Redis 命令:")
            print("npx -y @modelcontextprotocol/server-redis redis://localhost:6379")
            return
    else:
        print("✗ 本地未检测到 Redis")
    
    # 尝试使用 Docker 启动 Redis
    print("\n尝试使用 Docker 启动 Redis...")
    if run_docker_redis_alternative():
        print("\n✓ Docker Redis 服务已启动")
        print("现在您可以运行 MCP Server Redis 命令:")
        print("npx -y @modelcontextprotocol/server-redis redis://localhost:6379")
        return
    else:
        print("✗ Docker Redis 启动失败")
    
    # 提供手动解决方案
    provide_manual_steps()
    
    print("\n=== 总结 ===")
    print("要解决 MCP Server Redis 初始化失败的问题，您需要确保 Redis 服务在 localhost:6379 上运行。")
    print("一旦 Redis 服务启动，您就可以运行以下命令:")
    print("npx -y @modelcontextprotocol/server-redis redis://localhost:6379")


if __name__ == "__main__":
    main()