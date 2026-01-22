"""
数据分析服务
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import statistics

from ..models.matches import Match
from ..models.odds_companies import OddsCompany
from ..models.sp_records import SPRecord
from ..models.sp_modification_logs import SPModificationLog
from ..schemas.analysis import DistributionAnalysisResponse, VolatilityAnalysisResponse

logger = logging.getLogger(__name__)


class DataAnalysisService:
    """数据分析服务"""
    
    async def analyze_distribution(self, db: Session, filters: Dict[str, Any]) -> DistributionAnalysisResponse:
        """SP值分布统计"""
        try:
            # 构建查询
            query = db.query(SPRecord).join(Match).join(OddsCompany)
            
            # 应用过滤器
            if filters.get('league'):
                query = query.filter(Match.league.contains(filters['league']))
            if filters.get('company_id'):
                query = query.filter(SPRecord.company_id == filters['company_id'])
            if filters.get('handicap_type'):
                query = query.filter(SPRecord.handicap_type == filters['handicap_type'])
            if filters.get('date_from'):
                query = query.filter(SPRecord.recorded_at >= filters['date_from'])
            if filters.get('date_to'):
                query = query.filter(SPRecord.recorded_at <= filters['date_to'])
            
            records = query.all()
            
            if not records:
                return DistributionAnalysisResponse(
                    total_count=0,
                    avg_sp_value=0,
                    min_sp_value=0,
                    max_sp_value=0,
                    distribution={},
                    charts_data={}
                )
            
            # 提取SP值
            sp_values = [float(r.sp_value) for r in records]
            
            # 计算基本统计
            total_count = len(sp_values)
            avg_sp_value = statistics.mean(sp_values)
            min_sp_value = min(sp_values)
            max_sp_value = max(sp_values)
            
            # 分布统计
            distribution = self._calculate_distribution(sp_values)
            
            # 图表数据
            charts_data = self._prepare_charts_data(records, sp_values, filters)
            
            return DistributionAnalysisResponse(
                total_count=total_count,
                avg_sp_value=round(avg_sp_value, 2),
                min_sp_value=min_sp_value,
                max_sp_value=max_sp_value,
                distribution=distribution,
                charts_data=charts_data
            )
            
        except Exception as e:
            logger.error(f"SP值分布分析失败: {str(e)}")
            raise
    
    async def analyze_volatility(self, db: Session, time_before_match: int = 30) -> VolatilityAnalysisResponse:
        """SP值变动分析（临场变盘）"""
        try:
            # 获取最近完成的比赛
            recent_matches = db.query(Match).filter(
                and_(
                    Match.status == 'finished',
                    Match.match_time >= datetime.utcnow() - timedelta(days=7)
                )
            ).all()
            
            volatile_matches = 0
            top_volatile_cases = []
            
            for match in recent_matches:
                # 获取比赛的SP历史
                history = await self._get_match_sp_history(db, match.id)
                
                if len(history) < 2:
                    continue
                
                # 计算波动率
                volatility_score = self._calculate_volatility_score(history, time_before_match)
                
                if volatility_score > 0.2:  # 阈值可调整
                    volatile_matches += 1
                    
                    # 记录高波动案例
                    if len(top_volatile_cases) < 10:
                        max_change = max([abs(item['change_rate']) for item in history])
                        top_volatile_cases.append({
                            "match_id": match.id,
                            "match_info": f"{match.home_team} vs {match.away_team}",
                            "league": match.league,
                            "volatility_score": round(volatility_score, 3),
                            "max_change_rate": round(max_change, 2),
                            "record_count": len(history)
                        })
            
            total_matches = len(recent_matches)
            volatility_rate = (volatile_matches / total_matches * 100) if total_matches > 0 else 0
            
            # 按波动率排序
            top_volatile_cases.sort(key=lambda x: x['volatility_score'], reverse=True)
            
            return VolatilityAnalysisResponse(
                total_matches=total_matches,
                volatile_matches=volatile_matches,
                volatility_rate=round(volatility_rate, 2),
                top_volatile_cases=top_volatile_cases
            )
            
        except Exception as e:
            logger.error(f"SP值变动分析失败: {str(e)}")
            raise
    
    async def compare_companies(self, db: Session, match_ids: List[int] = None) -> Dict[str, Any]:
        """赔率公司对比分析"""
        try:
            # 构建查询
            query = db.query(
                OddsCompany.id,
                OddsCompany.name,
                OddsCompany.short_name,
                func.count(SPRecord.id).label('record_count'),
                func.avg(SPRecord.sp_value).label('avg_sp_value'),
                func.min(SPRecord.sp_value).label('min_sp_value'),
                func.max(SPRecord.sp_value).label('max_sp_value')
            ).join(SPRecord)
            
            if match_ids:
                query = query.filter(SPRecord.match_id.in_(match_ids))
            
            query = query.group_by(OddsCompany.id, OddsCompany.name, OddsCompany.short_name)
            
            results = query.all()
            
            companies = []
            for row in results:
                companies.append({
                    "id": row.id,
                    "name": row.name,
                    "short_name": row.short_name,
                    "record_count": row.record_count,
                    "avg_sp_value": round(float(row.avg_sp_value), 2) if row.avg_sp_value else 0,
                    "min_sp_value": float(row.min_sp_value) if row.min_sp_value else 0,
                    "max_sp_value": float(row.max_sp_value) if row.max_sp_value else 0
                })
            
            # 计算对比指标
            comparison_metrics = self._calculate_comparison_metrics(companies)
            
            # 生成建议
            recommendations = self._generate_company_recommendations(companies, comparison_metrics)
            
            return {
                "companies": companies,
                "comparison_metrics": comparison_metrics,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"赔率公司对比分析失败: {str(e)}")
            raise
    
    async def calculate_correlation(self, db: Session, sp_range: tuple = None, 
                                 result_type: str = None) -> Dict[str, Any]:
        """SP值与赛果关联分析"""
        try:
            # 构建查询
            query = db.query(Match, SPRecord).join(SPRecord)
            
            # 应用SP值范围过滤
            if sp_range and sp_range[0] is not None and sp_range[1] is not None:
                query = query.filter(
                    and_(
                        SPRecord.sp_value >= sp_range[0],
                        SPRecord.sp_value <= sp_range[1]
                    )
                )
            
            # 应用赛果类型过滤
            if result_type:
                if result_type == 'home_win':
                    query = query.filter(Match.home_score > Match.away_score)
                elif result_type == 'away_win':
                    query = query.filter(Match.home_score < Match.away_score)
                elif result_type == 'draw':
                    query = query.filter(Match.home_score == Match.away_score)
            
            results = query.all()
            
            if not results:
                return {
                    "correlation_coefficient": 0,
                    "sample_size": 0,
                    "insights": ["没有足够的数据进行分析"],
                    "confidence_level": 0
                }
            
            # 分析关联
            correlation_data = self._analyze_sp_result_correlation(results, sp_range, result_type)
            
            return correlation_data
            
        except Exception as e:
            logger.error(f"SP值与赛果关联分析失败: {str(e)}")
            raise
    
    async def custom_query(self, db: Session, query: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """自定义查询分析"""
        try:
            # 这里简化处理，实际应用中应该使用安全的查询构建器
            # 防止SQL注入
            
            if query == 'popular_leagues':
                results = db.query(
                    Match.league,
                    func.count(Match.id).label('match_count')
                ).group_by(Match.league).order_by(
                    func.count(Match.id).desc()
                ).limit(10).all()
                
                return {
                    "type": "popular_leagues",
                    "data": [
                        {"league": r.league, "match_count": r.match_count} 
                        for r in results
                    ]
                }
            
            elif query == 'accuracy_by_company':
                # 分析各公司的准确率（需要实际业务规则）
                return {"type": "accuracy_by_company", "data": []}
            
            else:
                return {"error": "不支持的查询类型"}
                
        except Exception as e:
            logger.error(f"自定义查询失败: {str(e)}")
            raise
    
    async def generate_distribution_report(self, db: Session, league: str = None, 
                                        company_id: int = None) -> List[Dict[str, Any]]:
        """生成SP值分布报表"""
        try:
            query = db.query(
                Match.league,
                OddsCompany.name.label('company_name'),
                SPRecord.handicap_type,
                func.count(SPRecord.id).label('count'),
                func.avg(SPRecord.sp_value).label('avg_sp'),
                func.min(SPRecord.sp_value).label('min_sp'),
                func.max(SPRecord.sp_value).label('max_sp')
            ).join(Match).join(OddsCompany)
            
            if league:
                query = query.filter(Match.league.contains(league))
            if company_id:
                query = query.filter(SPRecord.company_id == company_id)
            
            query = query.group_by(
                Match.league, OddsCompany.name, SPRecord.handicap_type
            ).order_by(Match.league, OddsCompany.name)
            
            results = query.all()
            
            report_data = []
            for row in results:
                report_data.append({
                    "league": row.league,
                    "company_name": row.company_name,
                    "handicap_type": row.handicap_type,
                    "count": row.count,
                    "avg_sp": round(float(row.avg_sp), 2),
                    "min_sp": float(row.min_sp),
                    "max_sp": float(row.max_sp)
                })
            
            return report_data
            
        except Exception as e:
            logger.error(f"生成SP值分布报表失败: {str(e)}")
            raise
    
    async def generate_match_analysis_report(self, db: Session, match_ids: List[int] = None) -> List[Dict[str, Any]]:
        """生成比赛分析报表"""
        try:
            query = db.query(Match)
            if match_ids:
                query = query.filter(Match.id.in_(match_ids))
            
            matches = query.all()
            
            report_data = []
            for match in matches:
                # 获取该比赛的SP统计
                sp_stats = db.query(
                    func.avg(SPRecord.sp_value).label('avg_sp'),
                    func.count(SPRecord.id).label('sp_count')
                ).filter(SPRecord.match_id == match.id).first()
                
                report_data.append({
                    "match_id": match.match_id,
                    "home_team": match.home_team,
                    "away_team": match.away_team,
                    "league": match.league,
                    "match_time": match.match_time.isoformat(),
                    "status": match.status,
                    "final_result": match.final_result,
                    "score": f"{match.home_score}:{match.away_score}" if match.home_score is not None else "-",
                    "avg_sp_value": round(float(sp_stats.avg_sp), 2) if sp_stats.avg_sp else 0,
                    "sp_record_count": sp_stats.sp_count or 0
                })
            
            return report_data
            
        except Exception as e:
            logger.error(f"生成比赛分析报表失败: {str(e)}")
            raise
    
    def _calculate_distribution(self, sp_values: List[float]) -> Dict[str, int]:
        """计算SP值分布"""
        distribution = {
            "0.0-1.0": 0,
            "1.0-1.5": 0,
            "1.5-2.0": 0,
            "2.0-3.0": 0,
            "3.0-5.0": 0,
            "5.0+": 0
        }
        
        for value in sp_values:
            if value < 1.0:
                distribution["0.0-1.0"] += 1
            elif value < 1.5:
                distribution["1.0-1.5"] += 1
            elif value < 2.0:
                distribution["1.5-2.0"] += 1
            elif value < 3.0:
                distribution["2.0-3.0"] += 1
            elif value < 5.0:
                distribution["3.0-5.0"] += 1
            else:
                distribution["5.0+"] += 1
        
        return distribution
    
    def _prepare_charts_data(self, records: List[SPRecord], sp_values: List[float], 
                           filters: Dict[str, Any]) -> Dict[str, Any]:
        """准备图表数据"""
        # 按时间分布
        time_series = {}
        for record in records:
            hour = record.recorded_at.strftime('%H:00')
            if hour not in time_series:
                time_series[hour] = []
            time_series[hour].append(float(record.sp_value))
        
        # 计算每小时平均值
        time_chart = {
            hour: round(sum(values) / len(values), 2)
            for hour, values in time_series.items()
        }
        
        return {
            "time_series": time_chart,
            "histogram": self._calculate_distribution(sp_values)
        }
    
    def _get_match_sp_history(self, db: Session, match_id: int) -> List[Dict[str, Any]]:
        """获取单场比赛的SP历史"""
        records = db.query(SPRecord).filter(
            SPRecord.match_id == match_id
        ).order_by(SPRecord.recorded_at).all()
        
        history = []
        prev_value = None
        
        for record in records:
            current_value = float(record.sp_value)
            
            if prev_value is not None:
                change_rate = abs(current_value - prev_value) / prev_value if prev_value > 0 else 0
            else:
                change_rate = 0
            
            history.append({
                "recorded_at": record.recorded_at,
                "sp_value": current_value,
                "change_rate": change_rate
            })
            
            prev_value = current_value
        
        return history
    
    def _calculate_volatility_score(self, history: List[Dict[str, Any]], 
                                  time_before_match: int) -> float:
        """计算波动率评分"""
        if len(history) < 2:
            return 0
        
        # 计算平均变动率
        change_rates = [item['change_rate'] for item in history]
        avg_change = statistics.mean(change_rates)
        
        # 计算标准差
        if len(change_rates) > 1:
            std_dev = statistics.stdev(change_rates)
        else:
            std_dev = 0
        
        # 波动率评分 = 平均变动率 + 标准差权重
        volatility_score = avg_change + (std_dev * 0.5)
        
        return min(volatility_score, 1.0)  # 归一化到0-1
    
    def _calculate_comparison_metrics(self, companies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算公司对比指标"""
        if not companies:
            return {}
        
        # 找出各项指标的极值
        max_count = max([c['record_count'] for c in companies])
        min_avg = min([c['avg_sp_value'] for c in companies])
        max_avg = max([c['avg_sp_value'] for c in companies])
        
        return {
            "most_active_company": next((c for c in companies if c['record_count'] == max_count), None),
            "avg_sp_range": {
                "min": min_avg,
                "max": max_avg,
                "spread": max_avg - min_avg
            },
            "company_count": len(companies)
        }
    
    def _generate_company_recommendations(self, companies: List[Dict[str, Any]], 
                                       metrics: Dict[str, Any]) -> List[str]:
        """生成公司推荐"""
        recommendations = []
        
        if metrics.get('most_active_company'):
            rec = f"最活跃的数据源: {metrics['most_active_company']['name']}，建议优先关注"
            recommendations.append(rec)
        
        if metrics.get('avg_sp_range', {}).get('spread', 0) > 1.0:
            recommendations.append("不同公司的平均SP值差异较大，建议综合分析")
        
        if len(companies) < 3:
            recommendations.append("数据源较少，建议增加更多赔率公司以提高分析准确性")
        
        return recommendations
    
    def _analyze_sp_result_correlation(self, results: List, sp_range: tuple, result_type: str) -> Dict[str, Any]:
        """分析SP值与赛果关联"""
        # 简化的关联分析逻辑
        total_samples = len(results)
        
        # 这里应该实现具体的关联算法
        # 例如：计算SP值与实际赛果的相关系数
        
        insights = [
            f"样本数量: {total_samples}",
            "需要进一步实现具体的关联分析算法"
        ]
        
        return {
            "correlation_coefficient": 0.0,  # 占位符
            "sample_size": total_samples,
            "insights": insights,
            "confidence_level": 0.0
        }