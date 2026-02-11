import uvicorn
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # 从backend.main导入app
    from backend.main import app
    
    # 运行在8002端口以避免冲突
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=False)