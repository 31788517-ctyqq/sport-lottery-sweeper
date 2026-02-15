"""
API V1 璺敱鍏ュ彛
"""
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

# 鍒涘缓涓昏矾鐢卞櫒
router = APIRouter()

# 瀵煎叆鎵€鏈堿PI璺敱
try:
    from . import lottery
    logger.info("lottery module imported successfully")
except Exception as e:
    logger.error(f"lottery module import failed: {e}")

try:
    from . import matches
    logger.info("matches module imported successfully")
    # 鍙湁褰撴ā鍧楀鍏ユ垚鍔熸椂鎵嶆敞鍐岃矾鐢?
    router.include_router(matches.router, prefix="/matches", tags=["matches"])
except Exception as e:
    logger.error(f"matches module import failed: {e}")

try:
    from . import public_matches
    logger.info("public_matches module imported successfully")
    # 鍙湁褰撴ā鍧楀鍏ユ垚鍔熸椂鎵嶆敞鍐岃矾鐢?
    router.include_router(public_matches.router, prefix="/public-matches", tags=["public-matches"])
except Exception as e:
    logger.error(f"public_matches module import failed: {e}")

try:
    from . import admin
    logger.info("admin module imported successfully")
    # 只有当前模块导入成功时才注册路由
    router.include_router(admin.router, prefix="/admin")
except Exception as e:
    logger.error(f"admin module import failed: {e}")

try:
    from . import auth  # 璁よ瘉API
    logger.info("SUCCESS auth 妯″潡瀵煎叆鎴愬姛")
    logger.info(f"  auth.router 瀵硅薄: {auth.router}")
    logger.info(f"  auth.router 璺敱鏁? {len(auth.router.routes)}")
    # 灏嗚璇佽矾鐢辨敞鍐屽埌涓昏矾鐢变腑
    router.include_router(auth.router)
except Exception as e:
    logger.error(f"FAILED auth 妯″潡瀵煎叆澶辫触: {e}")
    import traceback
    traceback.print_exc()

try:
    from . import intelligence
    logger.info("SUCCESS intelligence 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED intelligence 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import data_submission
    logger.info("SUCCESS data_submission 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED data_submission 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import caipiao_data
    logger.info("SUCCESS caipiao_data 妯″潡瀵煎叆鎴愬姛")
    logger.info(f"  caipiao_data.router 瀵硅薄: {caipiao_data.router}")
    logger.info(f"  caipiao_data.router 璺敱鏁? {len(caipiao_data.router.routes)}")
except Exception as e:
    logger.error(f"FAILED caipiao_data 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import draw_prediction
    logger.info("SUCCESS draw_prediction 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED draw_prediction 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import hedging
    logger.info("SUCCESS hedging 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED hedging 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import crawler
    logger.info("SUCCESS crawler 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED crawler 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import crawler_alert
    logger.info("SUCCESS crawler_alert 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED crawler_alert 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import crawler_monitor
    logger.info("SUCCESS crawler_monitor 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED crawler_monitor 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import crawler_tasks_adapter
    logger.info("SUCCESS crawler_tasks_adapter 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED crawler_tasks_adapter 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import data_center_adapter
    logger.info("SUCCESS data_center_adapter 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED data_center_adapter 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import headers_adapter
    logger.info("SUCCESS headers_adapter 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED headers_adapter 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import ip_pool_adapter
    logger.info("SUCCESS ip_pool_adapter 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED ip_pool_adapter 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import llm
    logger.info("SUCCESS llm 妯″潡瀵煎叆鎴愬姛")
    logger.info(f"  llm.router 瀵硅薄: {llm.router}")
    logger.info(f"  llm.router 璺敱鏁? {len(llm.router.routes)}")
    # 灏哃LM璺敱娉ㄥ唽鍒颁富璺敱涓?
    router.include_router(llm.router)
except Exception as e:
    logger.error(f"FAILED llm 妯″潡瀵煎叆澶辫触: {e}")
    import traceback
    traceback.print_exc()

# 娣诲姞LLM渚涘簲鍟嗙鐞咥PI妯″潡
try:
    from . import llm_providers
    logger.info("SUCCESS llm_providers 妯″潡瀵煎叆鎴愬姛")
    logger.info(f"  llm_providers.router 瀵硅薄: {llm_providers.router}")
    logger.info(f"  llm_providers.router 璺敱鏁? {len(llm_providers.router.routes)}")
    # 灏哃LM渚涘簲鍟嗚矾鐢辨敞鍐屽埌涓昏矾鐢变腑
    router.include_router(llm_providers.router)
except Exception as e:
    logger.error(f"FAILED llm_providers 妯″潡瀵煎叆澶辫触: {e}")
    import traceback
    traceback.print_exc()

try:
    from . import log_analysis
    logger.info("SUCCESS log_analysis 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED log_analysis 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import lottery_schedule
    logger.info("SUCCESS lottery_schedule 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED lottery_schedule 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import lottery_simple
    logger.info("SUCCESS lottery_simple 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED lottery_simple 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import lottery_test
    logger.info("SUCCESS lottery_test 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED lottery_test 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import lottery_direct
    logger.info("SUCCESS lottery_direct 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED lottery_direct 妯″潡瀵煎叆澶辫触: {e}")

try:
    from . import lottery_final
    logger.info("SUCCESS lottery_final 妯″潡瀵煎叆鎴愬姛")
except Exception as e:
    logger.error(f"FAILED lottery_final 妯″潡瀵煎叆澶辫触: {e}")

# 娣诲姞100qiu鏁版嵁婧怉PI妯″潡
try:
    from . import data_source_100qiu
    logger.info("SUCCESS data_source_100qiu 妯″潡瀵煎叆鎴愬姛")
    logger.info(f"  data_source_100qiu.router 瀵硅薄: {data_source_100qiu.router}")
    logger.info(f"  data_source_100qiu.router 璺敱鏁? {len(data_source_100qiu.router.routes)}")
    # 灏?00qiu鏁版嵁婧愯矾鐢辨敞鍐屽埌涓昏矾鐢变腑锛岀洿鎺ヤ娇鐢ㄦā鍧楀畾涔夌殑璺敱锛屼笉娣诲姞棰濆鍓嶇紑
    router.include_router(data_source_100qiu.router)
except Exception as e:
    logger.error(f"FAILED data_source_100qiu 妯″潡瀵煎叆澶辫触: {e}")
    import traceback
    traceback.print_exc()

# 娉ㄥ唽缁熶竴Matches API
logger.info("=== 娉ㄥ唽缁熶竴Matches API ===")
try:
    from . import unified_matches
    logger.info("SUCCESS unified_matches 妯″潡瀵煎叆鎴愬姛")
    logger.info(f"  unified_matches.router 瀵硅薄: {unified_matches.router}")
    logger.info(f"  unified_matches.router 璺敱鏁? {len(unified_matches.router.routes)}")
    # 娉ㄥ唽缁熶竴Matches API璺敱
    router.include_router(unified_matches.router)
    logger.info("SUCCESS unified_matches 璺敱娉ㄥ唽鎴愬姛")
except Exception as e:
    logger.error(f"FAILED unified_matches 妯″潡瀵煎叆澶辫触: {e}")
    import traceback
    traceback.print_exc()

# 娉ㄦ剰锛氬寳鍗曡繃婊PI宸插湪main.py涓崟鐙敞鍐岋紝閬垮厤寰幆瀵煎叆
# 娣诲姞鍖楀崟杩囨护API妯″潡
# 宸叉敞閲婏細宸插湪main.py涓洿鎺ユ敞鍐岋紝閬垮厤閲嶅娉ㄥ唽
# try:
#     from backend.app.api_v1.endpoints.beidan_filter_api import router as beidan_filter_router
#     router.include_router(beidan_filter_router, prefix="/beidan-filter", tags=["beidan-filter"])
#     logger.info("SUCCESS beidan_filter_api 妯″潡瀵煎叆骞舵敞鍐屾垚鍔?)
# except Exception as e:
#     logger.error(f"FAILED beidan_filter_api 妯″潡瀵煎叆澶辫触: {e}")
#     import traceback
#     traceback.print_exc()

# 璁板綍鎬昏矾鐢辨暟
logger.info(f"API V1 涓昏矾鐢卞櫒鍒濆鍖栧畬鎴愶紝璺敱鏁? {len(router.routes)}")

# 瀵煎嚭璺敱
__all__ = ["router"]

# API鍋ュ悍妫€鏌ョ鐐?
@router.get("/health")
async def health_check() -> dict:
    """
    API鍋ュ悍妫€鏌ョ鐐?
    """
    return {
        "status": "healthy",
        "api_version": "v1",
        "endpoints": "dynamic",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

# API淇℃伅绔偣
@router.get("/info")
async def api_info() -> dict:
    """
    API information endpoint
    """
    return {
        "title": "体育彩票扫盘系统 API v1",
        "version": "1.0.0", 
        "description": "提供体育彩票数据分析、预测和智能分析服务",
        "features": [
            "数据采集和分析",
            "比赛结果预测", 
            "智能分析引擎",
            "实时监控分析",
            "LLM智能服务"
        ],
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

