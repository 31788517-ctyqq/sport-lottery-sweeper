#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能启动脚本 - 统一管理前后端服务启动
AI_WORKING: coder1 @2026-01-25T00:00:00 - 创建智能启动脚本，支持端口检查和健康检测
"""

import os
import sys
import time
import subprocess
import signal
import psutil
import requests
import argparse
from pathlib import Path
from datetime import datetime

class SmartStart:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / 'backend'
        self.frontend_dir = self.project_root / 'frontend'
        self.logs_dir = self.project_root / 'logs'
        self.logs_dir.mkdir(exist_ok=True)
        
        # 端口配置
        self.frontend_port = 3000
        self.backend_port = 8000
        
        # 进程句柄
        self.backend_process = None
        self.frontend_process = None
        
    def log(self, message, level='INFO'):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        
        # 写入日志文件
        log_file = self.logs_dir / 'startup.log'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def cleanup_port(self, port):
        """清理指定端口的进程"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info['connections'] or []:
                        if conn.laddr.port == port:
                            self.log(f"发现端口 {port} 被进程 {proc.info['pid']} ({proc.info['name']}) 占用，正在终止...")
                            proc.terminate()
                            proc.wait(timeout=5)
                            self.log(f"已终止进程 {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.log(f"清理端口 {port} 时发生错误: {e}", 'ERROR')
    
    def check_port(self, port, timeout=5):
        """检查端口是否可用"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result != 0  # True if port is available
        except Exception:
            return False
    
    def start_backend(self):
        """启动后端服务"""
        self.log("正在启动后端服务...")
        
        # 检查端口
        if not self.check_port(self.backend_port):
            self.log(f"端口 {self.backend_port} 被占用，正在清理...")
            self.cleanup_port(self.backend_port)
            time.sleep(2)
        
        # 启动后端
        try:
            os.chdir(self.backend_dir)
            self.backend_process = subprocess.Popen(
                [sys.executable, 'main.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 等待启动
            self.log("等待后端服务启动...")
            for i in range(30):  # 最多等待30秒
                if self.check_port(self.backend_port):
                    self.log(f"后端服务启动成功，监听端口 {self.backend_port}")
                    return True
                time.sleep(1)
            
            self.log("后端服务启动超时", 'ERROR')
            return False
            
        except Exception as e:
            self.log(f"启动后端服务失败: {e}", 'ERROR')
            return False
    
    def start_frontend(self):
        """启动前端服务"""
        self.log("正在启动前端服务...")
        
        # 检查端口
        if not self.check_port(self.frontend_port):
            self.log(f"端口 {self.frontend_port} 被占用，正在清理...")
            self.cleanup_port(self.frontend_port)
            time.sleep(2)
        
        # 启动前端
        try:
            os.chdir(self.frontend_dir)
            self.frontend_process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 等待启动
            self.log("等待前端服务启动...")
            for i in range(60):  # 最多等待60秒
                if self.check_port(self.frontend_port):
                    self.log(f"前端服务启动成功，监听端口 {self.frontend_port}")
                    return True
                time.sleep(1)
            
            self.log("前端服务启动超时", 'ERROR')
            return False
            
        except Exception as e:
            self.log(f"启动前端服务失败: {e}", 'ERROR')
            return False
    
    def health_check(self):
        """健康检查"""
        self.log("正在进行健康检查...")
        
        results = {
            'backend': False,
            'frontend': False,
            'api_docs': False
        }
        
        # 检查后端健康端点
        try:
            response = requests.get(f'http://localhost:{self.backend_port}/health/live', timeout=5)
            if response.status_code == 200:
                results['backend'] = True
                self.log("✓ 后端服务健康")
            else:
                self.log(f"✗ 后端服务异常: HTTP {response.status_code}", 'WARNING')
        except Exception as e:
            self.log(f"✗ 后端服务不可达: {e}", 'WARNING')
        
        # 检查API文档
        try:
            response = requests.get(f'http://localhost:{self.backend_port}/docs', timeout=5)
            if response.status_code == 200:
                results['api_docs'] = True
                self.log("✓ API文档可访问")
            else:
                self.log(f"✗ API文档异常: HTTP {response.status_code}", 'WARNING')
        except Exception as e:
            self.log(f"✗ API文档不可达: {e}", 'WARNING')
        
        # 检查前端
        try:
            response = requests.get(f'http://localhost:{self.frontend_port}', timeout=5)
            if response.status_code == 200:
                results['frontend'] = True
                self.log("✓ 前端服务可访问")
            else:
                self.log(f"✗ 前端服务异常: HTTP {response.status_code}", 'WARNING')
        except Exception as e:
            self.log(f"✗ 前端服务不可达: {e}", 'WARNING')
        
        # 输出总结
        success_count = sum(results.values())
        total_count = len(results)
        self.log(f"健康检查完成: {success_count}/{total_count} 服务正常")
        
        return all(results.values())
    
    def start_all(self, background=False):
        """启动所有服务"""
        self.log("=== 智能启动开始 ===")
        
        # 启动后端
        if not self.start_backend():
            self.log("后端启动失败，退出", 'ERROR')
            return False
        
        # 启动前端
        if not self.start_frontend():
            self.log("前端启动失败，但后端已启动", 'WARNING')
        
        # 健康检查
        time.sleep(3)  # 等待服务稳定
        health_ok = self.health_check()
        
        if health_ok:
            self.log("🎉 所有服务启动成功！")
            self.log(f"📱 前端地址: http://localhost:{self.frontend_port}")
            self.log(f"🔧 API文档: http://localhost:{self.backend_port}/docs")
            self.log(f"💚 健康检查: http://localhost:{self.backend_port}/health/live")
        else:
            self.log("⚠️  部分服务异常，请检查日志", 'WARNING')
        
        # 后台模式
        if background:
            self.log("进入后台监控模式...")
            try:
                while True:
                    time.sleep(30)
                    # 定期检查服务状态
                    if self.backend_process and self.backend_process.poll() is not None:
                        self.log("后端进程意外退出", 'ERROR')
                        break
                    if self.frontend_process and self.frontend_process.poll() is not None:
                        self.log("前端进程意外退出", 'WARNING')
            except KeyboardInterrupt:
                self.stop_all()
        
        return health_ok
    
    def stop_all(self):
        """停止所有服务"""
        self.log("正在停止所有服务...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait(timeout=10)
            self.log("后端服务已停止")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait(timeout=10)
            self.log("前端服务已停止")
        
        # 清理端口
        self.cleanup_port(self.backend_port)
        self.cleanup_port(self.frontend_port)
        
        self.log("=== 所有服务已停止 ===")

def main():
    parser = argparse.ArgumentParser(description='智能启动体育彩票扫盘系统')
    parser.add_argument('--backend-only', action='store_true', help='仅启动后端')
    parser.add_argument('--frontend-only', action='store_true', help='仅启动前端')
    parser.add_argument('--background', action='store_true', help='后台运行模式')
    parser.add_argument('--stop', action='store_true', help='停止所有服务')
    
    args = parser.parse_args()
    
    starter = SmartStart()
    
    if args.stop:
        starter.stop_all()
    elif args.backend_only:
        starter.start_backend()
        if not args.background:
            try:
                starter.backend_process.wait()
            except KeyboardInterrupt:
                starter.stop_all()
    elif args.frontend_only:
        starter.start_frontend()
        if not args.background:
            try:
                starter.frontend_process.wait()
            except KeyboardInterrupt:
                starter.stop_all()
    else:
        starter.start_all(background=args.background)

if __name__ == '__main__':
    main()
# AI_DONE: coder1 @2026-01-25T00:00:00