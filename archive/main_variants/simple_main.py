#!/usr/bin/env python3
"""
简化版后端服务 - 专注爬虫API验证
避免编码问题，快速启动服务
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime

app = FastAPI(
    title="体育彩票扫盘系统API",
    description="Sports Lottery Sweeper API - 爬虫管理",
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

# 模拟数据
MOCK_SOURCES = [
    {
        "id": "0001",
        "name": "500赛事抓取器",
        "category": "football_sp_odds",
        "createTime": "2024-01-15 10:30:00",
        "status": "active",
        "url": "https://www.500.com",
        "config": {"timeout": 10, "retry": 3}
    },
    {
        "id": "0002", 
        "name": "球探网数据抓取",
        "category": "team_info",
        "createTime": "2024-01-16 09:15:00",
        "status": "active",
        "url": "https://www.titan007.com",
        "config": {"timeout": 15, "retry": 2}
    }
]

MOCK_INTELLIGENCE = {
    "items": [
        {
            "id": "int_001",
            "title": "[快讯] 英超豪门爆发激烈冲突",
            "content": "据最新消息，英超两支豪门球队在训练中爆发激烈冲突，多名球员卷入其中...",
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

# 基础路由
@app.get("/")
async def root():
    return {"message": "体育彩票扫盘系统API", "version": "1.0.0"}

@app.get("/health/live")
async def health_live():
    return {"status": "healthy", "service": "sport-lottery-sweeper"}

@app.get("/health/ready")
async def health_ready():
    return {"status": "ready", "database": "connected", "cache": "connected"}

# 爬虫配置管理API
@app.get("/api/admin/v1/crawler-configs")
async def get_crawler_configs():
    print("📋 获取爬虫配置列表")
    mock_configs = [
        {
            "id": 1,
            "name": "全局默认配置",
            "config_type": "global", 
            "content": {"timeout": 10, "retry": 3, "headers": {"User-Agent": "default-agent"}},
            "version": 1,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    return JSONResponse({
        "code": 200,
        "message": "success",
        "data": mock_configs
    })

@app.post("/api/admin/v1/crawler-configs")
async def create_crawler_config():
    print("➕ 创建爬虫配置")
    return JSONResponse({
        "code": 200,
        "message": "配置创建成功",
        "data": {"id": 999}
    })

# 数据源管理API (前端实际使用)
@app.get("/api/admin/v1/sources")
async def get_sources():
    print("📋 获取数据源列表")
    return JSONResponse({
        "code": 200,
        "message": "success", 
        "data": MOCK_SOURCES
    })

@app.post("/api/admin/v1/sources")
async def create_source():
    print("➕ 创建数据源")
    return JSONResponse({
        "code": 200,
        "message": "数据源创建成功",
        "data": {"id": "999", "name": "新数据源"}
    })

@app.put("/api/admin/v1/sources/{source_id}/status")
async def update_source_status(source_id: str):
    print(f"🔄 更新数据源状态: {source_id}")
    return JSONResponse({
        "code": 200,
        "message": "状态更新成功"
    })

# 数据情报API (前端实际使用) 
@app.get("/api/admin/v1/intelligence/data")
async def get_intelligence_data():
    print("📊 获取数据情报列表")
    return JSONResponse({
        "code": 200,
        "message": "success",
        "data": MOCK_INTELLIGENCE
    })

@app.get("/api/admin/v1/intelligence/stats")
async def get_intelligence_stats():
    print("📈 获取数据情报统计")
    return JSONResponse({
        "code": 200,
        "message": "success",
        "data": {
            "total_count": 1250,
            "valid_count": 1180,
            "invalid_count": 70,
            "quality_avg": 0.87
        }
    })

@app.get("/api/admin/v1/intelligence/trend")
async def get_trend_analysis():
    print("📉 获取趋势分析")
    return JSONResponse({
        "code": 200,
        "message": "success",
        "data": {
            "dates": ["2024-01-10", "2024-01-11", "2024-01-12", "2024-01-13", "2024-01-14"],
            "counts": [120, 135, 128, 142, 138]
        }
    })

# 系统管理API
@app.get("/api/admin/v1/system/health")
async def system_health():
    print("🏥 系统健康检查")
    return JSONResponse({
        "code": 200,
        "message": "success",
        "data": {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "connected",
                "cache": "connected", 
                "crawler": "running"
            }
        }
    })

@app.get("/api/admin/v1/users")
async def get_users():
    return JSONResponse({
        "code": 200,
        "message": "success",
        "data": [{"id": 1, "username": "admin", "email": "admin@example.com"}]
    })

if __name__ == "__main__":
    print("[START] 启动简化版后端服务...")
    print("[INFO] 服务地址: http://localhost:8000")
    print("[INFO] API文档: http://localhost:8000/docs")
    print("[INFO] 按 Ctrl+C 停止服务")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
