#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重启服务脚本
用于重启整个Sport Lottery Sweeper系统，包括所有依赖服务
"""

import subprocess
import sys
import time
import os
import signal
from typing import List


def stop_existing_services():
    """停止现有的服务进程"""
    print("停止现有服务...")
    
    # 尝试停止Docker容器
    try:
        subprocess.run(['docker-compose', 'down'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        print("已停止Docker服务")
    except FileNotFoundError:
        print("Docker命令不可用，跳过Docker服务停止")

    # 结束可能占用端口的进程
    ports_to_check = [8000, 3000, 6379, 5432, 5555]
    for port in ports_to_check:
        try:
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
                    if len(parts) > 4:
                        pid = parts[4]
                        print(f"结束占用端口{port}的进程(PID: {pid})")
                        subprocess.run(['taskkill', '/f', '/pid', pid], 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"检查端口{port}时出错: {e}")


def start_redis_service():
    """启动Redis服务"""
    print("启动Redis服务...")
    
    # 检查Redis容器是否已存在
    result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=mcp-redis'], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           text=True)
    
    if 'mcp-redis' in result.stdout:
        # 启动已存在的容器
        subprocess.run(['docker', 'start', 'mcp-redis'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        print("Redis容器已启动")
    else:
        # 创建并启动新的Redis容器
        run_result = subprocess.run([
            'docker', 'run', 
            '--name', 'mcp-redis', 
            '-p', '6379:6379', 
            '-d', 'redis:7.0-alpine',
            '--maxmemory', '256mb',
            '--maxmemory-policy', 'allkeys-lru'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if run_result.returncode != 0:
            print(f"启动Redis容器失败: {run_result.stderr}")
            return False
    
    # 等待Redis服务准备就绪
    time.sleep(5)
    print("Redis服务已启动")
    return True


def start_backend_service():
    """启动后端服务"""
    print("启动后端服务...")
    
    try:
        # 初始化数据库和管理员账户
        print("初始化管理员账户...")
        init_result = subprocess.run([
            sys.executable, 'scripts/admin/init_admin_and_roles.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if init_result.returncode != 0:
            print(f"初始化管理员账户失败: {init_result.stderr}")
        else:
            print("管理员账户初始化完成")
        
        # 在后台启动后端服务
        backend_process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 
            'backend.main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000', 
            '--reload'
        ])
        
        print("后端服务已启动 (端口 8000)")
        return backend_process
    except Exception as e:
        print(f"启动后端服务失败: {e}")
        return None


def main():
    print("开始重启Sport Lottery Sweeper系统...")
    print("="*50)
    
    # 1. 停止现有服务
    stop_existing_services()
    
    print()
    
    # 2. 启动Redis服务
    if not start_redis_service():
        print("Redis服务启动失败，无法继续")
        return False
    
    print()
    
    # 3. 启动后端服务
    backend_process = start_backend_service()
    if not backend_process:
        print("后端服务启动失败")
        return False
    
    print()
    
    # 4. 显示登录信息
    print("="*50)
    print("✅ 系统重启完成！")
    print()
    print("系统已启动以下服务:")
    print("- Redis 服务 (端口 6379)")
    print("- 后端 API 服务 (端口 8000)")
    print()
    print("管理员账户信息:")
    print("- 用户名: admin")
    print("- 密码: admin123")
    print("- 权限: super_admin (全部权限)")
    print()
    print("请使用以上账户登录系统以访问全部功能，包括日志版块。")
    print()
    print("按 Ctrl+C 停止服务")
    
    try:
        # 等待用户中断
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        print("服务已停止")


if __name__ == "__main__":
    main()