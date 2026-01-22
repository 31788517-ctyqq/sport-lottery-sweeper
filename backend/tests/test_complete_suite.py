"""
完整测试套件：覆盖爬虫、缓存、API端点
运行：pytest tests/test_complete_suite.py -v
"""
import pytest
import asyncio
import logging
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
import json
from backend.app.cache.cache_manager import MemoryCache, HybridCache, generate_cache_key, CACHE_KEYS, get_cache, CacheConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestSportteryScraper:
    """爬虫单元测试"""
    
    @pytest.mark.asyncio
    async def test_mock_data_generation(self):
        """测试模拟数据生成"""
        from backend.app.scrapers.sporttery_scraper_clean import sporttery_scraper
        
        async with sporttery_scraper:
            matches = await sporttery_scraper._generate_mock_data(3)
        
        # 验证数据结构
        assert len(matches) > 0, "模拟数据应该至少有一条"
        assert len(matches) == 15, "模拟数据应该生成15条"
        
        for match in matches:
            assert 'home_team' in match, "必须包含home_team字段"
            assert 'away_team' in match, "必须包含away_team字段"
            assert 'league' in match, "必须包含league字段"
            assert 'match_date' in match, "必须包含match_date字段"
            assert 'odds_home_win' in match, "必须包含赔率字段"
            assert match['home_team'] != match['away_team'], "主客队不能相同"
    
    @pytest.mark.asyncio
    async def test_date_filtering(self):
        """测试日期过滤功能"""
        from backend.app.scrapers.sporttery_scraper_clean import sporttery_scraper
        
        async with sporttery_scraper:
            matches_3day = await sporttery_scraper.get_recent_matches(3)
            matches_7day = await sporttery_scraper.get_recent_matches(7)
        
        # 3天的比赛应该少于7天的
        assert len(matches_3day) <= len(matches_7day), "3天的比赛数应该 <= 7天的"
        
        # 验证日期范围
        now = datetime.now()
        for match in matches_3day:
            match_time_str = match.get('match_date', '')
            # 应该在近3天内
            assert match_time_str != '', "比赛时间不能为空"
    
    @pytest.mark.asyncio
    async def test_scraper_context_manager(self):
        """测试爬虫上下文管理器"""
        from backend.app.scrapers.sporttery_scraper_clean import sporttery_scraper
        
        # 测试正常流程
        async with sporttery_scraper:
            assert sporttery_scraper.session is not None, "session应该被初始化"
        
        # 上下文退出后session应该被关闭
        # （注意：这取决于实现）
    
    @pytest.mark.asyncio
    async def test_scraper_returns_valid_data(self):
        """测试爬虫返回有效数据"""
        from backend.app.scrapers.sporttery_scraper_clean import sporttery_scraper
        
        async with sporttery_scraper:
            matches = await sporttery_scraper.get_recent_matches(3)
        
        assert isinstance(matches, list), "应该返回列表"
        assert len(matches) > 0, "应该返回至少一条数据"
        
        # 验证返回的数据包含所有必要字段
        required_fields = {
            'home_team', 'away_team', 'league', 'match_date', 
            'odds_home_win', 'odds_draw', 'odds_away_win'
        }
        
        for match in matches:
            assert isinstance(match, dict), "每条数据应该是字典"
            for field in required_fields:
                assert field in match, f"缺少必要字段: {field}"


class TestCacheManager:
    """缓存管理器单元测试"""
    
    @pytest.mark.asyncio
    async def test_memory_cache_basic_operations(self):
        """测试内存缓存基本操作"""
        from backend.app.cache.cache_manager import MemoryCache
        
        cache = MemoryCache()
        
        # 设置值
        await cache.set('test_key', {'data': 'test_value'}, ttl=3600)
        
        # 获取值
        value = await cache.get('test_key')
        assert value == {'data': 'test_value'}, "应该能正确获取设置的值"
        
        # 获取不存在的键
        value = await cache.get('non_existent_key')
        assert value is None, "不存在的键应该返回None"
        
        # 删除
        await cache.delete('test_key')
        value = await cache.get('test_key')
        assert value is None, "删除后应该无法获取"
    
    @pytest.mark.asyncio
    async def test_memory_cache_ttl(self):
        """测试内存缓存TTL过期"""
        from backend.app.cache.cache_manager import MemoryCache
        
        cache = MemoryCache()
        
        # 设置短TTL
        await cache.set('expire_test', 'value', ttl=1)
        
        # 立即获取应该成功
        value = await cache.get('expire_test')
        assert value == 'value', "应该能立即获取"
        
        # 等待过期
        await asyncio.sleep(1.1)
        value = await cache.get('expire_test')
        assert value is None, "过期后应该无法获取"
    
    @pytest.mark.asyncio
    async def test_memory_cache_stats(self):
        """测试缓存统计"""
        from backend.app.cache.cache_manager import MemoryCache
        
        cache = MemoryCache()
        
        await cache.set('key1', {'data': 1})
        await cache.set('key2', {'data': 2})
        
        stats = await cache.get_stats()
        assert stats['total_keys'] == 2, "应该有2个键"
        assert 'key1' in stats['keys'], "key1应该在统计中"
        assert 'key2' in stats['keys'], "key2应该在统计中"
    
    @pytest.mark.asyncio
    async def test_hybrid_cache_fallback(self):
        """测试混合缓存回退机制"""
        from backend.app.cache.cache_manager import HybridCache
        
        cache = HybridCache()
        
        # Redis不可用，应该使用内存缓存
        await cache.set('hybrid_test', 'value')
        value = await cache.get('hybrid_test')
        assert value == 'value', "应该使用内存缓存"
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """测试缓存键生成"""
        from backend.app.cache.cache_manager import generate_cache_key, CACHE_KEYS
        
        # 基本键生成
        key1 = generate_cache_key('prefix', 'arg1', 'arg2')
        assert 'prefix' in key1, "键应该包含前缀"
        
        # 使用预定义键
        key2 = CACHE_KEYS['RECENT_MATCHES'](3)
        assert 'matches:recent' in key2, "应该包含特定前缀"


class TestJCZQRoutes:
    """竞彩足球API路由测试"""
    
    @pytest.mark.asyncio
    async def test_recent_matches_route(self, client):
        """测试获取最近比赛路由"""
        response = client.get("/api/jczq/matches/recent?days=3")
        assert response.status_code == 200, "应该返回200状态码"
        
        data = response.json()
        assert data['status'] == 'success', "应该返回success状态"
        assert 'matches' in data, "应该包含matches字段"
        assert 'count' in data, "应该包含count字段"
        assert isinstance(data['matches'], list), "matches应该是列表"
    
    @pytest.mark.asyncio
    async def test_popular_matches_route(self, client):
        """测试热门比赛路由"""
        response = client.get("/api/jczq/matches/popular?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data['matches']) <= 10, "应该返回不超过limit数量的比赛"
    
    @pytest.mark.asyncio
    async def test_leagues_route(self, client):
        """测试联赛列表路由"""
        response = client.get("/api/jczq/leagues?days=3")
        assert response.status_code == 200
        
        data = response.json()
        assert 'leagues' in data, "应该包含leagues字段"
        assert isinstance(data['leagues'], list), "leagues应该是列表"
    
    @pytest.mark.asyncio
    async def test_league_filter(self, client):
        """测试联赛过滤"""
        response = client.get("/api/jczq/matches/recent?days=3&league=英超")
        assert response.status_code == 200
        
        data = response.json()
        # 如果有过滤结果，每个都应该是英超
        for match in data.get('matches', []):
            assert match.get('league') == '英超', "应该只返回英超比赛"
    
    @pytest.mark.asyncio
    async def test_sorting(self, client):
        """测试排序功能"""
        # 按时间排序
        response = client.get("/api/jczq/matches/recent?days=3&sort_by=date")
        assert response.status_code == 200
        
        # 按热度排序
        response = client.get("/api/jczq/matches/recent?days=3&sort_by=popularity")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_cache_clear_route(self, client):
        """测试缓存清空路由"""
        response = client.post("/api/jczq/cache/clear")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'success', "清空缓存应该返回success"
    
    @pytest.mark.asyncio
    async def test_cache_stats_route(self, client):
        """测试缓存统计路由"""
        response = client.get("/api/jczq/cache/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert 'cache_stats' in data, "应该包含cache_stats"


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_scraper_to_cache_to_api_flow(self):
        """测试从爬虫到缓存再到API的完整流程"""
        from backend.app.scrapers.sporttery_scraper_clean import sporttery_scraper
        from backend.app.cache.cache_manager import get_cache, CACHE_KEYS, CacheConfig
        
        cache = get_cache()
        cache_key = CACHE_KEYS['RECENT_MATCHES'](3)
        
        # 步骤1：清空缓存
        await cache.delete(cache_key)
        
        # 步骤2：从爬虫获取数据
        async with sporttery_scraper:
            matches = await sporttery_scraper.get_recent_matches(3)
        
        # 步骤3：缓存数据
        await cache.set(cache_key, matches)
        
        # 步骤4：从缓存获取
        cached_matches = await cache.get(cache_key)
        
        # 验证
        assert cached_matches is not None, "缓存应该有数据"
        assert len(cached_matches) > 0, "缓存数据应该不为空"
        assert cached_matches == matches, "缓存数据应该与原数据一致"
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self):
        """测试并发请求处理"""
        from backend.app.scrapers.sporttery_scraper_clean import sporttery_scraper
        from backend.app.cache.cache_manager import get_cache
        
        cache = get_cache()
        
        # 并发执行多个请求
        async def get_matches(days):
            async with sporttery_scraper:
                return await sporttery_scraper.get_recent_matches(days)
        
        tasks = [get_matches(3) for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # 所有请求都应该返回数据
        assert all(len(r) > 0 for r in results), "所有请求都应该返回数据"


class TestDataValidation:
    """数据验证测试"""
    
    @pytest.mark.asyncio
    async def test_match_data_types(self):
        """验证比赛数据类型"""
        from backend.app.scrapers.sporttery_scraper_clean import sporttery_scraper
        
        async with sporttery_scraper:
            matches = await sporttery_scraper.get_recent_matches(3)
        
        for match in matches:
            assert isinstance(match.get('home_team'), str), "home_team应该是字符串"
            assert isinstance(match.get('away_team'), str), "away_team应该是字符串"
            assert isinstance(match.get('odds_home_win'), (int, float)), "赔率应该是数字"
            assert isinstance(match.get('popularity'), int), "热度应该是整数"
    
    @pytest.mark.asyncio
    async def test_odds_range_validation(self):
        """验证赔率范围"""
        from backend.app.scrapers.sporttery_scraper_clean import sporttery_scraper
        
        async with sporttery_scraper:
            matches = await sporttery_scraper.get_recent_matches(3)
        
        for match in matches:
            odds_home = match.get('odds_home_win', 0)
            odds_draw = match.get('odds_draw', 0)
            odds_away = match.get('odds_away_win', 0)
            
            # 赔率应该在合理范围内
            assert 1.0 <= odds_home <= 10.0, f"主队赔率异常: {odds_home}"
            assert 1.0 <= odds_draw <= 10.0, f"平局赔率异常: {odds_draw}"
            assert 1.0 <= odds_away <= 10.0, f"客队赔率异常: {odds_away}"


# Fixture
@pytest.fixture
def client():
    """创建FastAPI测试客户端"""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


@pytest.fixture
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# 运行测试
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
