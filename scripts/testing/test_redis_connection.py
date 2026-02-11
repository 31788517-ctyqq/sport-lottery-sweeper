#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Redis 连接测试脚本
用于测试本地 Redis 服务是否正常运行
"""

import redis
import sys
import subprocess
import os


def test_redis_connection():
    """测试 Redis 连接"""
    try:
        # 尝试连接本地 Redis 服务
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        print("✓ 成功连接到 Redis 服务!")
        return True
    except redis.ConnectionError:
        print("✗ 无法连接到 Redis 服务，请确保 Redis 服务正在运行。")
        return False
    except Exception as e:
        print(f"✗ Redis 连接发生未知错误: {e}")
        return False


def install_redis_windows():
    """提供在 Windows 上安装 Redis 的指导"""
    print("\n在 Windows 上安装 Redis 的方法:")
    print("1. 使用 WSL2 (推荐):")
    print("   - 安装 WSL2")
    print("   - 在 WSL2 中安装 Redis: sudo apt-get install redis-server")
    print("   - 启动 Redis: sudo service redis-server start")
    
    print("\n2. 使用 Docker Desktop:")
    print("   - 下载并安装 Docker Desktop for Windows")
    print("   - 启动 Docker Desktop")
    print("   - 运行命令: docker run --name redis-container -p 6379:6379 -d redis:7-alpine")
    
    print("\n3. 使用 Redis for Windows (非官方):")
    print("   - 访问 https://github.com/tporadowski/redis/releases")
    print("   - 下载最新版本的 Redis for Windows")
    print("   - 解压并运行 redis-server.exe")


def main():
    print("正在测试 Redis 连接...")
    print("目标地址: localhost:6379")
    
    if test_redis_connection():
        print("\nRedis 服务已就绪，MCP Server 应该能够正常连接。")
    else:
        print("\nRedis 服务未运行或未安装。")
        install_redis_windows()
        
        # 尝试使用 Docker 启动 Redis（如果 Docker 可用）
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("\n检测到 Docker 已安装，可以使用以下命令启动 Redis:")
                print("docker run --name mcp-redis -p 6379:6379 -d redis:7-alpine")
            else:
                print("\n未检测到 Docker，请先安装 Docker Desktop。")
        except FileNotFoundError:
            print("\n未检测到 Docker，请先安装 Docker Desktop。")


if __name__ == "__main__":
    main()