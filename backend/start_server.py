#!/usr/bin/env python3
"""
后端服务启动脚本 - 固定端口8000
"""
import uvicorn
import os
import sys
from pathlib import Path

def main():
    # 固定端口为8000
    port = 8000
    host = "0.0.0.0"
    
    print(f"🚀 启动后端服务...")
    print(f"📍 地址: http://{host}:{port}")
    print(f"📖 API文档: http://{host}:{port}/docs")
    print(f"❤️  健康检查: http://{host}:{port}/health/live")
    print("-" * 50)
    
    # 启动uvicorn服务器，固定端口8000
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()