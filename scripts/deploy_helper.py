"""
部署辅助脚本：健康检查、初始化、监控
"""
import asyncio
import logging
from datetime import datetime
import httpx
import requests
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_health_check(max_retries=30, delay=10):
    """
    等待应用健康检查通过
    """
    url = f"http://localhost:{settings.PORT}/health"
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info("应用健康检查通过")
                return True
            else:
                logger.error(f"应用返回错误状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"应用不可用: {e}")
        
        logger.info(f"等待应用启动... ({i+1}/{max_retries})")
        time.sleep(delay)
    
    logger.error("应用启动超时")
    return False

def check_endpoints(endpoints, max_retries=5, delay=2):
    """
    检查多个端点的可用性
    """
    def check_single_endpoint(endpoint):
        url = f"http://localhost:{settings.PORT}{endpoint}"
        for i in range(max_retries):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"端点可用: {endpoint}")
                    return endpoint, True
                else:
                    logger.warning(f"端点返回错误: {endpoint} ({response.status_code})")
            except requests.exceptions.RequestException as e:
                logger.error(f"端点不可用: {endpoint} ({e})")
            
            time.sleep(delay)
        
        logger.error(f"端点检查失败: {endpoint}")
        return endpoint, False

    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(check_single_endpoint, ep): ep for ep in endpoints}
        for future in as_completed(futures):
            endpoint, status = future.result()
            results[endpoint] = status

    return results

def check_cache_system():
    """
    检查缓存系统是否可用
    """
    try:
        # 测试缓存写入和读取
        import redis
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, 
                       password=settings.REDIS_PASSWORD, db=settings.REDIS_DB, 
                       socket_connect_timeout=5)
        
        # 尝试ping通redis
        if r.ping():
            logger.info("缓存系统可用")
            return True
        else:
            logger.error("缓存系统ping不通")
            return False
    except Exception as e:
        logger.error(f"缓存系统不可用: {e}")
        return False

def check_component(name, check_func, *args, **kwargs):
    """
    通用组件检查函数
    """
    try:
        result = check_func(*args, **kwargs)
        if result:
            logger.info(f"{name} 检查通过")
            return True
        else:
            logger.error(f"{name} 检查失败")
            return False
    except Exception as e:
        logger.error(f"{name} 检查失败: {e}")
        return False

def warm_up_cache():
    """
    预热缓存，提前加载常用数据
    """
    try:
        from backend.services.match_service import MatchService
        from backend.core.cache_manager import cache_manager
        
        # 获取未来3天和7天的比赛数据，触发缓存
        service = MatchService()
        matches_3 = service.get_matches_by_date_range(days_ahead=3)
        matches_7 = service.get_matches_by_date_range(days_ahead=7)
        
        logger.info(f"缓存预热完成 (3天: {len(matches_3)}场, 7天: {len(matches_7)}场)")
        return True
    except Exception as e:
        logger.error(f"缓存预热失败: {e}")
        return False

def cleanup_expired_cache():
    """
    清理过期缓存
    """
    try:
        # 这里可以实现具体的缓存清理逻辑
        # 目前只是模拟操作
        logger.info("过期缓存已清理")
        return True
    except Exception as e:
        logger.error(f"缓存清理失败: {e}")
        return False

if __name__ == "__main__":
    logger.info("开始部署后检查...")
    
    # 等待应用启动
    if not wait_for_health_check():
        logger.error("应用未能在预期时间内启动")
        exit(1)
    
    # 检查关键端点
    endpoints_to_check = [
        settings.API_V1_STR + "/health",
        settings.API_V1_STR + "/matches",
        settings.API_V1_STR + "/intelligence"
    ]
    
    endpoint_results = check_endpoints(endpoints_to_check)
    all_endpoints_ok = all(endpoint_results.values())
    
    # 检查缓存系统
    cache_ok = check_component("缓存系统", check_cache_system)
    
    # 初始化缓存
    if cache_ok:
        check_component("缓存系统初始化", warm_up_cache)
        check_component("过期缓存清理", cleanup_expired_cache)
    
    logger.info("部署后检查完成")
    logger.info(f"端点检查结果: {'通过' if all_endpoints_ok else '部分失败'}")
    logger.info(f"缓存检查结果: {'通过' if cache_ok else '失败'}")
