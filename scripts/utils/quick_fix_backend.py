"""
快速修复后端服务
"""
import subprocess
import time
import sys
import os

def start_backend():
    """启动后端服务"""
    print("正在启动后端服务...")
    
    # 切换到backend目录
    os.chdir('backend')
    
    # 启动服务
    proc = subprocess.Popen(
        [sys.executable, 'main.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(5)
    
    # 检查服务是否启动成功
    import urllib.request
    try:
        response = urllib.request.urlopen('http://localhost:8000/health', timeout=5)
        if response.getcode() == 200:
            print("✓ 后端服务启动成功!")
            return proc
        else:
            print("✗ 后端服务响应异常")
            return None
    except Exception as e:
        print(f"✗ 后端服务启动失败: {e}")
        # 输出日志
        try:
            output, _ = proc.communicate(timeout=1)
            print("服务日志:", output[-500:])
        except:
            pass
        return None

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    proc = start_backend()
    if proc:
        print("后端服务运行中... PID:", proc.pid)
        # 保持运行
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("正在停止服务...")
            proc.terminate()
    else:
        print("启动失败，请检查日志")
