#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Docker修复和Redis启动脚本
用于修复Docker镜像拉取问题并启动Redis服务以支持MCP Server
"""

import subprocess
import sys
import time
import os


def restart_docker_desktop():
    """重启Docker Desktop"""
    print("尝试重启Docker Desktop...")
    
    try:
        # 尝试通过任务管理器结束Docker进程
        subprocess.run(['taskkill', '/f', '/im', 'Docker Desktop.exe'], 
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['taskkill', '/f', '/im', 'Docker.exe'], 
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("已终止Docker进程，正在启动Docker Desktop...")
        # 启动Docker Desktop
        result = subprocess.run([
            'start', '""', '"C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"'
        ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Docker Desktop 启动命令已发送。请等待几分钟让Docker完全启动。")
        print("建议等待至少2分钟，让Docker服务完全初始化。")
        return True
    except Exception as e:
        print(f"重启Docker Desktop时出错: {e}")
        return False


def configure_docker_registry_mirror():
    """配置Docker镜像源（如果需要）"""
    print("配置Docker镜像源...")
    
    # 获取Docker daemon配置路径
    daemon_json_path = os.path.expanduser('~/.docker/daemon.json')
    
    # 创建或更新daemon.json文件
    daemon_config = '''{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ],
  "insecure-registries": [],
  "debug": false,
  "experimental": false
}'''
    
    try:
        # 写入配置文件
        os.makedirs(os.path.dirname(daemon_json_path), exist_ok=True)
        with open(daemon_json_path, 'w', encoding='utf-8') as f:
            f.write(daemon_config)
        
        print(f"已创建Docker配置文件: {daemon_json_path}")
        print("请重启Docker Desktop以应用配置更改")
        return True
    except Exception as e:
        print(f"配置Docker镜像源时出错: {e}")
        return False


def clean_docker_resources():
    """清理Docker资源"""
    print("清理Docker资源...")
    
    try:
        # 清理构建缓存
        subprocess.run(['docker', 'builder', 'prune', '-a', '-f'], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 清理系统缓存
        subprocess.run(['docker', 'system', 'prune', '-a', '-f'], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Docker资源清理完成")
        return True
    except Exception as e:
        print(f"清理Docker资源时出错: {e}")
        return False


def test_docker_connection():
    """测试Docker连接"""
    print("测试Docker连接...")
    
    try:
        result = subprocess.run(['docker', 'version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True, 
                               timeout=30)
        
        if result.returncode == 0:
            print("✓ Docker连接正常")
            return True
        else:
            print(f"✗ Docker连接失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Docker连接超时")
        return False
    except Exception as e:
        print(f"✗ Docker连接错误: {e}")
        return False


def pull_redis_image_with_retry():
    """带重试机制的Redis镜像拉取"""
    print("尝试拉取Redis镜像...")
    
    # 尝试多个Redis镜像标签
    redis_tags = ['redis:7-alpine', 'redis:latest', 'redis:7.0-alpine']
    
    for tag in redis_tags:
        print(f"正在拉取 {tag}...")
        try:
            result = subprocess.run([
                'docker', 'pull', tag
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✓ 成功拉取 {tag}")
                return tag
            else:
                print(f"✗ 拉取 {tag} 失败: {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"✗ 拉取 {tag} 超时")
        except Exception as e:
            print(f"✗ 拉取 {tag} 错误: {e}")
    
    return None


def start_redis_container(image_tag):
    """启动Redis容器"""
    print(f"使用镜像 {image_tag} 启动Redis容器...")
    
    try:
        # 检查是否已有名为 mcp-redis 的容器
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=mcp-redis'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True)
        
        if 'mcp-redis' in result.stdout:
            # 如果容器存在，先移除它
            print("移除现有的Redis容器...")
            subprocess.run(['docker', 'rm', '-f', 'mcp-redis'], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
        
        # 运行Redis容器
        run_result = subprocess.run([
            'docker', 'run', 
            '--name', 'mcp-redis', 
            '-p', '6379:6379', 
            '-d', image_tag,
            '--maxmemory', '256mb',
            '--maxmemory-policy', 'allkeys-lru'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if run_result.returncode != 0:
            print(f"启动Redis容器失败: {run_result.stderr}")
            return False
        
        print("Redis容器已启动，等待服务准备就绪...")
        # 等待几秒钟让Redis准备就绪
        time.sleep(10)
        
        # 验证Redis是否可以连接
        verify_result = subprocess.run([
            'docker', 'exec', 'mcp-redis', 'redis-cli', 'ping'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if 'PONG' in verify_result.stdout:
            print("✓ Redis服务已启动并可连接")
            return True
        else:
            print("✗ Redis服务启动失败或无法连接")
            return False
            
    except Exception as e:
        print(f"启动Redis容器时出错: {e}")
        return False


def main():
    print("开始修复Docker和启动Redis服务...")
    print("="*50)
    
    # 1. 测试当前Docker连接状态
    if not test_docker_connection():
        print("\nDocker未运行或连接有问题，我们将尝试修复...")
        
        # 2. 重启Docker Desktop
        print("\n第1步: 重启Docker Desktop")
        restart_docker_desktop()
        
        print("\n请等待几分钟让Docker服务完全启动，然后按Enter键继续...")
        input()
        
        # 3. 再次测试Docker连接
        if not test_docker_connection():
            print("\nDocker仍未正常运行，尝试配置镜像源...")
            
            # 4. 配置Docker镜像源
            print("\n第2步: 配置Docker镜像源")
            configure_docker_registry_mirror()
            
            print("\n请重启Docker Desktop应用配置更改，然后按Enter键继续...")
            input()
        
        # 5. 再次测试Docker连接
        if not test_docker_connection():
            print("\nDocker仍然无法连接，请确保Docker Desktop已正确安装和启动")
            return False
    
    # 6. 清理Docker资源
    print("\n第3步: 清理Docker资源")
    clean_docker_resources()
    
    # 7. 再次测试Docker连接
    if not test_docker_connection():
        print("\nDocker连接仍存在问题")
        return False
    
    # 8. 尝试拉取Redis镜像
    print("\n第4步: 拉取Redis镜像")
    image_tag = pull_redis_image_with_retry()
    
    if not image_tag:
        print("\n无法拉取Redis镜像，请检查网络连接或尝试其他解决方案")
        return False
    
    # 9. 启动Redis容器
    print("\n第5步: 启动Redis容器")
    if start_redis_container(image_tag):
        print("\n" + "="*50)
        print("✅ Redis服务已成功启动！")
        print("\n现在您可以运行MCP Server Redis命令:")
        print("npx -y @modelcontextprotocol/server-redis redis://localhost:6379")
        print("="*50)
        return True
    else:
        print("\nRedis容器启动失败")
        return False


if __name__ == "__main__":
    main()