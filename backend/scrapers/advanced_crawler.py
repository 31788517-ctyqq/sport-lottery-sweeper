from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
import random

# 创建日志记录器
logger = logging.getLogger(__name__)

def _generate_mock_data(days_ahead: int = 3) -> List[Dict[str, Any]]:
    """生成模拟比赛数据"""
    matches = []
    current_date = datetime.now()
    
    for i in range(days_ahead):
        match_date = current_date + timedelta(days=i)
        match_time = match_date.strftime("%Y-%m-%d %H:%M")
        
        # 添加几场模拟比赛
        for j in range(3):  # 每天3场比赛
            match = {
                "id": f"mock_{i}_{j}",
                "match_id": f"M{i}{j:02d}",
                "home_team": f"主队 {j+1}",
                "away_team": f"客队 {j+1}",
                "league": "中超联赛",
                "match_time": match_time,
                "status": "未开赛",
                "source": "mock"
            }
            matches.append(match)
    
    return matches

def _generate_popular_matches() -> List[Dict[str, Any]]:
    """生成热门比赛数据"""
    popular_matches = []
    leagues = ['英超', '西甲', '德甲', '意甲', '法甲', '中超', '欧冠']
    teams = [
        '皇马', '巴萨', '拜仁', '多特', '尤文', '国米', '曼联', '曼城', 
        '利物浦', '切尔西', '巴黎', '马竞', '热刺', '阿森纳'
    ]
    
    for i in range(5):  # 生成5场热门比赛
        league = random.choice(leagues)
        home_team = random.choice(teams)
        away_team = random.choice([t for t in teams if t != home_team])
        match_time = (datetime.now() + timedelta(hours=random.randint(1, 72))).strftime("%Y-%m-%d %H:%M")
        
        match = {
            "match_id": f"popular_{i:02d}",
            "home_team": home_team,
            "away_team": away_team,
            "league": league,
            "match_time": match_time,
            "popularity": random.randint(80, 100),
            "odds_home_win": round(random.uniform(1.5, 3.0), 2),
            "odds_draw": round(random.uniform(2.5, 4.0), 2),
            "odds_away_win": round(random.uniform(2.8, 5.0), 2),
            "status": "销售中"
        }
        popular_matches.append(match)
    
    return popular_matches

def _generate_trending_topics() -> List[Dict[str, Any]]:
    """生成趋势话题数据"""
    trending_topics = []
    topics = [
        "欧冠淘汰赛焦点战",
        "英超争冠白热化",
        "西甲国家德比前瞻",
        "德甲拜仁能否卫冕",
        "意甲米兰双雄对决",
        "法甲大巴黎一骑绝尘",
        "中超新赛季开幕",
        "世界杯预选赛亚洲区",
        "欧洲杯备战情况",
        "转会市场最新动态"
    ]
    
    sources = ["竞彩网", "足球报", "体坛周报", "新浪体育", "腾讯体育"]
    
    for i in range(3):  # 生成3个趋势话题
        topic = {
            "id": f"topic_{i:02d}",
            "title": random.choice(topics),
            "source": random.choice(sources),
            "popularity": random.randint(70, 95),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "summary": f"关于{random.choice(topics)}的最新分析和预测"
        }
        trending_topics.append(topic)
    
    return trending_topics

class AdvancedCrawler:
    """高级爬虫类"""
    
    async def crawl_sporttery_matches(self, days_ahead: int = 3) -> List[Dict[str, Any]]:
        """爬取竞彩网比赛数据（简化版本）"""
        logger.info(f"开始爬取未来 {days_ahead} 天的竞彩比赛数据")
        
        try:
            # 目前返回模拟数据，实际实现需要网络请求
            mock_data = _generate_mock_data(days_ahead)
            logger.info(f"成功生成 {len(mock_data)} 条模拟比赛数据")
            return mock_data
            
        except Exception as e:
            logger.error(f"爬取竞彩网比赛数据失败: {str(e)}")
            return []

    async def get_popular_matches(self) -> List[Dict[str, Any]]:
        """获取热门比赛数据"""
        logger.info("获取热门比赛数据")
        try:
            popular_matches = _generate_popular_matches()
            logger.info(f"成功生成 {len(popular_matches)} 条热门比赛数据")
            return popular_matches
        except Exception as e:
            logger.error(f"获取热门比赛数据失败: {str(e)}")
            return []

    async def get_trending_topics(self) -> List[Dict[str, Any]]:
        """获取趋势话题数据"""
        logger.info("获取趋势话题数据")
        try:
            trending_topics = _generate_trending_topics()
            logger.info(f"成功生成 {len(trending_topics)} 个趋势话题数据")
            return trending_topics
        except Exception as e:
            logger.error(f"获取趋势话题数据失败: {str(e)}")
            return []

# 创建全局实例
advanced_crawler = AdvancedCrawler()