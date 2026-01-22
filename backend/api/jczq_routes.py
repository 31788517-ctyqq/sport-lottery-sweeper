"""
⚠️ 已废弃 - 向后兼容路由
此文件将在 v2.0 版本移除
请使用 /api/v1/jczq 新版API

前端集成API：暴露缓存的比赛数据，支持实时更新、过滤、排序
提供向后兼容的API端点
"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..core.cache_manager import cached_method, get_cache_manager

router = APIRouter(tags=["legacy-jczq-deprecated"])
logger = logging.getLogger(__name__)

# 废弃警告
DEPRECATION_WARNING = {
    "deprecated": True,
    "deprecation_message": "此API已废弃，将在v2.0移除。请使用 /api/v1/jczq 新版API",
    "migration_guide": "https://github.com/your-repo/docs/api-migration.md"
}


@router.get("/jczq/matches/recent", summary="[已废弃] 获取近期比赛赛程", deprecated=True)
async def get_recent_matches(
    days: int = Query(3, ge=1, le=7, description="未来N天内的比赛"),
    league: Optional[str] = Query(None, description="联赛过滤（如：英超、西甲等）"),
    sort_by: str = Query("date", description="排序方式：date（时间）、popularity（热度）、odds（赔率）"),
    page: int = Query(1, ge=1, description="分页页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页返回的比赛数量")
) -> Dict[str, Any]:
    """
    [已废弃] 获取近期比赛赛程数据，支持分页和排序
    请使用新版API: GET /api/v1/jczq/matches
    """
    logger.warning("使用已废弃的API: /jczq/matches/recent")
    try:
        # 延迟导入，只在需要时才导入相关模块
        from ..scrapers.sporttery_scraper import sporttery_scraper
        cache_manager = get_cache_manager()

        cache_key = f"recent_matches:{days}:{league}:{sort_by}:{page}:{page_size}"

        # 尝试从缓存获取
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            logger.info(f"[缓存命中] 近期比赛数据 (days={days})")
            matches = cached_data
        else:
            logger.info(f"[缓存未命中] 获取新数据 (days={days})")
            # 使用爬虫获取数据
            async with sporttery_scraper:
                matches = await sporttery_scraper.get_recent_matches(days)

            # 缓存数据，设置TTL为5分钟
            from datetime import timedelta
            await cache_manager.set(cache_key, matches, timedelta(minutes=5))

        # 联赛过滤
        if league:
            matches = [m for m in matches if m.get('league') == league]
            logger.debug(f"按联赛过滤: {league} -> {len(matches)}场")

        # 排序
        if sort_by == "popularity":
            matches = sorted(matches, key=lambda x: x.get('popularity', 0), reverse=True)
        elif sort_by == "odds":
            matches = sorted(matches, key=lambda x: x.get('odds_home_win', 0))
        else:  # date
            matches = sorted(matches, key=lambda x: x.get('match_date', ''))

        # 分页
        total_matches = len(matches)
        start = (page - 1) * page_size
        end = start + page_size
        matches = matches[start:end]

        return {
            'status': 'success',
            'count': len(matches),
            'total': total_matches,
            'page': page,
            'page_size': page_size,
            'days': days,
            'league_filter': league,
            'sort_by': sort_by,
            'matches': matches,
            **DEPRECATION_WARNING
        }

    except Exception as e:
        logger.error(f"获取比赛数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/jczq/matches/popular", summary="[已废弃] 获取热门比赛", deprecated=True)
async def get_popular_matches(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
) -> Dict[str, Any]:
    """[已废弃] 获取热门比赛TOP N - 请使用 /api/v1/jczq/popular"""
    logger.warning("使用已废弃的API: /jczq/matches/popular")
    try:
        from ..scrapers.sporttery_scraper import sporttery_scraper
        cache_manager = get_cache_manager()
        
        cache_key = f"popular_matches:{limit}"
        
        # 尝试从缓存获取
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            logger.info(f"[缓存命中] 热门比赛 (limit={limit})")
            matches = cached_data
        else:
            logger.info(f"[缓存未命中] 获取新数据 (limit={limit})")
            # 获取近7天的所有比赛
            async with sporttery_scraper:
                matches = await sporttery_scraper.get_recent_matches(7)
            
            # 按热度排序并取前N个
            matches = sorted(matches, key=lambda x: x.get('popularity', 0), reverse=True)[:limit]
            
            # 缓存数据
            from datetime import timedelta
            await cache_manager.set(cache_key, matches, timedelta(minutes=5))
        
        return {
            'status': 'success',
            'count': len(matches),
            'limit': limit,
            'matches': matches,
            **DEPRECATION_WARNING
        }
    
    except Exception as e:
        logger.error(f"获取热门比赛失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/jczq/leagues", summary="[已废弃] 获取联赛列表", deprecated=True)
async def get_leagues(days: int = Query(3, ge=1, le=7)) -> Dict[str, Any]:
    """[已废弃] 获取未来N天内的所有联赛 - 请使用 /api/v1/jczq/leagues"""
    logger.warning("使用已废弃的API: /jczq/leagues")
    try:
        from ..scrapers.sporttery_scraper import sporttery_scraper
        cache_manager = get_cache_manager()
        
        cache_key = f"leagues:{days}"
        
        # 尝试从缓存获取
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            logger.info(f"[缓存命中] 联赛列表 (days={days})")
            return cached_data
        else:
            logger.info(f"[缓存未命中] 获取新联赛数据 (days={days})")
            async with sporttery_scraper:
                matches = await sporttery_scraper.get_recent_matches(days)
            
            # 提取唯一的联赛
            leagues = sorted(set(m.get('league', '未知') for m in matches if m.get('league')))
            
            # 统计每个联赛的比赛数
            league_stats = {}
            for match in matches:
                league = match.get('league', '未知')
                league_stats[league] = league_stats.get(league, 0) + 1
            
            result = {
                'status': 'success',
                'days': days,
                'total_leagues': len(leagues),
                'leagues': [
                    {
                        'name': league,
                        'match_count': league_stats.get(league, 0)
                    }
                    for league in leagues
                ],
                **DEPRECATION_WARNING
            }
            
            # 缓存联赛数据
            from datetime import timedelta
            await cache_manager.set(cache_key, result, timedelta(minutes=10))
            
            return result
    
    except Exception as e:
        logger.error(f"获取联赛列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/jczq/match/{match_id}", summary="[已废弃] 获取比赛详情", deprecated=True)
async def get_match_detail(match_id: str) -> Dict[str, Any]:
    """[已废弃] 获取单场比赛详细信息 - 请使用 /api/v1/matches/{match_id}"""
    logger.warning(f"使用已废弃的API: /jczq/match/{match_id}")
    try:
        from ..scrapers.sporttery_scraper import sporttery_scraper
        cache_manager = get_cache_manager()
        
        cache_key = f"match_detail:{match_id}"
        
        # 尝试从缓存获取
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
         return {
            'status': 'success',
            'source': 'cache',
            'match': cached_data,
            **DEPRECATION_WARNING
        }
        
        # 从爬虫获取所有比赛
        async with sporttery_scraper:
            matches = await sporttery_scraper.get_recent_matches(7)
        
        # 查找目标比赛
        match = next((m for m in matches if m.get('id') == match_id or m.get('match_id') == match_id), None)
        
        if not match:
            raise HTTPException(status_code=404, detail=f"比赛不存在: {match_id}")
        
        # 缓存比赛详情
        from datetime import timedelta
        await cache_manager.set(cache_key, match, timedelta(minutes=5))
        
        return {
            'status': 'success',
            'source': 'fresh',
            'match': match,
            **DEPRECATION_WARNING
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取比赛详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.post("/jczq/cache/clear", summary="清空缓存（向后兼容）")
async def clear_cache(pattern: Optional[str] = Query(None, description="清空模式（如：matches:*）")) -> Dict[str, Any]:
    """清空比赛缓存（向后兼容端点）"""
    try:
        cache_manager = get_cache_manager()
        
        if pattern:
            logger.info(f"清空缓存模式: {pattern}")
            cleared_count = await cache_manager.invalidate_pattern(pattern)
            result_msg = f"清除了 {cleared_count} 个匹配的缓存项"
        else:
            logger.info("清空所有缓存")
            await cache_manager.clear()
            result_msg = "所有缓存已清空"
        
        return {
            'status': 'success',
            'message': result_msg,
            'pattern': pattern,
        }
    
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.get("/jczq/cache/stats", summary="获取缓存统计（向后兼容）")
async def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息（向后兼容端点）"""
    try:
        cache_manager = get_cache_manager()
        stats = await cache_manager.get_stats()
        
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'cache_stats': stats,
        }
    
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/jczq/stats", summary="获取数据统计（向后兼容）")
async def get_data_stats(days: int = Query(3, ge=1, le=7)) -> Dict[str, Any]:
    """获取比赛数据统计信息（向后兼容端点）"""
    try:
        from ..scrapers.sporttery_scraper import sporttery_scraper
        cache_manager = get_cache_manager()
        
        cache_key = f"data_stats:{days}"
        
        # 尝试从缓存获取
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            logger.info(f"[缓存命中] 数据统计 (days={days})")
            return cached_data
        else:
            logger.info(f"[缓存未命中] 获取新统计数据 (days={days})")
            async with sporttery_scraper:
                matches = await sporttery_scraper.get_recent_matches(days)
            
            # 统计信息
            leagues = {}
            total_odds_home = 0
            total_odds_draw = 0
            total_odds_away = 0
            
            for match in matches:
                league = match.get('league', '未知')
                if league not in leagues:
                    leagues[league] = {'count': 0, 'avg_popularity': 0, 'total_popularity': 0}
                
                leagues[league]['count'] += 1
                leagues[league]['total_popularity'] += match.get('popularity', 0)
                
                total_odds_home += match.get('odds_home_win', 0)
                total_odds_draw += match.get('odds_draw', 0)
                total_odds_away += match.get('odds_away_win', 0)
            
            # 计算平均值
            for league in leagues:
                if leagues[league]['count'] > 0:
                    leagues[league]['avg_popularity'] = round(
                        leagues[league]['total_popularity'] / leagues[league]['count'], 2
                    )
            
            count = len(matches)
            
            result = {
                'status': 'success',
                'days': days,
                'total_matches': count,
                'avg_odds_home': round(total_odds_home / count, 2) if count > 0 else 0,
                'avg_odds_draw': round(total_odds_draw / count, 2) if count > 0 else 0,
                'avg_odds_away': round(total_odds_away / count, 2) if count > 0 else 0,
                'leagues': leagues,
            }
            
            # 缓存统计数据
            from datetime import timedelta
            await cache_manager.set(cache_key, result, timedelta(minutes=10))
            
            return result
    
    except Exception as e:
        logger.error(f"获取数据统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/jczq/matches", summary="[已废弃] 获取竞彩足球比赛", deprecated=True)
async def get_jczq_matches():
    """
    [已废弃] 获取竞彩足球比赛数据
    请使用新版API: GET /api/v1/jczq/matches
    """
    logger.warning("使用已废弃的API: /jczq/matches")
    try:
        from ..scrapers.sporttery_scraper import sporttery_scraper
        cache_manager = get_cache_manager()
        
        # 尝试从缓存获取比赛数据
        cache_key = "jczq_matches_data"
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            logger.info("[缓存命中] 竞彩足球比赛数据")
            matches = cached_data['matches']
        else:
            logger.info("[缓存未命中] 获取新竞彩足球数据")
            async with sporttery_scraper:
                raw_matches = await sporttery_scraper.get_recent_matches(3)
            
            # 转换数据格式以适应前端需求
            matches = []
            for raw_match in raw_matches[:15]:  # 限制为15场比赛
                # 为每场比赛生成模拟情报数据
                intelligence = generate_mock_intelligence()
                match_data = {
                    'id': raw_match.get('id', f"match_{len(matches)+1}"),
                    'league': raw_match.get('league', '未知联赛'),
                    'homeTeam': raw_match.get('home_team', '主队'),
                    'awayTeam': raw_match.get('away_team', '客队'),
                    'matchTime': raw_match.get('match_date', datetime.now().isoformat()),
                    'score': raw_match.get('score', '-:-'),
                    'odds': {
                        'homeWin': str(raw_match.get('odds_home_win', 2.1)),
                        'draw': str(raw_match.get('odds_draw', 3.2)),
                        'awayWin': str(raw_match.get('odds_away_win', 3.5))
                    },
                    'status': raw_match.get('status', '未开始'),
                    'intelligence': intelligence
                }
                matches.append(match_data)
            
            # 缓存数据
            from datetime import timedelta
            await cache_manager.set(cache_key, {'matches': matches}, timedelta(minutes=5))
        
        # 计算统计数据
        stats = {
            'totalMatches': len(matches),
            'upcomingMatches': len([m for m in matches if m['status'] == '未开始']),
            'liveMatches': len([m for m in matches if m['status'] == '进行中']),
            'finishedMatches': len([m for m in matches if m['status'] == '已结束']),
            'totalIntelligence': sum(len(m['intelligence']) for m in matches),
            'highWeightIntelligence': sum(1 for m in matches for i in m['intelligence'] if i['weight'] >= 8.0)
        }
        
        return {
            'matches': matches,
            'stats': stats,
            **DEPRECATION_WARNING
        }
    except Exception as e:
        logger.error(f"获取竞彩足球比赛数据失败: {e}")
        # 返回模拟数据作为备选
        return generate_mock_response()


def generate_mock_intelligence():
    """生成模拟情报数据"""
    import random
    from datetime import datetime, timedelta
    
    intelligence_types = [
        {'id': 'sp', 'name': '赔率变动', 'icon': 'fas fa-chart-line', 'color': 'var(--tag-sp)'},
        {'id': 'injury', 'name': '伤病情报', 'icon': 'fas fa-user-injured', 'color': 'var(--tag-injury)'},
        {'id': 'weather', 'name': '天气影响', 'icon': 'fas fa-cloud-rain', 'color': 'var(--tag-weather)'},
        {'id': 'referee', 'name': '裁判信息', 'icon': 'fas fa-whistle', 'color': 'var(--tag-referee)'},
        {'id': 'motive', 'name': '战意分析', 'icon': 'fas fa-fire', 'color': 'var(--tag-motive)'},
    ]
    
    sources = [
        {'id': 'official', 'name': '官方', 'color': 'var(--source-official)'},
        {'id': 'media', 'name': '媒体', 'color': 'var(--source-media)'},
        {'id': 'social', 'name': '社媒', 'color': 'var(--source-social)'},
        {'id': 'bookmaker', 'name': '机构', 'color': 'var(--source-bookmaker)'},
    ]
    
    # 每场比赛生成3-7条情报
    count = random.randint(3, 7)
    intelligence = []
    for _ in range(count):
        intel_type = random.choice(intelligence_types)
        source = random.choice(sources)
        weight = round(random.uniform(1.0, 10.0), 1)
        is_new = random.random() < 0.3  # 30% 新情报
        
        # 根据情报类型生成内容
        title_prefixes = {
            'sp': ['重要赔率变动', '欧指大幅调整', '亚盘深度分析'],
            'injury': ['主力球员伤缺', '关键位置减员', '复出时间未定'],
            'weather': ['恶劣天气预警', '场地条件不佳', '气温影响发挥'],
            'referee': ['裁判执法风格', '争议判罚记录', '黄牌倾向明显'],
            'motive': ['争冠形势影响', '保级压力巨大', '国家德比战意']
        }
        titles = title_prefixes.get(intel_type['id'], ['其他类型情报'])
        title = random.choice(titles)
        
        content_samples = {
            'sp': ['根据最新数据监控，本场比赛的欧指出现明显变动...', '亚盘方面，亚洲盘口从平手升至主让平半...'],
            'injury': ['据官方消息，主队核心前锋张三在训练中拉伤大腿肌肉...', '客队中场主力李四累计黄牌停赛...'],
            'weather': ['气象预报显示，比赛当日将有大雨，场地湿滑会影响传球精准度...', '气温降至5摄氏度以下...'],
            'referee': ['本场比赛裁判张三执法风格偏向进攻，场均黄牌数达到4.2张...', 'VAR使用率较高...'],
            'motive': ['本场比赛关系到争冠形势，主队战意十足...', '客队已无降级风险，战意存疑...']
        }
        contents = content_samples.get(intel_type['id'], ['暂无具体内容，仅供参考。'])
        content = random.choice(contents)
        
        intel = {
            'id': f"intel_{random.randint(1000, 9999)}",
            'type': intel_type['id'],
            'source': source['id'],
            'title': title,
            'content': content,
            'weight': weight,
            'time': (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
            'isNew': is_new,
            'impact': round(weight * random.uniform(0.7, 1.3), 1)
        }
        intelligence.append(intel)
    
    return intelligence


def generate_mock_response():
    """生成模拟响应数据"""
    import random
    from datetime import datetime, timedelta
    
    # 生成15场比赛的模拟数据
    matches = []
    for i in range(15):
        intelligence = generate_mock_intelligence()
        match_data = {
            'id': f"match_{i+1}",
            'league': random.choice(['英超', '西甲', '德甲', '意甲', '法甲', '中超']),
            'homeTeam': f"主队{i+1}",
            'awayTeam': f"客队{i+1}",
            'matchTime': (datetime.now() + timedelta(hours=random.randint(1, 48))).isoformat(),
            'score': f"{random.randint(0, 4)}:{random.randint(0, 4)}" if random.random() > 0.6 else "-:-",
            'odds': {
                'homeWin': str(round(random.uniform(1.5, 3.5), 2)),
                'draw': str(round(random.uniform(2.5, 4.0), 2)),
                'awayWin': str(round(random.uniform(2.0, 5.0), 2))
            },
            'status': random.choice(['未开始', '进行中', '已结束']),
            'intelligence': intelligence
        }
        matches.append(match_data)
    
    # 计算统计数据
    stats = {
        'totalMatches': len(matches),
        'upcomingMatches': len([m for m in matches if m['status'] == '未开始']),
        'liveMatches': len([m for m in matches if m['status'] == '进行中']),
        'finishedMatches': len([m for m in matches if m['status'] == '已结束']),
        'totalIntelligence': sum(len(m['intelligence']) for m in matches),
        'highWeightIntelligence': sum(1 for m in matches for i in m['intelligence'] if i['weight'] >= 8.0)
    }
    
    return {
        'matches': matches,
        'stats': stats
    }


@router.post("/jczq/refresh", summary="[已废弃] 刷新数据", deprecated=True)
async def refresh_jczq_data():
    """
    [已废弃] 刷新竞彩足球数据
    请使用新版API: POST /api/v1/jczq/refresh
    """
    logger.warning("使用已废弃的API: /jczq/refresh")
    try:
        cache_manager = get_cache_manager()
        # 清除相关缓存
        await cache_manager.invalidate_pattern("jczq_*")
        await cache_manager.invalidate_pattern("recent_matches:*")
        logger.info("已清除竞彩足球相关缓存")
        return {"message": "数据刷新成功"}
    except Exception as e:
        logger.error(f"刷新竞彩足球数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"刷新失败: {str(e)}")