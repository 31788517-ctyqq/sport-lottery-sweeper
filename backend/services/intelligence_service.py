"""
数据情报服务
处理情报数据的统计分析、趋势分析和导出功能
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
import csv
import io

from ..models.intelligence import Intelligence
from ..models.match import Match
from ..models.admin_user import AdminUser
from ..models.crawler_logs import CrawlerTaskLog
from ..schemas.crawler import (
    CrawlerIntelligenceStats, CrawlerIntelligenceData, CrawlerIntelligenceResponse,
    TrendAnalysisData, ErrorDistributionData
)
from .crawler_service import BaseCrawlerService


class IntelligenceService(BaseCrawlerService):
    """数据情报服务类"""
    
    def get_stats(self) -> CrawlerIntelligenceStats:
        """
        获取数据情报统计信息
        
        Returns:
            CrawlerIntelligenceStats: 统计信息
        """
        # 获取基础统计数据
        total_count = self.db.query(Intelligence).count()
        
        # 今日数据
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        today_stats = self.db.query(
            func.count(Intelligence.id).label('total'),
            func.sum(func.cast(Intelligence.is_new, Integer)).label('success')
        ).filter(
            and_(
                Intelligence.created_at >= today_start,
                Intelligence.created_at <= today_end
            )
        ).first()
        
        today_total = today_stats.total or 0
        today_success = today_stats.success or 0
        today_failed = today_total - today_success
        
        # 计算总体成功率
        overall_success_rate = 0.0
        if total_count > 0:
            # 模拟成功率计算（实际应根据业务逻辑计算）
            successful_intelligence = self.db.query(Intelligence).filter(
                Intelligence.content.isnot(None)
            ).count()
            overall_success_rate = round(successful_intelligence / total_count * 100, 2)
        
        # 活跃数据源数量
        active_sources = self.db.query(Intelligence.source).distinct().count()
        
        # 错误分布（基于真实日志数据）
        error_distribution = self._get_real_error_distribution()

        return CrawlerIntelligenceStats(
            total_crawled=total_count,
            today_crawled=today_total,
            today_success=today_success,
            today_failed=today_failed,
            overall_success_rate=overall_success_rate,
            active_sources=active_sources,
            error_distribution=error_distribution
        )
    
    def _get_real_error_distribution(self) -> List[Dict[str, Any]]:
        """
        获取基于真实日志的错误分布
        
        Returns:
            List[Dict[str, Any]]: 错误分布数据
        """
        # 查询最近30天的失败日志
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        failed_logs = self.db.query(CrawlerTaskLog).filter(
            and_(
                CrawlerTaskLog.started_at >= thirty_days_ago,
                CrawlerTaskLog.status.in_(['failed', 'error', 'timeout'])
            )
        ).all()
        
        if not failed_logs:
            # 如果没有失败日志，返回空数组
            return []
        
        # 分析错误消息来分类错误类型
        error_categories = {
            '网络错误': ['network', 'connection', 'dns', 'socket', 'connection refused'],
            '解析错误': ['parse', 'parsing', 'invalid', 'malformed', 'syntax'],
            '数据格式错误': ['format', 'schema', 'validation', 'type', 'convert'],
            '超时错误': ['timeout', 'timed out', 'slow', 'latency'],
            '认证错误': ['auth', 'unauthorized', 'forbidden', 'token', 'login'],
            '服务器错误': ['server', '5xx', '502', '503', '504', 'internal']
        }
        
        error_counts = {category: 0 for category in error_categories.keys()}
        uncategorized = 0
        
        for log in failed_logs:
            error_msg = (log.error_message or '').lower()
            categorized = False
            
            for category, keywords in error_categories.items():
                if any(keyword in error_msg for keyword in keywords):
                    error_counts[category] += 1
                    categorized = True
                    break
            
            if not categorized:
                uncategorized += 1
        
        # 构建响应数据
        colors = {
            '网络错误': '#ff4757',
            '解析错误': '#ff6348', 
            '数据格式错误': '#ff7675',
            '超时错误': '#fd79a8',
            '认证错误': '#e17055',
            '服务器错误': '#d63031',
            '其他错误': '#636e72'
        }
        
        result = []
        for category, count in error_counts.items():
            if count > 0:
                result.append({
                    "name": category,
                    "value": count,
                    "color": colors.get(category, '#636e72')
                })
        
        # 添加未分类错误
        if uncategorized > 0:
            result.append({
                "name": "其他错误",
                "value": uncategorized,
                "color": colors['其他错误']
            })
        
        # 按值降序排列
        result.sort(key=lambda x: x['value'], reverse=True)
        
        return result
    
    def get_intelligence_data(self, source_id: Optional[int] = None, 
                            category: Optional[str] = None, status: Optional[str] = None,
                            page: int = 1, page_size: int = 20) -> List[CrawlerIntelligenceData]:
        """
        获取数据情报列表
        
        Args:
            source_id: 数据源ID筛选
            category: 情报分类筛选
            status: 状态筛选
            page: 页码
            page_size: 每页数量
            
        Returns:
            List[CrawlerIntelligenceData]: 情报数据列表
        """
        query = self.db.query(Intelligence).join(
            Match, Intelligence.match_id == Match.match_id
        )
        
        # 应用筛选条件
        if source_id:
            query = query.filter(Intelligence.source == f"source_{source_id}")
        
        if category:
            query = query.filter(Intelligence.category == category)
        
        if status:
            if status == "new":
                query = query.filter(Intelligence.is_new == True)
            elif status == "processed":
                query = query.filter(Intelligence.is_new == False)
        
        # 分页
        offset = (page - 1) * page_size
        intelligence_list = query.offset(offset).limit(page_size).all()
        
        # 转换为响应模型
        result = []
        for intel in intelligence_list:
            # 查找数据源名称
            source_name = "未知数据源"
            if hasattr(intel, 'source') and intel.source:
                source_name = intel.source.replace('_', ' ').title()
            
            response = CrawlerIntelligenceData(
                id=intel.id,
                source_id=source_id or 1,  # 模拟数据源ID
                source_name=source_name,
                title=f"{intel.category}情报",
                content=intel.content or "",
                category=intel.category or "general",
                status="new" if intel.is_new else "processed",
                confidence_score=round(intel.weight or 0.5, 2),
                crawled_at=intel.created_at,
                processed_at=intel.updated_at
            )
            result.append(response)
        
        return result
    
    def get_trend_analysis(self, days: int = 7) -> TrendAnalysisData:
        """
        获取趋势分析数据
        
        Args:
            days: 分析天数
            
        Returns:
            TrendAnalysisData: 趋势分析数据
        """
        # 计算日期范围
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days - 1)
        
        # 生成日期列表
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime("%m-%d"))
            current_date += timedelta(days=1)
        
        # 模拟趋势数据（实际应从数据库查询）
        import random
        
        # 基础数据
        base_crawl = 50
        crawl_counts = []
        success_counts = []
        error_counts = []
        
        for i, date in enumerate(dates):
            # 模拟日常波动
            day_factor = 1 + 0.3 * random.sin(i * 0.5)  # 正弦波模拟周期性
            random_factor = random.uniform(0.7, 1.3)  # 随机波动
            
            daily_crawl = int(base_crawl * day_factor * random_factor)
            daily_success = int(daily_crawl * random.uniform(0.8, 0.95))  # 80-95%成功率
            daily_error = daily_crawl - daily_success
            
            crawl_counts.append(daily_crawl)
            success_counts.append(daily_success)
            error_counts.append(daily_error)
        
        return TrendAnalysisData(
            dates=dates,
            crawl_counts=crawl_counts,
            success_counts=success_counts,
            error_counts=error_counts
        )
    
    def mark_as_invalid(self, intelligence_id: int, updated_by: int) -> bool:
        """
        标记情报为无效
        
        Args:
            intelligence_id: 情报ID
            updated_by: 更新者ID
            
        Returns:
            bool: 是否标记成功
        """
        intelligence = self.db.query(Intelligence).filter(
            Intelligence.id == intelligence_id
        ).first()
        
        if not intelligence:
            return False
        
        # 标记为无效（设置权重为0或添加标记）
        intelligence.weight = 0.0
        intelligence.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def recrawl_data(self, intelligence_id: int, triggered_by: int) -> Dict[str, Any]:
        """
        重新抓取指定情报数据
        
        Args:
            intelligence_id: 情报ID
            triggered_by: 触发者ID
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        intelligence = self.db.query(Intelligence).filter(
            Intelligence.id == intelligence_id
        ).first()
        
        if not intelligence:
            raise ValueError("情报不存在")
        
        # 模拟重新抓取过程
        import random
        import time
        
        start_time = time.time()
        
        # 模拟抓取时间
        time.sleep(0.5)
        
        # 模拟抓取结果
        success = random.choice([True, True, True, False])  # 75%成功率
        new_content = None
        
        if success:
            new_content = f"重新抓取的情报内容 - {self._get_current_timestamp()}"
            intelligence.content = new_content
            intelligence.updated_at = datetime.utcnow()
            intelligence.weight = random.uniform(0.5, 1.0)  # 重置权重
            
            self.db.commit()
        
        return {
            "intelligence_id": intelligence_id,
            "status": "success" if success else "error",
            "execution_time": round(time.time() - start_time, 2),
            "new_content": new_content,
            "success": success,
            "message": f"重新抓取{'成功' if success else '失败'}",
            "triggered_by": triggered_by,
            "timestamp": self._get_current_timestamp()
        }
    
    def batch_mark_data(self, ids: List[int], status: str, updated_by: int) -> int:
        """
        批量标记情报数据
        
        Args:
            ids: 情报ID列表
            status: 状态
            updated_by: 更新者ID
            
        Returns:
            int: 标记的数量
        """
        if status == "invalid":
            # 标记为无效
            updated_count = self.db.query(Intelligence).filter(
                Intelligence.id.in_(ids)
            ).update({
                Intelligence.weight: 0.0,
                Intelligence.updated_at: datetime.utcnow()
            }, synchronize_session=False)
        elif status == "active":
            # 标记为有效（重置权重）
            updated_count = self.db.query(Intelligence).filter(
                Intelligence.id.in_(ids)
            ).update({
                Intelligence.weight: 0.5,
                Intelligence.updated_at: datetime.utcnow()
            }, synchronize_session=False)
        else:
            return 0
        
        self.db.commit()
        return updated_count
    
    def export_data(self, format: str = "csv") -> Dict[str, Any]:
        """
        导出数据情报
        
        Args:
            format: 导出格式
            
        Returns:
            Dict[str, Any]: 导出数据
        """
        # 获取所有情报数据
        intelligence_list = self.db.query(Intelligence).all()
        
        if format.lower() == "csv":
            return self._export_csv(intelligence_list)
        elif format.lower() == "json":
            return self._export_json(intelligence_list)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def _export_csv(self, intelligence_list: List[Intelligence]) -> Dict[str, Any]:
        """
        导出为CSV格式
        
        Args:
            intelligence_list: 情报列表
            
        Returns:
            Dict[str, Any]: CSV数据
        """
        output = io.StringIO()
        
        if not intelligence_list:
            return {"format": "csv", "data": "", "filename": "intelligence_export.csv"}
        
        # CSV头部
        fieldnames = ['ID', '比赛ID', '分类', '来源', '摘要', '内容', '权重', '创建时间', '更新时间', '是否新数据']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        # 写入数据
        for intel in intelligence_list:
            writer.writerow({
                'ID': intel.id,
                '比赛ID': intel.match_id,
                '分类': intel.category or '',
                '来源': intel.source or '',
                '摘要': intel.summary or '',
                '内容': intel.content or '',
                '权重': intel.weight or 0,
                '创建时间': intel.created_at.isoformat() if intel.created_at else '',
                '更新时间': intel.updated_at.isoformat() if intel.updated_at else '',
                '是否新数据': '是' if intel.is_new else '否'
            })
        
        csv_data = output.getvalue()
        output.close()
        
        return {
            "format": "csv",
            "data": csv_data,
            "filename": f"intelligence_export_{self._get_current_timestamp()[:10]}.csv",
            "size": len(csv_data.encode('utf-8'))
        }
    
    def _export_json(self, intelligence_list: List[Intelligence]) -> Dict[str, Any]:
        """
        导出为JSON格式
        
        Args:
            intelligence_list: 情报列表
            
        Returns:
            Dict[str, Any]: JSON数据
        """
        json_data = []
        
        for intel in intelligence_list:
            json_data.append({
                "id": intel.id,
                "match_id": intel.match_id,
                "category": intel.category,
                "source": intel.source,
                "summary": intel.summary,
                "content": intel.content,
                "weight": intel.weight,
                "created_at": intel.created_at.isoformat() if intel.created_at else None,
                "updated_at": intel.updated_at.isoformat() if intel.updated_at else None,
                "is_new": intel.is_new,
                "publish_time": intel.publish_time.isoformat() if intel.publish_time else None
            })
        
        return {
            "format": "json",
            "data": json_data,
            "filename": f"intelligence_export_{self._get_current_timestamp()[:10]}.json",
            "count": len(json_data)
        }
    
    def get_error_distribution(self) -> ErrorDistributionData:
        """
        获取错误分布数据
        
        Returns:
            ErrorDistributionData: 错误分布数据
        """
        # 模拟错误分布数据
        # 实际应用中应从日志或错误表中查询
        
        error_types = ["网络超时", "解析失败", "数据格式错误", "HTTP错误", "连接拒绝"]
        error_counts = [23, 15, 31, 8, 12]
        total_errors = sum(error_counts)
        
        percentages = [round(count / total_errors * 100, 1) for count in error_counts]
        
        return ErrorDistributionData(
            error_types=error_types,
            error_counts=error_counts,
            percentages=percentages
        )
    
    def analyze_intelligence_quality(self, days: int = 7) -> Dict[str, Any]:
        """
        分析情报质量
        
        Args:
            days: 分析天数
            
        Returns:
            Dict[str, Any]: 质量分析结果
        """
        # 计算日期范围
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 获取指定时间范围内的情报
        recent_intelligence = self.db.query(Intelligence).filter(
            Intelligence.created_at >= start_date
        ).all()
        
        if not recent_intelligence:
            return {
                "period_days": days,
                "total_count": 0,
                "quality_metrics": {}
            }
        
        # 计算质量指标
        total_count = len(recent_intelligence)
        
        # 完整性（有内容的情报比例）
        complete_count = sum(1 for intel in recent_intelligence if intel.content)
        completeness_rate = round(complete_count / total_count * 100, 2) if total_count > 0 else 0
        
        # 平均权重（质量评分）
        weights = [intel.weight for intel in recent_intelligence if intel.weight is not None]
        avg_weight = round(sum(weights) / len(weights), 3) if weights else 0
        
        # 时效性（新数据比例）
        new_count = sum(1 for intel in recent_intelligence if intel.is_new)
        freshness_rate = round(new_count / total_count * 100, 2) if total_count > 0 else 0
        
        return {
            "period_days": days,
            "total_count": total_count,
            "quality_metrics": {
                "completeness_rate": completeness_rate,
                "average_weight": avg_weight,
                "freshness_rate": freshness_rate,
                "quality_score": round((completeness_rate + min(avg_weight * 100, 100) + freshness_rate) / 3, 2)
            },
            "recommendations": self._generate_quality_recommendations(
                completeness_rate, avg_weight, freshness_rate
            )
        }
    
    def _generate_quality_recommendations(self, completeness: float, avg_weight: float, 
                                        freshness: float) -> List[str]:
        """
        生成质量改进建议
        
        Args:
            completeness: 完整率
            avg_weight: 平均权重
            freshness: 新鲜度
            
        Returns:
            List[str]: 建议列表
        """
        recommendations = []
        
        if completeness < 80:
            recommendations.append("提高情报内容完整性，确保每条情报都有详细描述")
        
        if avg_weight < 0.6:
            recommendations.append("提升情报质量权重，优化数据源筛选规则")
        
        if freshness < 70:
            recommendations.append("增加数据采集频率，确保情报及时性")
        
        if not recommendations:
            recommendations.append("情报质量良好，继续保持当前标准")
        
        return recommendations