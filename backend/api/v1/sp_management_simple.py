"""
足球SP管理模块 - 最简化API控制器层
"""
from fastapi import APIRouter
from typing import List

# 创建一个最简单的路由，避免复杂的导入
router = APIRouter()

@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "SP Management API is running"}

# 一个简单的测试端点
@router.get("/test")
async def test_endpoint():
    """测试端点"""
    return {"message": "SP Management API loaded successfully"}