"""
FastAPI版本的数据源管理路由
替代原有的Flask路由实现
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from backend.models.data_sources import DataSource as DBDataSource
from sqlalchemy.orm import Session
from backend.database import get_db

router = APIRouter(prefix="/crawler/sources", tags=["crawler-sources"])

# 数据模型定义
class DataSourceBase(BaseModel):
    id: int
    name: str
    url: str
    status: str
    last_crawl_time: Optional[str] = None
    success_rate: float
    response_time: float
    created_at: str
    updated_at: str

class DataSourceHealth(BaseModel):
    status: str
    response_time_ms: Optional[float] = None
    status_code: Optional[int] = None

class UpdateStatusRequest(BaseModel):
    status: str

# API端点实现
@router.get("", response_model=List[DataSourceBase])
async def list_sources():
    """获取数据源列表"""
    # 模拟数据，实际应用中应从数据库获取
    mock_data = [
        {
            'id': 1,
            'name': '新浪体育',
            'url': 'https://sports.sina.com.cn/',
            'status': 'online',
            'last_crawl_time': datetime.utcnow().isoformat(),
            'success_rate': 98.5,
            'response_time': 120.3,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        },
        {
            'id': 2,
            'name': '腾讯体育',
            'url': 'https://sports.qq.com/',
            'status': 'offline',
            'last_crawl_time': None,
            'success_rate': 0.0,
            'response_time': 0.0,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
    ]
    return mock_data

@router.get("/{source_id}/health", response_model=DataSourceHealth)
async def health_check(source_id: int):
    """健康检查"""
    # 简单判断 id
    if source_id == 1:
        return {'status': 'online', 'response_time_ms': 115, 'status_code': 200}
    else:
        return {'status': 'offline', 'response_time_ms': None, 'status_code': None}

@router.put("/{source_id}/status")
async def update_status(source_id: int, request: UpdateStatusRequest):
    """更新数据源状态"""
    # 模拟返回
    return {
        'message': 'status updated', 
        'id': source_id, 
        'new_status': request.status
    }