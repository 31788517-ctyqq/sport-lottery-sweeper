"""
API V1 路由入口
"""
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

# 创建主路由器
router = APIRouter()

# 导入所有API路由
try:
    from . import lottery
    logger.info("[OK] lottery 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] lottery 模块导入失败: {e}")

try:
    from . import matches
    logger.info("[OK] matches 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] matches 模块导入失败: {e}")

try:
    from . import public_matches
    logger.info("[OK] public_matches 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] public_matches 模块导入失败: {e}")

try:
    from . import admin
    logger.info("[OK] admin 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] admin 模块导入失败: {e}")

try:
    from . import auth  # 认证API
    logger.info("[OK] auth 模块导入成功")
    logger.info(f"  auth.router 对象: {auth.router}")
    logger.info(f"  auth.router 路由数: {len(auth.router.routes)}")
    # 将认证路由注册到主路由中
    router.include_router(auth.router)
except Exception as e:
    logger.error(f"[FAIL] auth 模块导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from . import intelligence
    logger.info("[OK] intelligence 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] intelligence 模块导入失败: {e}")

try:
    from . import data_submission
    logger.info("[OK] data_submission 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] data_submission 模块导入失败: {e}")

try:
    from . import caipiao_data
    logger.info("[OK] caipiao_data 模块导入成功")
    logger.info(f"  caipiao_data.router 对象: {caipiao_data.router}")
    logger.info(f"  caipiao_data.router 路由数: {len(caipiao_data.router.routes)}")
except Exception as e:
    logger.error(f"[FAIL] caipiao_data 模块导入失败: {e}")

try:
    from . import draw_prediction
    logger.info("[OK] draw_prediction 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] draw_prediction 模块导入失败: {e}")

try:
    from . import hedging
    logger.info("[OK] hedging 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] hedging 模块导入失败: {e}")

try:
    from . import crawler
    logger.info("[OK] crawler 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] crawler 模块导入失败: {e}")

try:
    from . import crawler_alert
    logger.info("[OK] crawler_alert 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] crawler_alert 模块导入失败: {e}")

try:
    from . import crawler_monitor
    logger.info("[OK] crawler_monitor 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] crawler_monitor 模块导入失败: {e}")

try:
    from . import crawler_tasks_adapter
    logger.info("[OK] crawler_tasks_adapter 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] crawler_tasks_adapter 模块导入失败: {e}")

try:
    from . import data_center_adapter
    logger.info("[OK] data_center_adapter 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] data_center_adapter 模块导入失败: {e}")

try:
    from . import headers_adapter
    logger.info("[OK] headers_adapter 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] headers_adapter 模块导入失败: {e}")

try:
    from . import ip_pool_adapter
    logger.info("[OK] ip_pool_adapter 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] ip_pool_adapter 模块导入失败: {e}")

try:
    from . import llm
    logger.info("[OK] llm 模块导入成功")
    logger.info(f"  llm.router 对象: {llm.router}")
    logger.info(f"  llm.router 路由数: {len(llm.router.routes)}")
    # 将LLM路由注册到主路由中
    router.include_router(llm.router)
except Exception as e:
    logger.error(f"[FAIL] llm 模块导入失败: {e}")
    import traceback
    traceback.print_exc()

# 添加LLM供应商管理API模块
try:
    from . import llm_providers
    logger.info("[OK] llm_providers 模块导入成功")
    logger.info(f"  llm_providers.router 对象: {llm_providers.router}")
    logger.info(f"  llm_providers.router 路由数: {len(llm_providers.router.routes)}")
    # 将LLM供应商路由注册到主路由中
    router.include_router(llm_providers.router)
except Exception as e:
    logger.error(f"[FAIL] llm_providers 模块导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from . import log_analysis
    logger.info("[OK] log_analysis 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] log_analysis 模块导入失败: {e}")

try:
    from . import lottery_schedule
    logger.info("[OK] lottery_schedule 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] lottery_schedule 模块导入失败: {e}")

try:
    from . import lottery_simple
    logger.info("[OK] lottery_simple 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] lottery_simple 模块导入失败: {e}")

try:
    from . import lottery_test
    logger.info("[OK] lottery_test 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] lottery_test 模块导入失败: {e}")

try:
    from . import lottery_direct
    logger.info("[OK] lottery_direct 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] lottery_direct 模块导入失败: {e}")

try:
    from . import lottery_final
    logger.info("[OK] lottery_final 模块导入成功")
except Exception as e:
    logger.error(f"[FAIL] lottery_final 模块导入失败: {e}")

# 添加100qiu数据源API模块
try:
    from . import data_source_100qiu
    logger.info("[OK] data_source_100qiu 模块导入成功")
    logger.info(f"  data_source_100qiu.router 对象: {data_source_100qiu.router}")
    logger.info(f"  data_source_100qiu.router 路由数: {len(data_source_100qiu.router.routes)}")
    # 将100qiu数据源路由注册到主路由中，直接使用模块定义的路由，不添加额外前缀
    router.include_router(data_source_100qiu.router)
except Exception as e:
    logger.error(f"[FAIL] data_source_100qiu 模块导入失败: {e}")
    import traceback
    traceback.print_exc()

# 注意：北单过滤API已在main.py中单独注册，避免循环导入
# 添加北单过滤API模块
try:
    from backend.app.api_v1.endpoints.beidan_filter_api import router as beidan_filter_router
    router.include_router(beidan_filter_router, prefix="/beidan-filter", tags=["beidan-filter"])
    logger.info("[OK] beidan_filter_api 模块导入并注册成功")
except Exception as e:
    logger.error(f"[FAIL] beidan_filter_api 模块导入失败: {e}")
    import traceback
    traceback.print_exc()

# 记录总路由数
logger.info(f"API V1 主路由器初始化完成，路由数: {len(router.routes)}")

# 导出路由
__all__ = ["router"]

# API健康检查端点
@router.get("/health")
async def health_check() -> dict:
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
async def api_info() -> dict:
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
