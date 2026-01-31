"""
平局预测模块 - 最简化API控制器层
"""
from fastapi import APIRouter

# 创建一个最简单的路由，避免复杂的导入
router = APIRouter()

@router.get("/draw-prediction/health")
async def health_check():
    """健康检查端点"""
    return {"status": "Draw Prediction API is running"}

# 一个简单的测试端点
@router.get("/draw-prediction/test")
async def test_endpoint():
    """测试端点"""
    return {"message": "Draw Prediction API loaded successfully"}