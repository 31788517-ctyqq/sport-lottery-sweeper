"""
Predictions API 路由 - 重定向到 draw_prediction
"""
from fastapi import APIRouter
from .draw_prediction import router as draw_prediction_router

router = APIRouter(prefix="/predictions", tags=["predictions"])

# 将 draw_prediction 的路由包含进来
router.include_router(draw_prediction_router)