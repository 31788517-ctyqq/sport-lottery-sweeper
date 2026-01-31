import asyncio
from typing import Dict, Any
from .base_agent import BaseAgent
from ..services.hedge_service import HedgeService
from ..models.match import MatchOdds

class OddsMonitorAgent(BaseAgent):
    def __init__(self, name: str, config: Dict[str, Any], hedge_service: HedgeService):
        super().__init__(name, config)
        self.hedge_service = hedge_service
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 获取最新赔率数据
        latest_odds = await self.fetch_latest_odds()
        
        # 检查是否存在套利机会
        arbitrage_opportunities = self.find_arbitrage_opportunities(latest_odds)
        
        if arbitrage_opportunities:
            # 执行对冲策略
            results = await self.execute_hedge(arbitrage_opportunities)
            return {
                "status": "executed", 
                "opportunities_found": len(arbitrage_opportunities), 
                "results": results
            }
        else:
            return {"status": "no_opportunities"}
    
    async def fetch_latest_odds(self) -> list:
        # 实现赔率获取逻辑
        # 这里需要根据实际的赔率数据获取方式进行实现
        from ..crud.odds_crud import get_latest_odds
        from ..database import SessionLocal
        
        db = SessionLocal()
        try:
            latest_odds = get_latest_odds(db)
            return latest_odds
        finally:
            db.close()
    
    def find_arbitrage_opportunities(self, odds: list) -> list:
        # 实现套利机会查找逻辑
        opportunities = []
        
        # 简单的套利检测逻辑：检查是否存在三个赔率的倒数之和小于1的情况
        for odd in odds:
            try:
                home_win_prob = 1.0 / odd.home_win
                draw_prob = 1.0 / odd.draw
                away_win_prob = 1.0 / odd.away_win
                
                total_probability = home_win_prob + draw_prob + away_win_prob
                
                # 如果总概率小于1，则存在套利机会
                if total_probability < 1.0:
                    profit_margin = (1 - total_probability) * 100
                    threshold = self.config.get("threshold", 0.02)  # 默认2%套利阈值
                    
                    if profit_margin > threshold:
                        opportunities.append({
                            "match_id": odd.match_id,
                            "bookmaker": odd.bookmaker,
                            "home_win": odd.home_win,
                            "draw": odd.draw,
                            "away_win": odd.away_win,
                            "profit_margin": profit_margin
                        })
            except ZeroDivisionError:
                # 如果某个赔率为0，跳过这个记录
                continue
        
        return opportunities
    
    async def execute_hedge(self, opportunities: list) -> list:
        # 执行对冲策略
        return await self.hedge_service.process_opportunities(opportunities)