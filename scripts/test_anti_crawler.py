"""
反爬虫功能测试脚本
测试代理池、请求头伪装、Cookie管理等功能
"""
import asyncio
import logging
import json
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_proxy_pool():
    """测试代理池功能"""
    logger.info("=== 测试代理池功能 ===")
    
    try:
        from backend.scrapers.core.proxy_pool import get_proxy_pool, ProxyPool
        
        # 创建代理池实例
        proxy_pool = get_proxy_pool()
        
        # 添加测试代理（这里使用示例代理，实际使用需要替换为真实代理）
        test_proxies = [
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080", 
            "socks5://proxy3.example.com:1080",
            "http://user:pass@proxy4.example.com:3128"
        ]
        
        for proxy_url in test_proxies:
            proxy_pool.add_proxy(proxy_url)
        
        logger.info(f"添加了 {len(test_proxies)} 个测试代理")
        
        # 显示代理池统计
        stats = proxy_pool.get_stats()
        logger.info(f"代理池统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        
        # 测试获取代理
        proxy = proxy_pool.get_random_proxy()
        if proxy:
            logger.info(f"获取到随机代理: {proxy.url}")
        
        best_proxy = proxy_pool.get_best_proxy()
        if best_proxy:
            logger.info(f"获取到最佳代理: {best_proxy.url} (评分: {best_proxy.stats.score:.1f})")
        
        # 执行健康检查
        health_result = await proxy_pool.health_check_all()
        logger.info(f"健康检查完成: {json.dumps(health_result, indent=2, ensure_ascii=False)}")
        
        # 停止健康检查循环
        await proxy_pool.stop_health_check_loop()
        
        logger.info("代理池测试完成")
        return True
        
    except Exception as e:
        logger.error(f"代理池测试失败: {e}", exc_info=True)
        return False


async def test_headers_manager():
    """测试请求头管理功能"""
    logger.info("=== 测试请求头管理功能 ===")
    
    try:
        from backend.scrapers.core.headers_manager import get_headers_manager, get_cookie_manager
        
        # 测试请求头管理器
        headers_manager = get_headers_manager()
        
        # 生成不同类型的请求头
        profiles = ['chrome_desktop', 'chrome_mobile', 'firefox_desktop']
        
        for profile in profiles:
            headers = headers_manager.generate_headers(profile_name=profile)
            logger.info(f"配置文件 {profile} 生成的请求头数量: {len(headers)}")
            logger.info(f"User-Agent: {headers.get('User-Agent', 'N/A')[:80]}...")
            logger.info(f"Accept-Language: {headers.get('Accept-Language', 'N/A')}")
            logger.info(f"Referer: {headers.get('Referer', 'N/A')}")
            
            # 显示指纹相关头部
            fingerprint_headers = {k: v for k, v in headers.items() if k.startswith('sec-')}
            if fingerprint_headers:
                logger.info(f"指纹头部: {fingerprint_headers}")
            logger.info("-" * 50)
        
        # 测试配置轮换
        original_profile = headers_manager.current_profile
        logger.info(f"当前配置: {original_profile}")
        
        headers_manager.rotate_profile()
        new_profile = headers_manager.current_profile
        logger.info(f"轮换后配置: {new_profile}")
        
        # 测试Cookie管理器
        cookie_manager = get_cookie_manager("test_cookies.json")
        
        # 生成浏览器指纹
        fingerprint = cookie_manager.generate_browser_fingerprint()
        logger.info(f"浏览器指纹: {json.dumps(fingerprint, indent=2, ensure_ascii=False)}")
        
        # 测试带指纹的请求头
        headers_with_fp = cookie_manager.get_headers_with_fingerprint()
        logger.info(f"带指纹的请求头数量: {len(headers_with_fp)}")
        
        fp_headers = {k: v for k, v in headers_with_fp.items() if k.startswith('sec-ch-')}
        if fp_headers:
            logger.info(f"客户端提示头部: {fp_headers}")
        
        logger.info("请求头管理测试完成")
        return True
        
    except Exception as e:
        logger.error(f"请求头管理测试失败: {e}", exc_info=True)
        return False


async def test_enhanced_engine():
    """测试增强爬虫引擎"""
    logger.info("=== 测试增强爬虫引擎 ===")
    
    try:
        from backend.scrapers.core.enhanced import EnhancedScraperEngine
        
        # 创建增强引擎（不使用代理进行测试）
        engine = EnhancedScraperEngine(
            max_connections=10,
            timeout=10,
            max_retries=2,
            rate_limit=5,  # 限制为5请求/秒
            enable_cache=True,
            cache_ttl=60,  # 1分钟缓存
            header_profile="chrome_desktop",
            enable_fingerprint=True,
            rotation_interval=10  # 每10个请求轮换
        )
        
        await engine.start()
        logger.info("增强引擎启动成功")
        
        # 测试健康检查
        health = await engine.health_check()
        logger.info(f"引擎健康检查: {json.dumps(health, indent=2, ensure_ascii=False)}")
        
        # 测试请求统计
        stats_before = engine.get_stats()
        logger.info(f"初始统计: 总请求={stats_before['total_requests']}, 代理使用率={stats_before.get('proxy_usage_rate', 0)}%")
        
        # 注意：这里不进行实际HTTP请求测试，避免外部依赖
        # 只测试引擎内部功能
        
        await engine.close()
        logger.info("增强引擎测试完成")
        return True
        
    except Exception as e:
        logger.error(f"增强引擎测试失败: {e}", exc_info=True)
        return False


async def test_config_loader():
    """测试配置加载器"""
    logger.info("=== 测试配置加载器 ===")
    
    try:
        from backend.scrapers.core.config_loader import get_anti_crawler_config, create_enhanced_engine_from_config
        
        # 测试配置加载
        config = get_anti_crawler_config()
        logger.info(f"代理池启用: {config.proxy_enabled}")
        logger.info(f"代理数量: {len(config.proxy_urls)}")
        logger.info(f"Cookie启用: {config.cookie_enabled}")
        logger.info(f"指纹启用: {config.enable_fingerprint}")
        
        # 测试从配置创建引擎
        engine_config = config.create_engine_config()
        logger.info(f"引擎配置项: {list(engine_config.keys())}")
        
        # 显示关键配置
        key_settings = {
            'max_connections': engine_config.get('max_connections'),
            'timeout': engine_config.get('timeout'),
            'header_profile': engine_config.get('header_profile'),
            'enable_fingerprint': engine_config.get('enable_fingerprint'),
            'proxy_urls_count': len(engine_config.get('proxy_urls', []))
        }
        logger.info(f"关键配置: {json.dumps(key_settings, indent=2, ensure_ascii=False)}")
        
        logger.info("配置加载器测试完成")
        return True
        
    except Exception as e:
        logger.error(f"配置加载器测试失败: {e}", exc_info=True)
        return False


async def main():
    """主测试函数"""
    logger.info("开始反爬虫功能测试")
    logger.info(f"测试时间: {datetime.now().isoformat()}")
    
    test_results = {}
    
    # 测试配置加载器
    test_results['config_loader'] = await test_config_loader()
    
    # 测试请求头管理
    test_results['headers_manager'] = await test_headers_manager()
    
    # 测试代理池
    test_results['proxy_pool'] = await test_proxy_pool()
    
    # 测试增强引擎
    test_results['enhanced_engine'] = await test_enhanced_engine()
    
    # 汇总结果
    logger.info("\n=== 测试结果汇总 ===")
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        logger.info("🎉 所有反爬虫功能测试通过！")
    else:
        logger.warning(f"⚠️  {total - passed} 项测试失败，请检查配置和实现")
    
    return passed == total


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())
    exit(0 if success else 1)