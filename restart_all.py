"""
一键重启前后端服务脚本
该脚本将停止当前运行的前后端服务并重新启动
"""
import subprocess
import sys
import os
import psutil
import threading
import time

def kill_process_by_name(process_name):
    """根据进程名杀死进程"""
    killed_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # 检查进程名是否匹配
            if process_name.lower() in proc.info['name'].lower():
                # 更精确地检查命令行参数
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if 'uvicorn' in cmdline or 'backend.main' in cmdline:
                    pid = proc.info['pid']
                    print(f"正在停止后端进程 PID: {pid}")
                    proc.kill()
                    killed_processes.append(pid)
                elif 'vite' in cmdline or 'npm' in cmdline or 'node' in cmdline:
                    # 检查是否是前端开发服务器
                    if 'dev' in cmdline or 'frontend' in cmdline or 'vite' in cmdline:
                        pid = proc.info['pid']
                        print(f"正在停止前端进程 PID: {pid}")
                        proc.kill()
                        killed_processes.append(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return len(killed_processes)

def restart_backend():
    """重启后端服务"""
    print("正在启动后端服务...")
    try:
        # 切换到项目根目录
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        # 启动后端服务
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "localhost", 
            "--port", "8001"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"后端服务已启动，PID: {process.pid}")
        print("后端服务地址: http://localhost:8001")
        print("API文档地址: http://localhost:8001/docs")
        
        # 实时打印后端输出
        def print_backend_output():
            for line in iter(process.stdout.readline, b''):
                try:
                    decoded_line = line.decode('utf-8')
                    print(decoded_line, end='')
                except UnicodeDecodeError:
                    # 尝试使用其他编码
                    try:
                        decoded_line = line.decode('gbk')
                        print(decoded_line, end='')
                    except UnicodeDecodeError:
                        # 如果还是失败，则跳过这一行
                        print('[无法解码的输出]', end='')
        
        t = threading.Thread(target=print_backend_output)
        t.daemon = True
        t.start()
        
        return process
    except Exception as e:
        print(f"启动后端服务失败: {e}")
        return None

def restart_frontend():
    """重启前端服务"""
    print("正在启动前端服务...")
    try:
        # 切换到前端目录
        project_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_dir = os.path.join(project_dir, "frontend")
        os.chdir(frontend_dir)
        
        # 启动前端服务
        process = subprocess.Popen([
            "npm", "run", "dev"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"前端服务已启动，PID: {process.pid}")
        print("前端服务将在可用端口上运行（通常是 http://localhost:3000）")
        
        # 实时打印前端输出
        def print_frontend_output():
            for line in iter(process.stdout.readline, b''):
                try:
                    decoded_line = line.decode('utf-8')
                    print(decoded_line, end='')
                except UnicodeDecodeError:
                    # 尝试使用其他编码
                    try:
                        decoded_line = line.decode('gbk')
                        print(decoded_line, end='')
                    except UnicodeDecodeError:
                        # 如果还是失败，则跳过这一行
                        print('[无法解码的输出]', end='')
        
        t = threading.Thread(target=print_frontend_output)
        t.daemon = True
        t.start()
        
        return process
    except FileNotFoundError:
        print("错误: 未找到npm命令，请确保已安装Node.js")
        return None
    except Exception as e:
        print(f"启动前端服务失败: {e}")
        return None

def restart_all():
    """重启所有服务"""
    print("="*50)
    print("正在重启前后端服务...")
    print("="*50)
    
    # 杀死现有的前后端进程
    backend_killed = kill_process_by_name('python')
    frontend_killed = kill_process_by_name('node')
    
    total_killed = backend_killed + frontend_killed
    if total_killed > 0:
        print(f"已停止 {total_killed} 个相关进程（后端: {backend_killed}, 前端: {frontend_killed}）")
    else:
        print("未找到正在运行的相关进程")
    
    # 等待一段时间确保进程完全停止
    time.sleep(2)
    
    print("-"*50)
    
    # 启动后端服务
    backend_process = restart_backend()
    if not backend_process:
        print("警告: 后端服务启动失败")
        return
    
    # 等待后端服务启动
    time.sleep(3)
    
    # 启动前端服务
    frontend_process = restart_frontend()
    if not frontend_process:
        print("警告: 前端服务启动失败")
        return
    
    print("-"*50)
    print("所有服务已成功重启!")
    print("前端服务地址: http://localhost:3000 (或相近端口号)")
    print("后端服务地址: http://localhost:8001")
    print("管理后台登录凭据:")
    print("  用户名: admin")
    print("  密码: admin123")
    print("="*50)
    print("服务正在运行中... 按 Ctrl+C 停止服务")

if __name__ == "__main__":
    try:
        restart_all()
        
        # 保持脚本运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n收到中断信号，退出...")
        sys.exit(0)