import subprocess
import sys
from pathlib import Path

def start_backend():
    """启动后端服务"""
    print("启动后端服务...")
    
    # 动态定位backend目录
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
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