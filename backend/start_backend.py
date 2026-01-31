import subprocess
import logging
logger = logging.getLogger(__name__)
import sys
import os

def start_backend():
    """启动后端服务"""
    logger.debug("启动后端服务...")
    
    # 切换到backend目录（使用当前脚本所在目录）
    backend_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_path)
    
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
        logger.debug(f"启动后端服务失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.debug("\n后端服务已停止")
        sys.exit(0)

if __name__ == "__main__":
    start_backend()