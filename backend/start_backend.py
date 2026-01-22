import subprocess
import sys
import os

def start_backend():
    """启动后端服务"""
    print("启动后端服务...")
    
    # 更改到backend目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 启动FastAPI服务
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8001",  # 修改为8001端口，因为8000被占用
        "--reload"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"启动后端服务失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n后端服务已停止")
        sys.exit(0)

if __name__ == "__main__":
    start_backend()