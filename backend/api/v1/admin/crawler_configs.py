"""
FastAPI版本的配置管理路由
替代原有的Flask路由实现
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/crawler/config", tags=["crawler-configs"])

# 数据模型定义
class CrawlerConfig(BaseModel):
    id: int
    name: str
    config_type: str
    content: Dict[str, Any]
    version: int
    created_at: str
    updated_at: str

class CreateConfigRequest(BaseModel):
    name: str
    config_type: str
    content: Dict[str, Any]

# API端点实现
@router.get("", response_model=List[CrawlerConfig])
async def get_configs():
    """获取配置列表"""
    # Mock 数据
    mock_data = [
        {
            'id': 1,
            'name': '全局默认配置',
            'config_type': 'global',
            'content': {'timeout': 10, 'retry': 3, 'headers': {'User-Agent': 'default-agent'}},
            'version': 1,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        },
        {
            'id': 2,
            'name': '单源-新浪体育',
            'config_type': 'single',
            'content': {'frequency': '5m', 'depth': 2, 'parse_rules': {'title': 'h1'}},
            'version': 2,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
    ]
    return mock_data

@router.post("", response_model=dict)
async def create_config(request: CreateConfigRequest):
    """创建配置"""
    # Mock 返回
    return {'message': 'created', 'id': 999}

@router.put("/{config_id}", response_model=dict)
async def update_config(config_id: int):
    """更新配置"""
    return {'message': 'updated'}

@router.delete("/{config_id}", response_model=dict)
async def delete_config(config_id: int):
    """删除配置"""
    return {'message': 'deleted'}