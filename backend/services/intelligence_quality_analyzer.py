"""
情报质量分析器
提供高级情报质量分析功能，包括多维质量评估、趋势分析和改进建议
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, extract

from ..models.intelligence import (
    Intelligence, IntelligenceType, IntelligenceSource, IntelligenceAnalytics,
    ConfidenceLevelEnum, ImportanceLevelEnum
)
from ..models.match import Match
from ..models.team import Team
from ..models.player import Player


class QualityDimension(Enum):
    """质量维度枚举"""
    COMPLETENESS = "completeness"      # 完整性
    ACCURACY = "accuracy"              # 准确性
    TIMELINESS = "timeliness"          # 及时性
    RELEVANCE = "relevance"            # 相关性
    CONSISTENCY = "consistency"        # 一致性
    USABILITY = "usability"            # 可用性


class QualityLevel(Enum):
    """质量等级枚举"""
    EXCELLENT = "excellent"    # 优秀 (90-100)
    GOOD = "good"              # 良好 (75-89)
    FAIR = "fair"              # 一般 (60-74)
    POOR = "poor"              # 较差 (40-59)
    UNACCEPTABLE = "unacceptable"  # 不可接受 (0-39)


@dataclass
class QualityMetric:
    """质量指标数据类"""
    dimension: QualityDimension
    score: float  # 0-100
    weight: float  # 0-1，表示该维度在总体质量中的权重
    indicators: Dict[str, Any]  # 详细指标数据


@dataclass
class QualityAnalysisResult:
    """质量分析结果数据类"""
    period_days: int
    total_items: int
    overall_score: float  # 0-100
    quality_level: QualityLevel
    dimension_scores: Dict[str, float]  # 各维度得分
    detailed_metrics: List[QualityMetric]
    trends: Dict[str, List[float]]  # 趋势数据
    recommendations: List[str]
    risk_factors: List[str]
    improvement_targets: List[str]


class IntelligenceQualityAnalyzer:
    """
    情报质量分析器
    提供全面的情报质量评估和分析功能
    """
    
    # 默认维度权重
    DEFAULT_DIMENSION_WEIGHTS = {
        QualityDimension.COMPLETENESS: 0.20,
        QualityDimension.ACCURACY: 0.25,
        QualityDimension.TIMELINESS: 0.20,
        QualityDimension.RELEVANCE: 0.15,
        QualityDimension.CONSISTENCY: 0.10,
        QualityDimension.USABILITY: 0.10,
    }
    
    def __init__(self, db_session: Session):
        """
        初始化分析器
        
        Args:
            db_session: 数据库会话
        """
        self.db = db_session
    
    def analyze_period(self, days: int = 7, 
                      dimension_weights: Optional[Dict[QualityDimension, float]] = None) -> QualityAnalysisResult:
        """
        分析指定时间范围内的情报质量
        
        Args:
            days: 分析天数
            dimension_weights: 自定义维度权重，如果为None则使用默认权重
            
        Returns:
            QualityAnalysisResult: 质量分析结果
        """
        # 计算日期范围
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 获取分析数据
        intelligence_list = self._get_intelligence_in_period(start_date, end_date)
        
        if not intelligence_list:
            return self._create_empty_result(days)
        
        # 计算各维度质量指标
        dimension_metrics = self._calculate_dimension_metrics(intelligence_list, dimension_weights)
        
        # 计算总体得分
        overall_score = self._calculate_overall_score(dimension_metrics)
        
        # 确定质量等级
        quality_level = self._determine_quality_level(overall_score)
        
        # 分析趋势
        trends = self._analyze_trends(start_date, end_date, days)
        
        # 生成建议
        recommendations = self._generate_recommendations(dimension_metrics, overall_score)
        
        # 识别风险因素
        risk_factors = self._identify_risk_factors(dimension_metrics)
        
        # 制定改进目标
        improvement_targets = self._create_improvement_targets(dimension_metrics)
        
        # 构建结果
        return QualityAnalysisResult(
            period_days=days,
            total_items=len(intelligence_list),
            overall_score=overall_score,
            quality_level=quality_level,
            dimension_scores={dim.value: metric.score for dim, metric in dimension_metrics.items()},
            detailed_metrics=list(dimension_metrics.values()),
            trends=trends,
            recommendations=recommendations,
            risk_factors=risk_factors,
            improvement_targets=improvement_targets
        )
    
    def analyze_by_source(self, source_id: int, days: int = 7) -> QualityAnalysisResult:
        """
        按数据源分析情报质量
        
        Args:
            source_id: 数据源ID
            days: 分析天数
            
        Returns:
            QualityAnalysisResult: 质量分析结果
        """
        # 计算日期范围
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 获取指定数据源的情报
        intelligence_list = self.db.query(Intelligence).filter(
            and_(
                Intelligence.created_at >= start_date,
                Intelligence.source_id == source_id
            )
        ).all()
        
        if not intelligence_list:
            return self._create_empty_result(days)
        
        # 计算质量指标
        dimension_metrics = self._calculate_dimension_metrics(intelligence_list)
        overall_score = self._calculate_overall_score(dimension_metrics)
        quality_level = self._determine_quality_level(overall_score)
        
        # 生成数据源特定的建议
        source = self.db.query(IntelligenceSource).filter(IntelligenceSource.id == source_id).first()
        source_name = source.name if source else f"数据源{source_id}"
        
        recommendations = self._generate_source_specific_recommendations(
            dimension_metrics, overall_score, source_name, source.reliability_score if source else 0.5
        )
        
        # 构建结果
        return QualityAnalysisResult(
            period_days=days,
            total_items=len(intelligence_list),
            overall_score=overall_score,
            quality_level=quality_level,
            dimension_scores={dim.value: metric.score for dim, metric in dimension_metrics.items()},
            detailed_metrics=list(dimension_metrics.values()),
            trends={},  # 简化版本，不包含趋势
            recommendations=recommendations,
            risk_factors=self._identify_risk_factors(dimension_metrics),
            improvement_targets=self._create_improvement_targets(dimension_metrics)
        )
    
    def compare_sources(self, source_ids: List[int], days: int = 7) -> Dict[str, Any]:
        """
        比较多个数据源的质量
        
        Args:
            source_ids: 数据源ID列表
            days: 分析天数
            
        Returns:
            Dict[str, Any]: 比较结果
        """
        comparison_results = {}
        
        for source_id in source_ids:
            result = self.analyze_by_source(source_id, days)
            source = self.db.query(IntelligenceSource).filter(IntelligenceSource.id == source_id).first()
            source_name = source.name if source else f"数据源{source_id}"
            
            comparison_results[source_name] = {
                "overall_score": result.overall_score,
                "quality_level": result.quality_level.value,
                "total_items": result.total_items,
                "dimension_scores": result.dimension_scores,
                "risk_factors": result.risk_factors
            }
        
        # 排序（按总体得分降序）
        sorted_results = dict(sorted(
            comparison_results.items(),
            key=lambda x: x[1]["overall_score"],
            reverse=True
        ))
        
        # 计算统计数据
        scores = [data["overall_score"] for data in sorted_results.values()]
        if scores:
            stats = {
                "average_score": statistics.mean(scores),
                "median_score": statistics.median(scores),
                "min_score": min(scores),
                "max_score": max(scores),
                "score_range": max(scores) - min(scores)
            }
        else:
            stats = {}
        
        return {
            "comparison": sorted_results,
            "statistics": stats,
            "best_source": next(iter(sorted_results)) if sorted_results else None,
            "worst_source": next(reversed(sorted_results)) if sorted_results else None
        }
    
    def predict_quality_trend(self, days: int = 30) -> Dict[str, Any]:
        """
        预测质量趋势
        
        Args:
            days: 预测天数
            
        Returns:
            Dict[str, Any]: 趋势预测结果
        """
        # 获取历史数据
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days * 2)  # 使用两倍天数获取足够历史数据
        
        # 按天分组计算历史得分
        daily_scores = []
        for i in range(days * 2):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_intelligence = self.db.query(Intelligence).filter(
                and_(
                    Intelligence.created_at >= day_start,
                    Intelligence.created_at < day_end
                )
            ).all()
            
            if day_intelligence:
                metrics = self._calculate_dimension_metrics(day_intelligence)
                score = self._calculate_overall_score(metrics)
                daily_scores.append({
                    "date": day_start.date(),
                    "score": score,
                    "count": len(day_intelligence)
                })
        
        if len(daily_scores) < 7:  # 数据不足
            return {
                "prediction_available": False,
                "message": "历史数据不足，无法进行趋势预测",
                "historical_data": daily_scores
            }
        
        # 简单移动平均预测（实际应用中可使用更复杂的模型）
        recent_scores = [item["score"] for item in daily_scores[-7:]]  # 最近7天
        avg_score = statistics.mean(recent_scores)
        
        # 计算趋势方向
        if len(daily_scores) >= 14:
            first_half_avg = statistics.mean([item["score"] for item in daily_scores[-14:-7]])
            second_half_avg = statistics.mean(recent_scores)
            trend = "improving" if second_half_avg > first_half_avg else "declining"
            trend_strength = abs(second_half_avg - first_half_avg)
        else:
            trend = "stable"
            trend_strength = 0.0
        
        # 生成预测
        prediction_dates = []
        predicted_scores = []
        
        for i in range(1, 8):  # 预测未来7天
            pred_date = end_date + timedelta(days=i)
            prediction_dates.append(pred_date.date())
            
            # 基于当前趋势的简单预测
            if trend == "improving":
                predicted_score = min(100, avg_score + trend_strength * i / 7)
            elif trend == "declining":
                predicted_score = max(0, avg_score - trend_strength * i / 7)
            else:
                predicted_score = avg_score
            
            predicted_scores.append(predicted_score)
        
        return {
            "prediction_available": True,
            "historical_average": avg_score,
            "trend": trend,
            "trend_strength": trend_strength,
            "prediction_dates": [d.isoformat() for d in prediction_dates],
            "predicted_scores": predicted_scores,
            "confidence_interval": self._calculate_confidence_interval(recent_scores),
            "historical_data": daily_scores[-14:] if len(daily_scores) >= 14 else daily_scores
        }
    
    def _get_intelligence_in_period(self, start_date: datetime, end_date: datetime) -> List[Intelligence]:
        """获取指定时间范围内的情报数据"""
        return self.db.query(Intelligence).filter(
            and_(
                Intelligence.created_at >= start_date,
                Intelligence.created_at < end_date,
                Intelligence.status == "active"  # 只分析活跃情报
            )
        ).all()
    
    def _calculate_dimension_metrics(self, intelligence_list: List[Intelligence],
                                   dimension_weights: Optional[Dict[QualityDimension, float]] = None) -> Dict[QualityDimension, QualityMetric]:
        """计算各维度质量指标"""
        weights = dimension_weights or self.DEFAULT_DIMENSION_WEIGHTS
        
        metrics = {}
        
        for dimension in QualityDimension:
            if dimension == QualityDimension.COMPLETENESS:
                score, indicators = self._calculate_completeness_score(intelligence_list)
            elif dimension == QualityDimension.ACCURACY:
                score, indicators = self._calculate_accuracy_score(intelligence_list)
            elif dimension == QualityDimension.TIMELINESS:
                score, indicators = self._calculate_timeliness_score(intelligence_list)
            elif dimension == QualityDimension.RELEVANCE:
                score, indicators = self._calculate_relevance_score(intelligence_list)
            elif dimension == QualityDimension.CONSISTENCY:
                score, indicators = self._calculate_consistency_score(intelligence_list)
            elif dimension == QualityDimension.USABILITY:
                score, indicators = self._calculate_usability_score(intelligence_list)
            else:
                score, indicators = 0.0, {}
            
            metrics[dimension] = QualityMetric(
                dimension=dimension,
                score=score,
                weight=weights[dimension],
                indicators=indicators
            )
        
        return metrics
    
    def _calculate_completeness_score(self, intelligence_list: List[Intelligence]) -> Tuple[float, Dict[str, Any]]:
        """计算完整性得分"""
        if not intelligence_list:
            return 0.0, {}
        
        total_items = len(intelligence_list)
        
        # 检查关键字段完整性
        fields_to_check = ["content", "title", "type_id", "source_id"]
        completeness_counts = {field: 0 for field in fields_to_check}
        
        for intel in intelligence_list:
            for field in fields_to_check:
                if getattr(intel, field):
                    completeness_counts[field] += 1
        
        # 计算字段完整率
        field_rates = {}
        for field in fields_to_check:
            rate = completeness_counts[field] / total_items * 100
            field_rates[f"{field}_completeness_rate"] = round(rate, 2)
        
        # 总体完整性得分（各字段平均）
        overall_score = statistics.mean(list(field_rates.values()))
        
        indicators = {
            "total_items": total_items,
            "field_completeness_rates": field_rates,
            "items_with_all_fields": sum(
                1 for intel in intelligence_list
                if all(getattr(intel, field) for field in fields_to_check)
            )
        }
        
        return round(overall_score, 2), indicators
    
    def _calculate_accuracy_score(self, intelligence_list: List[Intelligence]) -> Tuple[float, Dict[str, Any]]:
        """计算准确性得分"""
        if not intelligence_list:
            return 0.0, {}
        
        # 基于置信度和验证状态计算准确性
        total_items = len(intelligence_list)
        
        # 置信度得分
        confidence_scores = []
        for intel in intelligence_list:
            if hasattr(intel, 'confidence_score'):
                confidence_scores.append(intel.confidence_score * 100)
            else:
                # 根据置信度枚举估算
                confidence_map = {
                    ConfidenceLevelEnum.VERY_LOW: 20,
                    ConfidenceLevelEnum.LOW: 40,
                    ConfidenceLevelEnum.MEDIUM: 60,
                    ConfidenceLevelEnum.HIGH: 80,
                    ConfidenceLevelEnum.VERY_HIGH: 90,
                    ConfidenceLevelEnum.CONFIRMED: 100
                }
                score = confidence_map.get(intel.confidence, 60)
                confidence_scores.append(score)
        
        avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0
        
        # 验证状态得分
        verified_count = sum(1 for intel in intelligence_list if intel.is_verified)
        verification_rate = (verified_count / total_items) * 100
        
        # 来源可信度得分
        source_scores = []
        for intel in intelligence_list:
            if intel.source_info and hasattr(intel.source_info, 'reliability_score'):
                source_scores.append(intel.source_info.reliability_score * 100)
            else:
                source_scores.append(60)  # 默认值
        
        avg_source_score = statistics.mean(source_scores) if source_scores else 0
        
        # 综合准确性得分
        accuracy_score = (avg_confidence * 0.4 + verification_rate * 0.4 + avg_source_score * 0.2)
        
        indicators = {
            "total_items": total_items,
            "average_confidence_score": round(avg_confidence, 2),
            "verification_rate": round(verification_rate, 2),
            "average_source_reliability": round(avg_source_score, 2),
            "verified_items": verified_count
        }
        
        return round(accuracy_score, 2), indicators
    
    def _calculate_timeliness_score(self, intelligence_list: List[Intelligence]) -> Tuple[float, Dict[str, Any]]:
        """计算及时性得分"""
        if not intelligence_list:
            return 0.0, {}
        
        total_items = len(intelligence_list)
        now = datetime.utcnow()
        
        # 计算发布时间分布
        time_scores = []
        recent_items = 0
        
        for intel in intelligence_list:
            if intel.published_at:
                hours_since_publish = (now - intel.published_at).total_seconds() / 3600
                
                # 时间衰减得分（24小时内满分，随时间递减）
                if hours_since_publish <= 1:
                    time_score = 100  # 1小时内
                elif hours_since_publish <= 6:
                    time_score = 90   # 6小时内
                elif hours_since_publish <= 24:
                    time_score = 80   # 24小时内
                elif hours_since_publish <= 72:
                    time_score = 60   # 3天内
                else:
                    time_score = 40   # 超过3天
                
                time_scores.append(time_score)
                
                if hours_since_publish <= 24:
                    recent_items += 1
        
        avg_time_score = statistics.mean(time_scores) if time_scores else 0
        freshness_rate = (recent_items / total_items) * 100
        
        # 综合及时性得分
        timeliness_score = (avg_time_score * 0.6 + freshness_rate * 0.4)
        
        indicators = {
            "total_items": total_items,
            "average_time_score": round(avg_time_score, 2),
            "freshness_rate": round(freshness_rate, 2),
            "recent_items_24h": recent_items,
            "items_by_recency": {
                "within_1h": sum(1 for intel in intelligence_list 
                                if intel.published_at and 
                                (now - intel.published_at).total_seconds() / 3600 <= 1),
                "within_6h": sum(1 for intel in intelligence_list 
                                if intel.published_at and 
                                1 < (now - intel.published_at).total_seconds() / 3600 <= 6),
                "within_24h": sum(1 for intel in intelligence_list 
                                 if intel.published_at and 
                                 6 < (now - intel.published_at).total_seconds() / 3600 <= 24),
                "within_72h": sum(1 for intel in intelligence_list 
                                 if intel.published_at and 
                                 24 < (now - intel.published_at).total_seconds() / 3600 <= 72),
                "older_than_72h": sum(1 for intel in intelligence_list 
                                     if intel.published_at and 
                                     (now - intel.published_at).total_seconds() / 3600 > 72)
            }
        }
        
        return round(timeliness_score, 2), indicators
    
    def _calculate_relevance_score(self, intelligence_list: List[Intelligence]) -> Tuple[float, Dict[str, Any]]:
        """计算相关性得分"""
        if not intelligence_list:
            return 0.0, {}
        
        total_items = len(intelligence_list)
        
        # 基于重要性计算相关性
        importance_scores = []
        for intel in intelligence_list:
            importance_map = {
                ImportanceLevelEnum.LOW: 40,
                ImportanceLevelEnum.MEDIUM: 60,
                ImportanceLevelEnum.HIGH: 80,
                ImportanceLevelEnum.CRITICAL: 100
            }
            score = importance_map.get(intel.importance, 60)
            importance_scores.append(score)
        
        avg_importance = statistics.mean(importance_scores) if importance_scores else 0
        
        # 基于权重计算相关性
        weight_scores = [intel.calculated_weight * 100 for intel in intelligence_list if hasattr(intel, 'calculated_weight')]
        avg_weight = statistics.mean(weight_scores) if weight_scores else 0
        
        # 基于匹配度计算相关性（假设有相关字段）
        match_relevance = 70  # 默认值，实际应用中可根据业务逻辑计算
        
        # 综合相关性得分
        relevance_score = (avg_importance * 0.4 + avg_weight * 0.4 + match_relevance * 0.2)
        
        indicators = {
            "total_items": total_items,
            "average_importance_score": round(avg_importance, 2),
            "average_weight_score": round(avg_weight, 2),
            "high_importance_items": sum(1 for intel in intelligence_list 
                                        if intel.importance in [ImportanceLevelEnum.HIGH, ImportanceLevelEnum.CRITICAL]),
            "weight_distribution": self._calculate_weight_distribution(intelligence_list)
        }
        
        return round(relevance_score, 2), indicators
    
    def _calculate_consistency_score(self, intelligence_list: List[Intelligence]) -> Tuple[float, Dict[str, Any]]:
        """计算一致性得分"""
        if not intelligence_list:
            return 0.0, {}
        
        # 计算字段一致性（例如，相同类型的情报应有相似的结构）
        # 简化版本：基于数据完整性和格式一致性
        
        # 检查重复情报
        duplicate_count = sum(1 for intel in intelligence_list if intel.is_duplicate)
        duplicate_rate = (duplicate_count / len(intelligence_list)) * 100
        
        # 格式一致性检查（简化）
        consistent_format_count = sum(
            1 for intel in intelligence_list
            if intel.content and len(intel.content) > 10  # 简单的内容长度检查
        )
        format_consistency_rate = (consistent_format_count / len(intelligence_list)) * 100
        
        # 一致性得分（越低重复率，越高格式一致性越好）
        consistency_score = max(0, 100 - duplicate_rate * 0.7 + format_consistency_rate * 0.3)
        
        indicators = {
            "total_items": len(intelligence_list),
            "duplicate_rate": round(duplicate_rate, 2),
            "duplicate_items": duplicate_count,
            "format_consistency_rate": round(format_consistency_rate, 2),
            "consistent_format_items": consistent_format_count
        }
        
        return round(consistency_score, 2), indicators
    
    def _calculate_usability_score(self, intelligence_list: List[Intelligence]) -> Tuple[float, Dict[str, Any]]:
        """计算可用性得分"""
        if not intelligence_list:
            return 0.0, {}
        
        total_items = len(intelligence_list)
        
        # 基于热门度计算可用性
        popularity_scores = []
        for intel in intelligence_list:
            if hasattr(intel, 'popularity_score'):
                popularity_scores.append(min(intel.popularity_score * 100, 100))
            else:
                popularity_scores.append(50)  # 默认值
        
        avg_popularity = statistics.mean(popularity_scores) if popularity_scores else 0
        
        # 互动率计算
        interactive_items = sum(
            1 for intel in intelligence_list
            if (hasattr(intel, 'view_count') and intel.view_count > 0) or
               (hasattr(intel, 'like_count') and intel.like_count > 0) or
               (hasattr(intel, 'comment_count') and intel.comment_count > 0)
        )
        interaction_rate = (interactive_items / total_items) * 100
        
        # 摘要质量（简化）
        has_summary_count = sum(1 for intel in intelligence_list if intel.summary)
        summary_rate = (has_summary_count / total_items) * 100
        
        # 综合可用性得分
        usability_score = (avg_popularity * 0.5 + interaction_rate * 0.3 + summary_rate * 0.2)
        
        indicators = {
            "total_items": total_items,
            "average_popularity_score": round(avg_popularity, 2),
            "interaction_rate": round(interaction_rate, 2),
            "summary_rate": round(summary_rate, 2),
            "interactive_items": interactive_items,
            "items_with_summary": has_summary_count
        }
        
        return round(usability_score, 2), indicators
    
    def _calculate_overall_score(self, dimension_metrics: Dict[QualityDimension, QualityMetric]) -> float:
        """计算总体质量得分"""
        weighted_sum = 0
        total_weight = 0
        
        for dimension, metric in dimension_metrics.items():
            weighted_sum += metric.score * metric.weight
            total_weight += metric.weight
        
        if total_weight == 0:
            return 0.0
        
        overall_score = weighted_sum / total_weight
        return round(overall_score, 2)
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """根据得分确定质量等级"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.FAIR
        elif score >= 40:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE
    
    def _analyze_trends(self, start_date: datetime, end_date: datetime, days: int) -> Dict[str, List[float]]:
        """分析质量趋势"""
        # 按天计算趋势
        trends = {
            "dates": [],
            "overall_scores": [],
            "completeness_scores": [],
            "accuracy_scores": [],
            "timeliness_scores": []
        }
        
        # 如果天数太多，按周分组
        if days > 30:
            interval = 7  # 周
        else:
            interval = 1  # 天
        
        current_date = start_date
        while current_date < end_date:
            period_end = min(current_date + timedelta(days=interval), end_date)
            
            # 获取该时间段的数据
            period_intelligence = self.db.query(Intelligence).filter(
                and_(
                    Intelligence.created_at >= current_date,
                    Intelligence.created_at < period_end,
                    Intelligence.status == "active"
                )
            ).all()
            
            if period_intelligence:
                metrics = self._calculate_dimension_metrics(period_intelligence)
                overall_score = self._calculate_overall_score(metrics)
                
                trends["dates"].append(current_date.strftime("%Y-%m-%d"))
                trends["overall_scores"].append(overall_score)
                trends["completeness_scores"].append(metrics[QualityDimension.COMPLETENESS].score)
                trends["accuracy_scores"].append(metrics[QualityDimension.ACCURACY].score)
                trends["timeliness_scores"].append(metrics[QualityDimension.TIMELINESS].score)
            
            current_date = period_end
        
        return trends
    
    def _generate_recommendations(self, dimension_metrics: Dict[QualityDimension, QualityMetric], 
                                overall_score: float) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于各维度得分生成建议
        for dimension, metric in dimension_metrics.items():
            if metric.score < 70:
                if dimension == QualityDimension.COMPLETENESS:
                    recommendations.append("提高情报内容完整性，确保关键字段（内容、标题、类型、来源）完整填写")
                elif dimension == QualityDimension.ACCURACY:
                    recommendations.append("加强情报验证机制，提高置信度评分和来源可信度")
                elif dimension == QualityDimension.TIMELINESS:
                    recommendations.append("优化数据采集频率，减少情报发布时间延迟")
                elif dimension == QualityDimension.RELEVANCE:
                    recommendations.append("改进重要性评估机制，提高高重要性情报比例")
                elif dimension == QualityDimension.CONSISTENCY:
                    recommendations.append("减少重复情报，统一数据格式标准")
                elif dimension == QualityDimension.USABILITY:
                    recommendations.append("增加情报摘要，提高用户互动率")
        
        # 基于总体得分生成建议
        if overall_score < 60:
            recommendations.insert(0, "情报质量整体较差，需要全面改进数据采集、处理和验证流程")
        elif overall_score < 75:
            recommendations.insert(0, "情报质量一般，建议重点关注低分维度进行改进")
        elif overall_score >= 90:
            recommendations.append("情报质量优秀，继续保持并优化现有流程")
        
        # 如果没有具体建议，添加通用建议
        if not recommendations:
            recommendations.append("情报质量良好，建议定期监控并持续优化")
        
        return recommendations[:5]  # 最多返回5条建议
    
    def _identify_risk_factors(self, dimension_metrics: Dict[QualityDimension, QualityMetric]) -> List[str]:
        """识别风险因素"""
        risk_factors = []
        
        for dimension, metric in dimension_metrics.items():
            if metric.score < 50:
                risk_factors.append(f"{dimension.value}维度得分过低（{metric.score}分），可能影响决策准确性")
            
            # 检查具体指标
            if dimension == QualityDimension.ACCURACY:
                if metric.indicators.get("verification_rate", 100) < 30:
                    risk_factors.append("情报验证率过低，存在准确性风险")
            
            elif dimension == QualityDimension.TIMELINESS:
                recent_items = metric.indicators.get("recent_items_24h", 0)
                total_items = metric.indicators.get("total_items", 1)
                if recent_items / total_items < 0.3:
                    risk_factors.append("24小时内新鲜情报比例不足30%，存在时效性风险")
        
        return risk_factors
    
    def _create_improvement_targets(self, dimension_metrics: Dict[QualityDimension, QualityMetric]) -> List[str]:
        """制定改进目标"""
        targets = []
        
        for dimension, metric in dimension_metrics.items():
            current_score = metric.score
            if current_score < 80:
                target_score = min(100, current_score + 15)  # 提高15分
                targets.append(f"将{dimension.value}维度得分从{current_score}分提高到{target_score}分")
        
        return targets[:3]  # 最多返回3个目标
    
    def _generate_source_specific_recommendations(self, dimension_metrics: Dict[QualityDimension, QualityMetric],
                                                overall_score: float, source_name: str, reliability_score: float) -> List[str]:
        """生成数据源特定的建议"""
        recommendations = []
        
        # 基于数据源可信度
        if reliability_score < 0.6:
            recommendations.append(f"数据源'{source_name}'可信度较低（{reliability_score:.2f}），建议验证其准确性或寻找替代源")
        
        # 基于各维度得分
        for dimension, metric in dimension_metrics.items():
            if metric.score < 70:
                if dimension == QualityDimension.ACCURACY:
                    recommendations.append(f"数据源'{source_name}'的准确性需要提升，建议加强数据验证")
                elif dimension == QualityDimension.TIMELINESS:
                    recommendations.append(f"数据源'{source_name}'的更新频率需要优化，以提高情报时效性")
        
        # 基于总体得分
        if overall_score < 60:
            recommendations.insert(0, f"数据源'{source_name}'的整体情报质量较差，建议重新评估其使用价值")
        elif overall_score >= 85:
            recommendations.append(f"数据源'{source_name}'表现良好，可考虑增加其数据采集权重")
        
        return recommendations[:5]
    
    def _calculate_weight_distribution(self, intelligence_list: List[Intelligence]) -> Dict[str, int]:
        """计算权重分布"""
        distribution = {
            "very_low": 0,    # 0-0.2
            "low": 0,         # 0.2-0.4
            "medium": 0,      # 0.4-0.6
            "high": 0,        # 0.6-0.8
            "very_high": 0    # 0.8-1.0
        }
        
        for intel in intelligence_list:
            if hasattr(intel, 'calculated_weight'):
                weight = intel.calculated_weight
                if weight <= 0.2:
                    distribution["very_low"] += 1
                elif weight <= 0.4:
                    distribution["low"] += 1
                elif weight <= 0.6:
                    distribution["medium"] += 1
                elif weight <= 0.8:
                    distribution["high"] += 1
                else:
                    distribution["very_high"] += 1
        
        return distribution
    
    def _calculate_confidence_interval(self, scores: List[float], confidence_level: float = 0.95) -> Dict[str, float]:
        """计算置信区间（简化版本）"""
        if len(scores) < 2:
            return {"lower": 0, "upper": 0, "mean": 0}
        
        mean_score = statistics.mean(scores)
        stdev = statistics.stdev(scores) if len(scores) >= 2 else 0
        
        # 简化计算（实际应使用t分布）
        margin = stdev * 1.96 / (len(scores) ** 0.5)  # 95%置信区间
        
        return {
            "lower": max(0, mean_score - margin),
            "upper": min(100, mean_score + margin),
            "mean": mean_score
        }
    
    def _create_empty_result(self, days: int) -> QualityAnalysisResult:
        """创建空结果"""
        return QualityAnalysisResult(
            period_days=days,
            total_items=0,
            overall_score=0.0,
            quality_level=QualityLevel.UNACCEPTABLE,
            dimension_scores={dim.value: 0.0 for dim in QualityDimension},
            detailed_metrics=[],
            trends={},
            recommendations=["暂无数据，无法进行质量分析"],
            risk_factors=["数据不足，无法评估风险"],
            improvement_targets=["首先需要收集足够的数据"]
        )