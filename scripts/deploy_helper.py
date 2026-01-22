"""
部署辅助脚本：健康检查、初始化、监控
"""
import asyncio
import logging
import sys
from datetime import datetime
import httpx

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthChecker:
    """应用健康检查"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=5.0)
    
    async def check_health(self) -> bool:
        """检查应用健康状态"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                logger.info("✓ 应用健康检查通过")
                return True
            else:
                logger.error(f"✗ 应用返回错误状态码: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ 应用不可用: {e}")
            return False
    
    async def check_api_endpoint(self, endpoint: str) -> bool:
        """检查具体API端点"""
        try:
            response = await self.client.get(f"{self.base_url}{endpoint}")
            if response.status_code == 200:
                logger.info(f"✓ 端点可用: {endpoint}")
                return True
            else:
                logger.warning(f"✗ 端点返回错误: {endpoint} ({response.status_code})")
                return False
        except Exception as e:
            logger.error(f"✗ 端点不可用: {endpoint} ({e})")
            return False
    
    async def check_cache(self) -> bool:
        """检查缓存系统"""
        try:
            response = await self.client.get(f"{self.base_url}/api/jczq/cache/stats")
            if response.status_code == 200:
                logger.info("✓ 缓存系统可用")
                return True
            else:
                logger.error(f"✗ 缓存系统错误: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ 缓存系统不可用: {e}")
            return False
    
    async def run_full_check(self) -> bool:
        """运行完整健康检查"""
        logger.info("=" * 50)
        logger.info("开始应用健康检查...")
        logger.info("=" * 50)
        
        checks = [
            ("应用健康", self.check_health()),
            ("比赛API", self.check_api_endpoint("/api/jczq/matches/recent?days=3")),
            ("热门比赛", self.check_api_endpoint("/api/jczq/matches/popular")),
            ("联赛列表", self.check_api_endpoint("/api/jczq/leagues")),
            ("缓存系统", self.check_cache()),
        ]
        
        results = []
        for name, check in checks:
            try:
                result = await check
                results.append(result)
            except Exception as e:
                logger.error(f"✗ {name} 检查失败: {e}")
                results.append(False)
        
        logger.info("=" * 50)
        logger.info(f"检查结果: {sum(results)}/{len(results)} 通过")
        logger.info("=" * 50)
        
        return all(results)
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


class DeploymentHelper:
    """部署辅助工具"""
    
    @staticmethod
    async def initialize_cache():
        """初始化缓存系统"""
        try:
            from ..app.cache.cache_manager import init_cache
            logger.info("初始化缓存系统...")
            await init_cache(redis_url="redis://redis:6379")
            logger.info("✓ 缓存系统初始化完成")
            return True
        except Exception as e:
            logger.error(f"✗ 缓存系统初始化失败: {e}")
            return False
    
    @staticmethod
    async def warm_up_cache():
        """预热缓存"""
        try:
            from ..app.scrapers.sporttery_clean import sporttery_scraper
            from ..app.cache.cache_manager import get_cache, CACHE_KEYS, CacheConfig
            
            logger.info("预热缓存...")
            cache = get_cache()
            
            # 获取近3天和7天的数据
            async with sporttery_scraper:
                matches_3 = await sporttery_scraper.get_recent_matches(3)
                matches_7 = await sporttery_scraper.get_recent_matches(7)
            
            # 缓存数据
            await cache.set(CACHE_KEYS['RECENT_MATCHES'](3), matches_3, ttl=CacheConfig.MATCH_LIST_TTL)
            await cache.set(CACHE_KEYS['RECENT_MATCHES'](7), matches_7, ttl=CacheConfig.MATCH_LIST_TTL)
            
            logger.info(f"✓ 缓存预热完成 (3天: {len(matches_3)}场, 7天: {len(matches_7)}场)")
            return True
        except Exception as e:
            logger.error(f"✗ 缓存预热失败: {e}")
            return False
    
    @staticmethod
    async def cleanup_old_cache():
        """清理过期缓存"""
        try:
            from ..app.cache.cache_manager import get_cache
            
            logger.info("清理过期缓存...")
            cache = get_cache()
            await cache.clear()
            logger.info("✓ 过期缓存已清理")
            return True
        except Exception as e:
            logger.error(f"✗ 缓存清理失败: {e}")
            return False


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="部署辅助脚本")
    parser.add_argument('--check', action='store_true', help='运行健康检查')
    parser.add_argument('--init-cache', action='store_true', help='初始化缓存')
    parser.add_argument('--warmup', action='store_true', help='预热缓存')
    parser.add_argument('--cleanup', action='store_true', help='清理缓存')
    parser.add_argument('--url', default='http://localhost:8000', help='应用URL')
    
    args = parser.parse_args()
    
    if args.check:
        checker = HealthChecker(args.url)
        try:
            success = await checker.run_full_check()
            sys.exit(0 if success else 1)
        finally:
            await checker.close()
    
    elif args.init_cache:
        success = await DeploymentHelper.initialize_cache()
        sys.exit(0 if success else 1)
    
    elif args.warmup:
        success = await DeploymentHelper.warm_up_cache()
        sys.exit(0 if success else 1)
    
    elif args.cleanup:
        success = await DeploymentHelper.cleanup_old_cache()
        sys.exit(0 if success else 1)
    
    else:
        # 默认运行所有初始化
        logger.info("运行完整部署初始化...")
        
        success = all([
            await DeploymentHelper.initialize_cache(),
            await DeploymentHelper.warm_up_cache(),
        ])
        
        # 运行健康检查
        checker = HealthChecker(args.url)
        try:
            check_success = await checker.run_full_check()
            success = success and check_success
        finally:
            await checker.close()
        
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
