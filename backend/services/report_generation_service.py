from typing import Dict, Any, List
from sqlalchemy.orm import Session
from jinja2 import Template
from ..models.match import Match
from ..models.odds import Odds
from ..services.llm_service import LLMService


class ReportGenerationService:
    def __init__(self, db: Session, llm_service: LLMService):
        self.db = db
        self.llm_service = llm_service
        
    async def generate_match_report(self, match_id: int) -> str:
        """生成比赛分析报告"""
        # 获取比赛数据
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise ValueError(f"Match with id {match_id} not found")
        
        odds_history = self.db.query(Odds).filter(Odds.match_id == match_id).all()
        
        # 准备报告数据
        report_data = {
            "match": match,
            "odds_history": odds_history,
            "prediction_insights": await self.get_prediction_insights(match_id),
            "historical_comparison": await self.get_historical_comparison(match)
        }
        
        # 生成详细分析
        detailed_analysis = await self.generate_detailed_analysis(report_data)
        
        # 使用模板生成最终报告
        template_str = """
# {{ match.league }} - {{ match.home_team }} vs {{ match.away_team }}

**比赛时间**: {{ match.start_time }}
**比分**: {{ match.score_home or '-' }} - {{ match.score_away or '-' }}

## 赔率分析
{% for odd in odds_history %}
- {{ odd.bookmaker }}: 主胜 {{ "%.2f"|format(odd.home_win) }}, 平局 {{ "%.2f"|format(odd.draw) }}, 客胜 {{ "%.2f"|format(odd.away_win) }}
{% endfor %}

## AI分析洞察
{{ detailed_analysis }}

## 历史对比
{% if historical_comparison.summary %}
{{ historical_comparison.summary }}
{% else %}
暂无历史对比数据
{% endif %}
        """.strip()
        
        template = Template(template_str)
        report = template.render(**report_data, detailed_analysis=detailed_analysis)
        
        return report
    
    async def get_prediction_insights(self, match_id: int) -> Dict[str, Any]:
        """获取预测洞察"""
        # 使用LLM分析预测结果
        prompt = f"""
请分析ID为{match_id}的比赛赔率变化趋势和预测模型输出，提供：
1. 赔率变动原因分析
2. 预测模型的置信度评估
3. 可能影响比赛结果的关键因素
4. 投注建议
        """
        
        try:
            insights = self.llm_service.generate_response(prompt, provider="qwen")
            return {"insights": insights}
        except Exception as e:
            return {"insights": f"获取预测洞察时发生错误: {str(e)}"}
    
    async def get_historical_comparison(self, match: Match) -> Dict[str, Any]:
        """获取历史对比数据"""
        # 查询历史交锋记录
        try:
            # 根据主客队查询历史比赛
            home_team = match.home_team
            away_team = match.away_team
            
            # 查询两队历史交锋
            historical_matches = self.db.query(Match).filter(
                ((Match.home_team == home_team) & (Match.away_team == away_team)) |
                ((Match.home_team == away_team) & (Match.away_team == home_team))
            ).order_by(Match.start_time.desc()).limit(5).all()
            
            if not historical_matches:
                return {"summary": f"{home_team} vs {away_team} 暂无历史交锋记录"}
            
            # 统计胜负情况
            home_wins = 0
            away_wins = 0
            draws = 0
            
            for hist_match in historical_matches:
                if hist_match.score_home > hist_match.score_away:
                    if hist_match.home_team == home_team:
                        home_wins += 1
                    else:
                        away_wins += 1
                elif hist_match.score_home < hist_match.score_away:
                    if hist_match.home_team == home_team:
                        away_wins += 1
                    else:
                        home_wins += 1
                else:
                    draws += 1
            
            summary = f"""
两队历史交锋统计（最近5场）：
- {match.home_team} 胜: {home_wins} 场
- {match.away_team} 胜: {away_wins} 场
- 平局: {draws} 场
            """.strip()
            
            return {"summary": summary, "matches": [m.__dict__ for m in historical_matches]}
        except Exception as e:
            return {"summary": f"查询历史数据时发生错误: {str(e)}"}
    
    async def generate_detailed_analysis(self, report_data: Dict[str, Any]) -> str:
        """生成详细分析"""
        try:
            prompt = f"""
基于以下比赛数据，撰写一份专业的分析报告：

比赛信息: {report_data.get('match')}
赔率历史: {[{"bookmaker": o.bookmaker, "home_win": o.home_win, "draw": o.draw, "away_win": o.away_win} for o in report_data.get('odds_history', [])]}

要求：
1. 专业性强，逻辑清晰
2. 包含数据支撑的观点
3. 提供可操作的建议
4. 字数控制在300-500字
            """
            
            analysis = self.llm_service.generate_response(prompt, provider="qwen")
            return analysis
        except Exception as e:
            return f"生成详细分析时发生错误: {str(e)}"