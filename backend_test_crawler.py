#!/usr/bin/env python3
"""
爬虫API测试服务 - 最小化版本
只测试我们修复的爬虫相关API
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 创建FastAPI应用
app = FastAPI(
    title="体育彩票扫盘系统API - 爬虫测试版",
    description="Sports Lottery Sweeper API - Crawler Test",
    version="1.0.0",
    docs_url="/docs"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基础路由
@app.get("/")
async def root():
    return {"message": "体育彩票扫盘系统API - 爬虫测试版", "version": "1.0.0"}

@app.get("/health/live")
async def health_live():
    return {"status": "healthy", "service": "sport-lottery-sweeper-crawler-test"}

@app.get("/health/ready")
async def health_ready():
    return {"status": "ready", "database": "mock", "cache": "mock"}

# 导入我们修复的爬虫服务
print("[INFO] 正在导入爬虫服务...")
try:
    from backend.services.service_registry import (
        get_data_source_service, get_task_scheduler_service, get_intelligence_service
    )
    print("[INFO] 服务注册表导入成功")
    
    # 测试服务实例化
    print("[INFO] 测试数据源服务...")
    data_source_service = get_data_source_service(None)
    print(f"[INFO] 数据源服务实例: {type(data_source_service)}")
    
    print("[INFO] 测试任务调度服务...")
    task_scheduler_service = get_task_scheduler_service(None)
    print(f"[INFO] 任务调度服务实例: {type(task_scheduler_service)}")
    
    print("[INFO] 测试智能分析服务...")
    intelligence_service = get_intelligence_service(None)
    print(f"[INFO] 智能分析服务实例: {type(intelligence_service)}")
    
    SERVICES_AVAILABLE = True
except Exception as e:
    print(f"[ERROR] 服务导入失败: {e}")
    SERVICES_AVAILABLE = False

# 爬虫配置管理API
@app.get("/api/admin/v1/crawler-configs")
async def get_crawler_configs():
    print("[API] 获取爬虫配置列表")
    mock_configs = [
        {
            "id": 1,
            "name": "全局默认配置",
            "config_type": "global", 
            "content": {"timeout": 10, "retry": 3},
            "version": 1,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    return {"code": 200, "message": "success", "data": mock_configs}

# 数据源管理API
@app.get("/api/admin/v1/sources")
async def get_sources():
    print("[API] 获取数据源列表")
    if not SERVICES_AVAILABLE:
        return {"code": 503, "message": "服务暂不可用", "data": []}
    
    try:
        data_source_service = get_data_source_service(None)
        # 这里可以调用真实的服务方法
        mock_sources = [
            {
                "id": "0001",
                "name": "500赛事抓取器",
                "category": "football_sp_odds",
                "createTime": "2024-01-15 10:30:00",
                "status": "active",
                "url": "https://www.500.com",
                "config": {"timeout": 10, "retry": 3}
            }
        ]
        return {"code": 200, "message": "success", "data": mock_sources}
    except Exception as e:
        print(f"[ERROR] 获取数据源失败: {e}")
        return {"code": 500, "message": f"服务错误: {str(e)}", "data": []}

@app.post("/api/admin/v1/sources")
async def create_source():
    print("[API] 创建数据源")
    if not SERVICES_AVAILABLE:
        return {"code": 503, "message": "服务暂不可用"}
    
    try:
        # 测试服务可用性
        get_data_source_service(None)
        return {"code": 200, "message": "数据源创建成功", "data": {"id": "999"}}
    except Exception as e:
        return {"code": 500, "message": f"服务错误: {str(e)}"}

@app.put("/api/admin/v1/sources/{source_id}/status")
async def update_source_status(source_id: str):
    print(f"[API] 更新数据源状态: {source_id}")
    if not SERVICES_AVAILABLE:
        return {"code": 503, "message": "服务暂不可用"}
    
    try:
        get_data_source_service(None)
        return {"code": 200, "message": "状态更新成功"}
    except Exception as e:
        return {"code": 500, "message": f"服务错误: {str(e)}"}

# 数据情报API
@app.get("/api/admin/v1/intelligence/data")
async def get_intelligence_data():
    print("[API] 获取数据情报列表")
    if not SERVICES_AVAILABLE:
        return {"code": 503, "message": "服务暂不可用", "data": {"items": [], "total": 0}}
    
    try:
        intelligence_service = get_intelligence_service(None)
        mock_intelligence = {
            "items": [
                {
                    "id": "int_001",
                    "title": "[快讯] 英超豪门爆发激烈冲突",
                    "content": "据最新消息，英超两支豪门球队在训练中爆发激烈冲突...",
                    "category": "football_news",
                    "quality_score": 0.92,
                    "is_valid": True,
                    "source_name": "500赛事抓取器",
                    "created_at": "2024-01-15T10:30:00"
                }
            ],
            "total": 1,
            "page": 1,
            "size": 20
        }
        return {"code": 200, "message": "success", "data": mock_intelligence}
    except Exception as e:
        print(f"[ERROR] 获取情报数据失败: {e}")
        return {"code": 500, "message": f"服务错误: {str(e)}", "data": {"items": [], "total": 0}}

@app.get("/api/admin/v1/intelligence/stats")
async def get_intelligence_stats():
    print("[API] 获取数据情报统计")
    if not SERVICES_AVAILABLE:
        return {"code": 503, "message": "服务暂不可用"}
    
    try:
        intelligence_service = get_intelligence_service(None)
        return {"code": 200, "message": "success", "data": {
            "total_count": 1250, "valid_count": 1180, "invalid_count": 70, "quality_avg": 0.87
        }}
    except Exception as e:
        return {"code": 500, "message": f"服务错误: {str(e)}"}

@app.get("/api/admin/v1/intelligence/trend")
async def get_trend_analysis():
    print("[API] 获取趋势分析")
    if not SERVICES_AVAILABLE:
        return {"code": 503, "message": "服务暂不可用"}
    
    try:
        intelligence_service = get_intelligence_service(None)
        return {"code": 200, "message": "success", "data": {
            "dates": ["2024-01-10", "2024-01-11", "2024-01-12"],
            "counts": [120, 135, 128]
        }}
    except Exception as e:
        return {"code": 500, "message": f"服务错误: {str(e)}"}

# 系统管理API
@app.get("/api/admin/v1/system/health")
async def system_health():
    print("[API] 系统健康检查")
    return {"code": 200, "message": "success", "data": {
        "status": "healthy", "timestamp": datetime.now().isoformat(),
        "services": {
            "data_source": "available" if SERVICES_AVAILABLE else "unavailable",
            "task_scheduler": "available" if SERVICES_AVAILABLE else "unavailable", 
            "intelligence": "available" if SERVICES_AVAILABLE else "unavailable"
        }
    }}

if __name__ == "__main__":
    print("[START] 启动爬虫API测试服务...")
    print("[INFO] 服务地址: http://localhost:8000")
    print("[INFO] API文档: http://localhost:8000/docs")
    print("[INFO] 按 Ctrl+C 停止服务")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)