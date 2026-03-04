#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Docker服务重启脚本
用于重启使用Docker容器的完整服务栈
"""

import subprocess
import sys
import time
import os


def check_docker_running():
    """检查Docker是否正在运行"""
    try:
        result = subprocess.run(['docker', 'info'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True, 
                                timeout=10, 
                                encoding='utf-8')
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def stop_existing_containers():
    """停止现有的Docker容器"""
    print("停止现有的Docker容器...")
    
    # 停止所有正在运行的容器
    try:
        ps_result = subprocess.run(['docker', 'ps', '-q'], 
                                  capture_output=True, text=True, encoding='utf-8')
        if ps_result.stdout.strip():
            container_ids = ps_result.stdout.strip().split()
            subprocess.run(['docker', 'stop'] + container_ids, 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass  # 如果没有运行的容器，忽略错误
    
    # 删除所有容器
    try:
        ps_all_result = subprocess.run(['docker', 'ps', '-aq'], 
                                      capture_output=True, text=True, encoding='utf-8')
        if ps_all_result.stdout.strip():
            container_ids = ps_all_result.stdout.strip().split()
            subprocess.run(['docker', 'rm', '-f'] + container_ids,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass  # 如果没有容器，忽略错误
    
    print("现有容器已清理")


def start_redis_container():
    """启动Redis容器"""
    print("启动Redis容器...")
    
    # 检查Redis容器是否已存在
    result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=mcp-redis'], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           text=True, 
                           encoding='utf-8')
    
    if result.stdout and 'mcp-redis' in result.stdout:
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
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        
        if run_result.returncode != 0:
            print(f"启动Redis容器失败: {run_result.stderr}")
            return False
    
    # 等待Redis服务准备就绪
    print("等待Redis服务准备就绪...")
    time.sleep(5)
    
    # 验证Redis是否可以连接
    try:
        verify_result = subprocess.run([
            'docker', 'exec', 'mcp-redis', 'redis-cli', 'ping'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        
        if verify_result.stdout and 'PONG' in verify_result.stdout:
            print("✓ Redis服务已启动并可连接")
            return True
        else:
            print("✗ Redis服务启动失败或无法连接")
            return False
    except Exception as e:
        print(f"验证Redis连接时出错: {e}")
        return False


def start_backend_service():
    """启动后端服务"""
    print("启动后端服务...")
    
    try:
        # 初始化数据库和管理员账户
        print("初始化管理员账户...")
        init_result = subprocess.run([
            sys.executable, 'scripts/admin/init_admin_and_roles.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        
        if init_result.returncode != 0:
            print(f"初始化管理员账户失败: {init_result.stderr}")
        else:
            print("管理员账户初始化完成")
        
        # 启动后端服务
        backend_process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 
            'backend.main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000'
        ])
        
        print("后端服务已启动 (端口 8000)")
        return backend_process
    except Exception as e:
        print(f"启动后端服务失败: {e}")
        return None


def main():
    print("开始重启Sport Lottery Sweeper系统 (Docker模式)...")
    print("="*60)
    
    # 检查Docker是否运行
    if not check_docker_running():
        print("Docker未运行，请先启动Docker Desktop应用程序")
        print("启动Docker Desktop后，请稍等几分钟让服务完全启动，然后再次运行此脚本。")
        return False
    
    print("✓ Docker服务正在运行")
    
    # 1. 停止现有容器
    stop_existing_containers()
    
    print()
    
    # 2. 启动Redis容器
    if not start_redis_container():
        print("Redis容器启动失败，无法继续")
        return False
    
    print()
    
    # 3. 启动后端服务
    backend_process = start_backend_service()
    if not backend_process:
        print("后端服务启动失败")
        return False
    
    print()
    
    # 4. 显示登录信息
    print("="*60)
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
    print("访问地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
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
        
        # 清理Docker容器
        try:
            subprocess.run(['docker', 'stop', 'mcp-redis'], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
        
        print("服务已停止")


if __name__ == "__main__":
    main()