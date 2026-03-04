#!/usr/bin/env python3
"""
对冲策略智能体
基于LangChain构建的对冲机会识别智能体，用于发现和评估投注对冲机会
"""

import logging
import math
from typing import Dict, Any, List, Optional, Tuple
import asyncio
from datetime import datetime, timedelta

from .base_agent import BaseAgent
from ..services.langchain_service import LangChainService, create_preset_chain
from ..services.llm_service import LLMService
from ..services.odds_analysis_service import OddsAnalysisService  # 假设存在赔率分析服务
from ..database import get_db

logger = logging.getLogger(__name__)


class HedgingStrategyAgent(BaseAgent):
    """对冲策略智能体"""
    
    def __init__(
        self, 
        name: str, 
        config: Dict[str, Any],
        langchain_service: Optional[LangChainService] = None,
        odds_analysis_service: Optional[OddsAnalysisService] = None
    ):
        super().__init__(name, config)
        
        # 初始化服务
        self.langchain_service = langchain_service or self._create_langchain_service()
        self.odds_analysis_service = odds_analysis_service or self._create_odds_analysis_service()
        
        # 创建对冲分析链
        self._setup_hedging_chains()
        
        # 对冲策略配置
        self.min_profit_margin = config.get("min_profit_margin", 0.01)  # 最小利润率 1%
        self.max_risk_per_trade = config.get("max_risk_per_trade", 1000)  # 单笔交易最大风险
        self.arbitrage_threshold = config.get("arbitrage_threshold", 0.02)  # 套利阈值 2%
        
        logger.info(f"对冲策略智能体 '{name}' 初始化完成")
    
    def _create_langchain_service(self) -> LangChainService:
        """创建LangChain服务"""
        # 创建LLM服务
        llm_service = LLMService()
        
        # 从配置或环境变量中获取API密钥
        import os
        openai_api_key = self.config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
        qwen_api_key = self.config.get("qwen_api_key") or os.getenv("QWEN_API_KEY")
        gemini_api_key = self.config.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
        
        # 注册提供商（至少需要一个）
        if openai_api_key and openai_api_key != "your-openai-api-key-here":
            llm_service.register_provider("openai", openai_api_key)
            llm_service.set_default_provider("openai")
        elif qwen_api_key and qwen_api_key != "your-qwen-api-key-here":
            llm_service.register_provider("qwen", qwen_api_key)
            llm_service.set_default_provider("qwen")
        elif gemini_api_key and gemini_api_key != "your-gemini-api-key-here":
            llm_service.register_provider("gemini", gemini_api_key)
            llm_service.set_default_provider("gemini")
        else:
            logger.warning("没有配置有效的LLM API密钥，智能体功能可能受限")
        
        # 创建LangChain服务
        return LangChainService(llm_service)
    
    def _create_odds_analysis_service(self) -> "OddsAnalysisService":
        """创建赔率分析服务（模拟实现）"""
        # 这里应该返回实际的OddsAnalysisService实例
        # 由于可能不存在，我们创建一个模拟类
        class MockOddsAnalysisService:
            def find_arbitrage_opportunities(self, odds_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                """查找套利机会"""
                opportunities = []
                for odds in odds_data:
                    # 简单套利检测逻辑
                    implied_prob = 1/odds.get('home_win', 100) + 1/odds.get('draw', 100) + 1/odds.get('away_win', 100)
                    if implied_prob < 0.98:  # 存在套利机会
                        profit_margin = 1 - implied_prob
                        opportunities.append({
                            'match_id': odds.get('match_id'),
                            'bookmaker': odds.get('bookmaker'),
                            'profit_margin': profit_margin,
                            'implied_probability': implied_prob
                        })
                return opportunities
            
            def calculate_hedge_ratios(self, initial_bet: Dict[str, Any], current_odds: Dict[str, Any]) -> Dict[str, Any]:
                """计算对冲比例"""
                # 简单对冲比例计算
                initial_stake = initial_bet.get('stake', 100)
                initial_odds = initial_bet.get('odds', 2.0)
                current_odds_home = current_odds.get('home_win', 2.0)
                current_odds_draw = current_odds.get('draw', 3.0)
                current_odds_away = current_odds.get('away_win', 4.0)
                
                # 计算对冲投注比例
                hedge_stake_home = initial_stake * (initial_odds - 1) / (current_odds_home - 1)
                hedge_stake_draw = initial_stake * (initial_odds - 1) / (current_odds_draw - 1)
                hedge_stake_away = initial_stake * (initial_odds - 1) / (current_odds_away - 1)
                
                return {
                    'hedge_home': hedge_stake_home,
                    'hedge_draw': hedge_stake_draw,
                    'hedge_away': hedge_stake_away,
                    'guaranteed_profit': initial_stake * (initial_odds - 1) - max(hedge_stake_home, hedge_stake_draw, hedge_stake_away)
                }
        
        return MockOddsAnalysisService()
    
    def _setup_hedging_chains(self):
        """设置对冲分析链"""
        try:
            # 创建风险评估链
            self.risk_chain = create_preset_chain(
                self.langchain_service, 
                "risk_assessment", 
                "hedging_risk_chain"
            )
            logger.info("风险评估链创建成功")
        except Exception as e:
            logger.warning(f"创建预设链失败，使用自定义链: {e}")
            # 创建自定义链
            risk_template = """评估以下对冲策略的风险：
策略：{strategy}
市场条件：{market_conditions}
当前赔率：{current_odds}
历史波动率：{historical_volatility}

请分析潜在风险和回报，并提供风险评分（1-10）："""
            
            self.risk_chain = self.langchain_service.create_simple_chain(
                chain_name="hedging_risk_custom",
                template=risk_template,
                input_variables=["strategy", "market_conditions", "current_odds", "historical_volatility"]
            )
        
        # 创建对冲机会识别链
        opportunity_template = """分析以下赔率数据，识别对冲机会：
比赛信息：{match_info}
各家博彩公司赔率：{bookmaker_odds}
市场趋势：{market_trend}

请识别以下类型的对冲机会：
1. 跨平台套利机会
2. 时间序列对冲机会
3. 结果组合对冲机会
4. 风险对冲机会

为每个机会提供：
- 机会类型
- 预期利润率
- 风险等级
- 建议操作
- 执行优先级（1-5）

分析结果："""
        
        self.opportunity_chain = self.langchain_service.create_simple_chain(
            chain_name="hedging_opportunity_chain",
            template=opportunity_template,
            input_variables=["match_info", "bookmaker_odds", "market_trend"]
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行对冲策略分析任务"""
        analysis_type = context.get("analysis_type", "opportunity_scan")
        
        logger.info(f"开始对冲策略分析，类型: {analysis_type}")
        
        try:
            if analysis_type == "opportunity_scan":
                # 机会扫描模式：扫描所有比赛寻找对冲机会
                result = await self._scan_hedging_opportunities(context)
            elif analysis_type == "strategy_analysis":
                # 策略分析模式：分析特定对冲策略
                result = await self._analyze_hedging_strategy(context)
            elif analysis_type == "risk_assessment":
                # 风险评估模式：评估特定对冲操作的风险
                result = await self._assess_hedging_risk(context)
            elif analysis_type == "execution_plan":
                # 执行计划模式：生成对冲操作执行计划
                result = await self._generate_execution_plan(context)
            else:
                return {
                    "success": False,
                    "error": f"不支持的分析类型: {analysis_type}",
                    "supported_types": ["opportunity_scan", "strategy_analysis", "risk_assessment", "execution_plan"]
                }
            
            logger.info(f"对冲策略分析完成，类型: {analysis_type}")
            
            return {
                "success": True,
                "analysis_type": analysis_type,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"对冲策略分析失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "analysis_type": analysis_type
            }
    
    async def _scan_hedging_opportunities(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """扫描对冲机会"""
        # 获取比赛数据
        match_ids = context.get("match_ids", [])
        if not match_ids:
            # 如果没有指定比赛，获取即将开始的比赛
            match_ids = await self._get_upcoming_matches()
        
        opportunities = []
        
        for match_id in match_ids[:10]:  # 限制扫描数量
            try:
                # 获取比赛赔率数据
                odds_data = await self._get_match_odds_data(match_id)
                
                if not odds_data:
                    continue
                
                # 使用传统方法查找套利机会
                arbitrage_ops = self.odds_analysis_service.find_arbitrage_opportunities(odds_data)
                
                # 使用LangChain分析更复杂的对冲机会
                llm_opportunities = await self._analyze_hedging_opportunities_with_llm(match_id, odds_data)
                
                # 合并机会
                match_opportunities = {
                    "match_id": match_id,
                    "arbitrage_opportunities": arbitrage_ops,
                    "llm_identified_opportunities": llm_opportunities,
                    "total_opportunities": len(arbitrage_ops) + len(llm_opportunities)
                }
                
                if match_opportunities["total_opportunities"] > 0:
                    opportunities.append(match_opportunities)
                    
            except Exception as e:
                logger.error(f"扫描比赛 {match_id} 对冲机会失败: {e}")
                continue
        
        # 排序和筛选
        filtered_opportunities = self._filter_and_rank_opportunities(opportunities)
        
        return {
            "scanned_matches": len(match_ids),
            "total_opportunities": sum(opp["total_opportunities"] for opp in opportunities),
            "filtered_opportunities": len(filtered_opportunities),
            "opportunities": filtered_opportunities,
            "scan_summary": self._generate_scan_summary(filtered_opportunities)
        }
    
    async def _analyze_hedging_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析对冲策略"""
        strategy = context.get("strategy", {})
        initial_bet = strategy.get("initial_bet")
        target_profit = strategy.get("target_profit")
        risk_tolerance = strategy.get("risk_tolerance", "medium")
        
        if not initial_bet:
            return {"error": "需要提供初始投注信息"}
        
        # 获取当前赔率
        match_id = initial_bet.get("match_id")
        current_odds = await self._get_current_odds(match_id)
        
        # 计算对冲比例
        hedge_ratios = self.odds_analysis_service.calculate_hedge_ratios(initial_bet, current_odds)
        
        # 使用LangChain进行风险评估
        risk_assessment = await self._assess_strategy_risk_with_llm(
            strategy, current_odds, hedge_ratios
        )
        
        # 生成执行建议
        execution_advice = self._generate_execution_advice(
            hedge_ratios, risk_assessment, target_profit, risk_tolerance
        )
        
        return {
            "hedge_ratios": hedge_ratios,
            "risk_assessment": risk_assessment,
            "execution_advice": execution_advice,
            "profitability_analysis": self._analyze_profitability(hedge_ratios, initial_bet),
            "recommendation": self._generate_strategy_recommendation(hedge_ratios, risk_assessment)
        }
    
    async def _assess_hedging_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """评估对冲风险"""
        operation = context.get("operation", {})
        
        # 准备风险评估数据
        risk_data = {
            "strategy": operation.get("strategy_description", "未知策略"),
            "market_conditions": operation.get("market_conditions", "稳定"),
            "current_odds": str(operation.get("current_odds", {})),
            "historical_volatility": operation.get("historical_volatility", "低")
        }
        
        # 使用LangChain风险评估链
        risk_result = await self.langchain_service.run_chain("hedging_risk_chain", risk_data)
        
        # 解析风险评分
        risk_score = self._extract_risk_score(risk_result.get("result", ""))
        
        # 传统风险指标计算
        traditional_risk = self._calculate_traditional_risk_metrics(operation)
        
        return {
            "llm_risk_assessment": risk_result,
            "risk_score": risk_score,
            "traditional_risk_metrics": traditional_risk,
            "overall_risk_level": self._determine_overall_risk(risk_score, traditional_risk),
            "risk_mitigation_suggestions": self._generate_risk_mitigation_suggestions(risk_score, traditional_risk)
        }
    
    async def _generate_execution_plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行计划"""
        opportunity = context.get("opportunity", {})
        
        # 生成执行步骤
        execution_steps = self._generate_execution_steps(opportunity)
        
        # 时间安排
        timing_plan = self._generate_timing_plan(opportunity)
        
        # 风险管理计划
        risk_plan = self._generate_risk_management_plan(opportunity)
        
        # 监控计划
        monitoring_plan = self._generate_monitoring_plan(opportunity)
        
        return {
            "execution_steps": execution_steps,
            "timing_plan": timing_plan,
            "risk_management_plan": risk_plan,
            "monitoring_plan": monitoring_plan,
            "success_criteria": self._define_success_criteria(opportunity),
            "contingency_plan": self._generate_contingency_plan(opportunity)
        }
    
    async def _get_upcoming_matches(self, limit: int = 20) -> List[int]:
        """获取即将开始的比赛ID"""
        from sqlalchemy.orm import Session
        db = next(get_db())
        
        from ..models.match import Match, MatchStatusEnum
        from datetime import datetime
        
        matches = db.query(Match).filter(
            Match.status == MatchStatusEnum.SCHEDULED,
            Match.match_date >= datetime.now(),
            Match.match_date <= datetime.now() + timedelta(hours=48)
        ).order_by(Match.match_date).limit(limit).all()
        
        return [match.id for match in matches]
    
    async def _get_match_odds_data(self, match_id: int) -> List[Dict[str, Any]]:
        """获取比赛赔率数据"""
        from sqlalchemy.orm import Session
        db = next(get_db())
        
        from ..models.odds import Odds
        odds_records = db.query(Odds).filter(
            Odds.match_id == match_id,
            Odds.odds_type == "match_odds"
        ).all()
        
        return [
            {
                "match_id": o.match_id,
                "bookmaker": o.bookmaker,
                "home_win": o.home_win,
                "draw": o.draw,
                "away_win": o.away_win,
                "timestamp": o.created_at.isoformat() if o.created_at else None,
                "odds_type": o.odds_type
            }
            for o in odds_records
        ]
    
    async def _get_current_odds(self, match_id: int) -> Dict[str, Any]:
        """获取当前最新赔率"""
        odds_data = await self._get_match_odds_data(match_id)
        if odds_data:
            # 取最新的一条记录
            return odds_data[-1]
        return {"home_win": 2.0, "draw": 3.0, "away_win": 4.0}
    
    async def _analyze_hedging_opportunities_with_llm(self, match_id: int, odds_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """使用LangChain分析对冲机会"""
        try:
            # 获取比赛信息
            from sqlalchemy.orm import Session
            db = next(get_db())
            
            from ..models.match import Match
            match = db.query(Match).filter(Match.id == match_id).first()
            
            if not match:
                return []
            
            match_info = {
                "home_team": match.home_team.name if match.home_team else "未知",
                "away_team": match.away_team.name if match.away_team else "未知",
                "league": match.league.name if match.league else "未知",
                "match_date": match.match_date.isoformat() if match.match_date else "未知"
            }
            
            # 准备输入数据
            inputs = {
                "match_info": str(match_info),
                "bookmaker_odds": str(odds_data),
                "market_trend": "稳定"  # 这里可以添加实际的市场趋势分析
            }
            
            # 运行机会识别链
            result = await self.langchain_service.run_chain("hedging_opportunity_chain", inputs)
            
            if result["success"]:
                # 解析结果
                opportunities = self._parse_llm_opportunities(result["result"])
                return opportunities
            else:
                logger.warning(f"LangChain机会识别失败: {result.get('error')}")
                return []
                
        except Exception as e:
            logger.error(f"LangChain机会分析异常: {e}")
            return []
    
    async def _assess_strategy_risk_with_llm(self, strategy: Dict[str, Any], current_odds: Dict[str, Any], hedge_ratios: Dict[str, Any]) -> Dict[str, Any]:
        """使用LangChain评估策略风险"""
        try:
            risk_data = {
                "strategy": str(strategy),
                "market_conditions": "当前市场条件",
                "current_odds": str(current_odds),
                "historical_volatility": "基于历史数据的波动率分析"
            }
            
            result = await self.langchain_service.run_chain("hedging_risk_chain", risk_data)
            return result
        except Exception as e:
            logger.error(f"LangChain风险评估异常: {e}")
            return {"error": str(e), "fallback_risk_score": 5}
    
    def _filter_and_rank_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤和排序机会"""
        filtered = []
        
        for opp in opportunities:
            # 过滤条件：至少有一个机会且利润率超过阈值
            if opp["total_opportunities"] > 0:
                # 计算综合利润率
                total_profit_margin = 0
                count = 0
                
                for arb in opp.get("arbitrage_opportunities", []):
                    total_profit_margin += arb.get("profit_margin", 0)
                    count += 1
                
                if count > 0:
                    avg_profit_margin = total_profit_margin / count
                    if avg_profit_margin >= self.min_profit_margin:
                        opp["avg_profit_margin"] = avg_profit_margin
                        filtered.append(opp)
        
        # 按利润率排序
        filtered.sort(key=lambda x: x.get("avg_profit_margin", 0), reverse=True)
        
        return filtered
    
    def _generate_scan_summary(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成扫描摘要"""
        if not opportunities:
            return {"message": "未发现符合条件的对冲机会"}
        
        total_matches = len(opportunities)
        total_opportunities = sum(opp["total_opportunities"] for opp in opportunities)
        avg_profit_margin = sum(opp.get("avg_profit_margin", 0) for opp in opportunities) / total_matches
        
        return {
            "total_matches_with_opportunities": total_matches,
            "total_opportunities_found": total_opportunities,
            "average_profit_margin": avg_profit_margin,
            "estimated_max_profit": self._estimate_max_profit(opportunities),
            "recommended_actions": self._generate_recommended_actions(opportunities)
        }
    
    def _extract_risk_score(self, risk_text: str) -> int:
        """从文本中提取风险评分"""
        import re
        
        # 尝试匹配数字模式
        score_pattern = r'风险评分[：:]\s*(\d+)'
        match = re.search(score_pattern, risk_text)
        
        if match:
            return int(match.group(1))
        
        # 尝试查找1-10之间的数字
        number_pattern = r'\b([1-9]|10)\b'
        matches = re.findall(number_pattern, risk_text)
        
        if matches:
            return int(matches[0])
        
        return 5  # 默认中等风险
    
    def _calculate_traditional_risk_metrics(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """计算传统风险指标"""
        # 这里实现传统的风险指标计算
        return {
            "var_95": 0.05,  # 95%置信度的风险价值
            "expected_shortfall": 0.08,
            "sharpe_ratio": 1.2,
            "max_drawdown": 0.15,
            "volatility": 0.25
        }
    
    def _determine_overall_risk(self, risk_score: int, traditional_risk: Dict[str, Any]) -> str:
        """确定总体风险等级"""
        if risk_score <= 3 and traditional_risk.get("var_95", 1) < 0.1:
            return "低"
        elif risk_score <= 6 and traditional_risk.get("var_95", 1) < 0.2:
            return "中"
        else:
            return "高"
    
    def _generate_risk_mitigation_suggestions(self, risk_score: int, traditional_risk: Dict[str, Any]) -> List[str]:
        """生成风险缓解建议"""
        suggestions = []
        
        if risk_score >= 7:
            suggestions.append("建议减少仓位规模")
            suggestions.append("考虑增加对冲比例")
            suggestions.append("设置严格的止损点")
        
        if traditional_risk.get("volatility", 0) > 0.3:
            suggestions.append("市场波动性高，建议分批执行")
        
        if traditional_risk.get("max_drawdown", 0) > 0.2:
            suggestions.append("历史最大回撤较大，需谨慎操作")
        
        if not suggestions:
            suggestions.append("风险水平可接受，按计划执行")
        
        return suggestions
    
    def _generate_execution_steps(self, opportunity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成执行步骤"""
        steps = [
            {
                "step": 1,
                "action": "验证机会",
                "description": "重新验证赔率数据和机会有效性",
                "estimated_time": "5分钟",
                "responsible": "系统"
            },
            {
                "step": 2,
                "action": "计算投注金额",
                "description": "根据资金管理和风险承受能力计算具体投注金额",
                "estimated_time": "2分钟",
                "responsible": "系统"
            },
            {
                "step": 3,
                "action": "执行投注",
                "description": "在多个平台执行对冲投注",
                "estimated_time": "10分钟",
                "responsible": "交易员/API"
            },
            {
                "step": 4,
                "action": "确认执行",
                "description": "确认所有投注已成功执行",
                "estimated_time": "5分钟",
                "responsible": "系统"
            },
            {
                "step": 5,
                "action": "监控和调整",
                "description": "监控市场变化，必要时进行调整",
                "estimated_time": "持续",
                "responsible": "监控系统"
            }
        ]
        
        return steps
    
    def _generate_timing_plan(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """生成时间安排"""
        return {
            "start_time": "立即",
            "execution_window": "30分钟",
            "best_execution_time": "市场流动性高时段",
            "deadline": "比赛开始前1小时",
            "monitoring_duration": "直到比赛结束"
        }
    
    def _generate_risk_management_plan(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """生成风险管理计划"""
        return {
            "max_loss": self.max_risk_per_trade,
            "stop_loss_trigger": "单边亏损超过20%",
            "profit_target": "达到预期利润的80%",
            "hedge_adjustment_threshold": "赔率变化超过5%",
            "emergency_protocol": "市场异常时立即平仓"
        }
    
    def _generate_monitoring_plan(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """生成监控计划"""
        return {
            "monitoring_frequency": "每分钟",
            "alert_triggers": ["赔率变化超过3%", "市场异常波动", "流动性下降"],
            "reporting_schedule": ["执行后立即", "每小时", "每日总结"],
            "escalation_procedure": "异常情况自动通知管理员"
        }
    
    def _define_success_criteria(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """定义成功标准"""
        return {
            "profit_target": "实现至少1%的利润率",
            "execution_speed": "所有投注在15分钟内完成",
            "risk_control": "最大回撤不超过10%",
            "completion": "所有投注成功执行并确认"
        }
    
    def _generate_contingency_plan(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """生成应急计划"""
        return {
            "partial_execution": "如果部分投注失败，立即调整剩余投注",
            "market_change": "赔率大幅变化时重新计算对冲比例",
            "system_failure": "系统故障时切换到手动模式",
            "liquidity_issue": "流动性不足时减少仓位规模"
        }
    
    def _parse_llm_opportunities(self, llm_output: str) -> List[Dict[str, Any]]:
        """解析LLM输出的机会"""
        opportunities = []
        
        # 简单解析逻辑（实际应更复杂）
        lines = llm_output.split('\n')
        current_opportunity = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('机会类型:'):
                if current_opportunity:
                    opportunities.append(current_opportunity)
                current_opportunity = {"type": line.replace('机会类型:', '').strip()}
            elif line.startswith('预期利润率:'):
                current_opportunity["expected_profit"] = line.replace('预期利润率:', '').strip()
            elif line.startswith('风险等级:'):
                current_opportunity["risk_level"] = line.replace('风险等级:', '').strip()
            elif line.startswith('建议操作:'):
                current_opportunity["suggestion"] = line.replace('建议操作:', '').strip()
            elif line.startswith('执行优先级:'):
                current_opportunity["priority"] = line.replace('执行优先级:', '').strip()
        
        if current_opportunity:
            opportunities.append(current_opportunity)
        
        return opportunities
    
    def _generate_execution_advice(self, hedge_ratios: Dict[str, Any], risk_assessment: Dict[str, Any], 
                                  target_profit: Optional[float], risk_tolerance: str) -> Dict[str, Any]:
        """生成执行建议"""
        guaranteed_profit = hedge_ratios.get('guaranteed_profit', 0)
        
        advice = {
            "recommended_action": "执行对冲" if guaranteed_profit > 0 else "放弃对冲",
            "reason": f"保证利润: {guaranteed_profit:.2f}" if guaranteed_profit > 0 else "无保证利润",
            "hedge_amounts": {
                "home": hedge_ratios.get('hedge_home', 0),
                "draw": hedge_ratios.get('hedge_draw', 0),
                "away": hedge_ratios.get('hedge_away', 0)
            },
            "risk_adjustment": self._adjust_for_risk_tolerance(hedge_ratios, risk_tolerance)
        }
        
        if target_profit and guaranteed_profit < target_profit:
            advice["note"] = f"保证利润({guaranteed_profit:.2f})低于目标利润({target_profit:.2f})"
        
        return advice
    
    def _adjust_for_risk_tolerance(self, hedge_ratios: Dict[str, Any], risk_tolerance: str) -> Dict[str, Any]:
        """根据风险承受能力调整"""
        adjustment_factor = {
            "low": 0.7,
            "medium": 1.0,
            "high": 1.3
        }.get(risk_tolerance, 1.0)
        
        return {
            "adjusted_home": hedge_ratios.get('hedge_home', 0) * adjustment_factor,
            "adjusted_draw": hedge_ratios.get('hedge_draw', 0) * adjustment_factor,
            "adjusted_away": hedge_ratios.get('hedge_away', 0) * adjustment_factor
        }
    
    def _analyze_profitability(self, hedge_ratios: Dict[str, Any], initial_bet: Dict[str, Any]) -> Dict[str, Any]:
        """分析盈利能力"""
        guaranteed_profit = hedge_ratios.get('guaranteed_profit', 0)
        initial_stake = initial_bet.get('stake', 100)
        
        return {
            "guaranteed_profit": guaranteed_profit,
            "roi": (guaranteed_profit / initial_stake) * 100 if initial_stake > 0 else 0,
            "break_even_point": "已保证盈利" if guaranteed_profit > 0 else "无保证",
            "profit_distribution": self._calculate_profit_distribution(hedge_ratios, initial_bet)
        }
    
    def _calculate_profit_distribution(self, hedge_ratios: Dict[str, Any], initial_bet: Dict[str, Any]) -> Dict[str, Any]:
        """计算利润分布"""
        return {
            "if_home_wins": "待计算",
            "if_draw": "待计算",
            "if_away_wins": "待计算"
        }
    
    def _generate_strategy_recommendation(self, hedge_ratios: Dict[str, Any], risk_assessment: Dict[str, Any]) -> str:
        """生成策略推荐"""
        guaranteed_profit = hedge_ratios.get('guaranteed_profit', 0)
        
        if guaranteed_profit <= 0:
            return "不推荐执行对冲策略"
        elif guaranteed_profit < self.max_risk_per_trade * 0.01:
            return "谨慎执行，利润较低"
        elif guaranteed_profit < self.max_risk_per_trade * 0.03:
            return "推荐执行，中等利润"
        else:
            return "强烈推荐执行，高利润机会"
    
    def _estimate_max_profit(self, opportunities: List[Dict[str, Any]]) -> float:
        """估计最大利润"""
        max_profit = 0
        for opp in opportunities:
            avg_margin = opp.get("avg_profit_margin", 0)
            # 假设每场比赛投注1000元
            max_profit += avg_margin * 1000
        return max_profit
    
    def _generate_recommended_actions(self, opportunities: List[Dict[str, Any]]) -> List[str]:
        """生成推荐操作"""
        actions = []
        
        if opportunities:
            top_match = opportunities[0]
            if top_match.get("avg_profit_margin", 0) > 0.05:
                actions.append(f"重点关注比赛 {top_match.get('match_id')}，利润率高达{top_match.get('avg_profit_margin', 0):.1%}")
            
            if len(opportunities) >= 3:
                actions.append("发现多个机会，建议分散投资以降低风险")
            
            actions.append("执行前务必验证赔率数据的实时性")
        
        return actions or ["暂无特别建议"]


# 工厂函数
def create_hedging_strategy_agent(
    name: str = "hedging_strategy_agent",
    config: Optional[Dict[str, Any]] = None
) -> HedgingStrategyAgent:
    """创建对冲策略智能体"""
    default_config = {
        "agent_type": "business",
        "description": "对冲策略智能体，识别和评估投注对冲机会",
        "enabled": True,
        "max_concurrent": 2,
        "timeout": 600,
        "min_profit_margin": 0.01,
        "max_risk_per_trade": 1000,
        "arbitrage_threshold": 0.02,
        "openai_api_key": None,
        "qwen_api_key": None,
        "gemini_api_key": None
    }
    
    if config:
        default_config.update(config)
    
    return HedgingStrategyAgent(name, default_config)