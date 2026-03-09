#!/usr/bin/env python3
"""
爬虫API最小测试服务 - 完全独立版本
不依赖有问题的模块，专门测试爬虫API逻辑
"""

import os
import sys
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 创建FastAPI应用
app = FastAPI(
    title="体育彩票扫盘系统API - 爬虫最小测试",
    description="Sports Lottery Sweeper API - Minimal Crawler Test",
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

print("[START] 启动爬虫最小测试服务...")

# 基础路由
@app.get("/")
async def root():
    return {"message": "体育彩票扫盘系统API - 爬虫最小测试", "version": "1.0.0"}

@app.get("/health/live")
async def health_live():
    return {"status": "healthy", "service": "sport-lottery-sweeper-minimal"}

@app.get("/health/ready")
async def health_ready():
    return {"status": "ready", "database": "not_required", "cache": "not_required"}

# 模拟服务类（不依赖外部模块）
class MockDataSourceService:
    """模拟数据源服务"""
    def __init__(self, db=None):
        self.db = db
        print("[Mock] DataSourceService initialized")
    
    def get_sources(self):
        return [
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

class MockTaskSchedulerService:
    """模拟任务调度服务"""
    def __init__(self, db=None):
        self.db = db
        print("[Mock] TaskSchedulerService initialized")

class MockIntelligenceService:
    """模拟智能分析服务"""
    def __init__(self, db=None):
        self.db = db
        print("[Mock] IntelligenceService initialized")

# 服务注册表（模拟修复后的版本）
_service_cache = {}

def get_data_source_service(db=None):
    """获取数据源服务（单例模式）"""
    global _service_cache
    if 'data_source' not in _service_cache:
        _service_cache['data_source'] = MockDataSourceService(db)
    return _service_cache['data_source']

def get_task_scheduler_service(db=None):
    """获取任务调度服务（单例模式）"""
    global _service_cache
    if 'task_scheduler' not in _service_cache:
        _service_cache['task_scheduler'] = MockTaskSchedulerService(db)
    return _service_cache['task_scheduler']

def get_intelligence_service(db=None):
    """获取智能分析服务（单例模式）"""
    global _service_cache
    if 'intelligence' not in _service_cache:
        _service_cache['intelligence'] = MockIntelligenceService(db)
    return _service_cache['intelligence']

# 测试服务可用性
print("[INFO] 初始化服务...")
try:
    ds_service = get_data_source_service()
    ts_service = get_task_scheduler_service() 
    intel_service = get_intelligence_service()
    print("[SUCCESS] 所有模拟服务初始化成功")
    SERVICES_OK = True
except Exception as e:
    print(f"[ERROR] 服务初始化失败: {e}")
    SERVICES_OK = False

# 爬虫配置管理API
@app.get("/api/admin/v1/crawler-configs")
async def get_crawler_configs():
    print("[API] GET /api/admin/v1/crawler-configs")
    mock_configs = [
        {
            "id": 1,
            "name": "全局默认配置",
            "config_type": "global", 
            "content": {"timeout": 10, "retry": 3, "max_concurrent": 5},
            "version": 1,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 2,
            "name": "足球赔率抓取配置",
            "config_type": "football_sp_odds",
            "content": {"timeout": 15, "retry": 5, "parser": "football_sp_parser"},
            "version": 2,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    return {"code": 200, "message": "success", "data": mock_configs}

# 数据源管理API
@app.get("/api/admin/v1/sources")
async def get_sources():
    print("[API] GET /api/admin/v1/sources")
    if not SERVICES_OK:
        return {"code": 503, "message": "服务暂不可用", "data": []}
    
    try:
        service = get_data_source_service()
        sources = service.get_sources()
        return {"code": 200, "message": "success", "data": sources}
    except Exception as e:
        print(f"[ERROR] 获取数据源失败: {e}")
        return {"code": 500, "message": f"服务错误: {str(e)}", "data": []}

@app.post("/api/admin/v1/sources")
async def create_source():
    print("[API] POST /api/admin/v1/sources")
    if not SERVICES_OK:
        return {"code": 503, "message": "服务暂不可用"}
    
    try:
        # 测试服务调用
        get_data_source_service()
        return {"code": 200, "message": "数据源创建成功", "data": {"id": "999", "name": "新创建的数据源"}}
    except Exception as e:
        return {"code": 500, "message": f"服务错误: {str(e)}"}

@app.put("/api/admin/v1/sources/{source_id}/status")
async def update_source_status(source_id: str):
    print(f"[API] PUT /api/admin/v1/sources/{source_id}/status")
    if not SERVICES_OK:
        return {"code": 503, "message": "服务暂不可用"}
    
    try:
        get_data_source_service()
        return {"code": 200, "message": "状态更新成功", "data": {"id": source_id, "status": "updated"}}
    except Exception as e:
        return {"code": 500, "message": f"服务错误: {str(e)}"}

# 数据情报API
@app.get("/api/admin/v1/intelligence/data")
async def get_intelligence_data():
    print("[API] GET /api/admin/v1/intelligence/data")
    if not SERVICES_OK:
        return {"code": 503, "message": "服务暂不可用", "data": {"items": [], "total": 0}}
    
    try:
        service = get_intelligence_service()
        mock_data = {
            "items": [
                {
                    "id": "int_001",
                    "title": "[快讯] 英超豪门爆发激烈冲突",
                    "content": "据最新消息，英超两支豪门球队在训练中爆发激烈冲突，场面一度失控...",
                    "category": "football_news",
                    "quality_score": 0.92,
                    "is_valid": True,
                    "source_name": "500赛事抓取器",
                    "created_at": "2024-01-15T10:30:00"
                },
                {
                    "id": "int_002", 
                    "title": "[分析] 欧冠半决赛战术预测",
                    "content": "专业分析师预测本轮欧冠半决赛的关键战术要点...",
                    "category": "tactical_analysis",
                    "quality_score": 0.88,
                    "is_valid": True,
                    "source_name": "专业分析平台",
                    "created_at": "2024-01-15T09:15:00"
                }
            ],
            "total": 2,
            "page": 1,
            "size": 20
        }
        return {"code": 200, "message": "success", "data": mock_data}
    except Exception as e:
        print(f"[ERROR] 获取情报数据失败: {e}")
        return {"code": 500, "message": f"服务错误: {str(e)}", "data": {"items": [], "total": 0}}

@app.get("/api/admin/v1/intelligence/stats")
async def get_intelligence_stats():
    print("[API] GET /api/admin/v1/intelligence/stats")
    if not SERVICES_OK:
        return {"code": 503, "message": "服务暂不可用"}
    
    try:
        get_intelligence_service()
        return {"code": 200, "message": "success", "data": {
            "total_count": 1250,
            "valid_count": 1180, 
            "invalid_count": 70,
            "quality_avg": 0.87,
            "categories": {
                "football_news": 450,
                "tactical_analysis": 320,
                "player_transfer": 280,
                "match_prediction": 200
            }
        }}
    except Exception as e:
        return {"code": 500, "message": f"服务错误: {str(e)}"}

@app.get("/api/admin/v1/intelligence/trend")
async def get_trend_analysis():
    print("[API] GET /api/admin/v1/intelligence/trend")
    if not SERVICES_OK:
        return {"code": 503, "message": "服务暂不可用"}
    
    try:
        get_intelligence_service()
        return {"code": 200, "message": "success", "data": {
            "dates": ["2024-01-10", "2024-01-11", "2024-01-12", "2024-01-13", "2024-01-14"],
            "counts": [120, 135, 128, 142, 138],
            "quality_scores": [0.85, 0.87, 0.86, 0.88, 0.89]
        }}
    except Exception as e:
        return {"code": 500, "message": f"服务错误: {str(e)}"}

# 系统管理API
@app.get("/api/admin/v1/system/health")
async def system_health():
    print("[API] GET /api/admin/v1/system/health")
    return {"code": 200, "message": "success", "data": {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "services": {
            "data_source": "available" if SERVICES_OK else "unavailable",
            "task_scheduler": "available" if SERVICES_OK else "unavailable", 
            "intelligence": "available" if SERVICES_OK else "unavailable"
        },
        "api_version": "1.0.0",
        "environment": "test"
    }}

if __name__ == "__main__":
    print("[INFO] 服务地址: http://localhost:8000")
    print("[INFO] API文档: http://localhost:8000/docs")
    print("[INFO] 按 Ctrl+C 停止服务")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)