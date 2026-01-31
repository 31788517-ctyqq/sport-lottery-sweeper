"""
API v1 路由入口
"""
import logging
from fastapi import APIRouter
from typing import Dict, Any

logger = logging.getLogger(__name__)

# 创建API路由器
router = APIRouter(prefix="/v1", tags=["v1"])

# 动态导入并注册子路由
def register_routes():
    """
    动态注册所有API路由
    """
    routes_to_register = [
        ("admin", "admin"),
        ("crawler", "crawler"),
        ("lottery", "lottery"),
        ("hedging", "hedging"),
        ("simple_hedging", "simple_hedging"),
        ("intelligence", "intelligence"),
        ("predictions", "predictions"),
        ("llm", "llm"),  # 添加LLM路由
        ("real_time_decision", "real_time"),  # 新增实时决策路由
    ]
    
    for module_name, route_prefix in routes_to_register:
        try:
            # 根据模块名动态导入路由
            module = __import__(f"backend.api.v1.{module_name}", fromlist=["router"])
            module_router = getattr(module, "router", None)
            
            if module_router:
                # 注册路由
                router.include_router(
                    module_router, 
                    prefix=f"/{route_prefix}", 
                    tags=[route_prefix]
                )
                logger.info(f"API v1 - {module_name} 路由已注册")
            else:
                logger.warning(f"API v1 - {module_name} 模块中未找到router")
                
        except ImportError as e:
            logger.error(f"API v1 - {module_name} 路由注册失败: {e}")
        except Exception as e:
            logger.error(f"API v1 - {module_name} 路由注册异常: {e}")

# 执行路由注册
register_routes()

# API健康检查端点
@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    API健康检查端点
    """
    return {
        "status": "healthy",
        "api_version": "v1",
        "endpoints": "dynamic",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

# API信息端点
@router.get("/info")
async def api_info() -> Dict[str, Any]:
    """
    API信息端点
    """
    return {
        "title": "体育彩票扫盘系统 API v1",
        "version": "1.0.0",
        "description": "提供体育彩票数据分析、预测和对冲策略服务",
        "features": [
            "数据爬取和处理",
            "比赛结果预测",
            "对冲策略分析",
            "情报分析",
            "LLM集成服务"
        ],
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }