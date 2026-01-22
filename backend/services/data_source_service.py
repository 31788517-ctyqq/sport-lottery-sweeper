"""
数据源管理服务
处理数据源的CRUD操作和状态管理
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from fastapi import HTTPException, status

from ..models.crawler_config import CrawlerConfig
from ..models.admin_user import AdminUser
from ..models.crawler_logs import CrawlerTaskLog, CrawlerSourceStat
from ..schemas.crawler import (
    CrawlerSourceCreate, CrawlerSourceUpdate, CrawlerSourceResponse
)
from .crawler_service import BaseCrawlerService


class DataSourceService(BaseCrawlerService):
    """数据源服务类"""
    
    def get_sources(self, status: Optional[str] = None, search: Optional[str] = None,
                   page: int = 1, page_size: int = 20) -> List[CrawlerSourceResponse]:
        """
        获取数据源列表
        
        Args:
            status: 状态筛选
            search: 搜索关键词
            page: 页码
            page_size: 每页数量
            
        Returns:
            List[CrawlerSourceResponse]: 数据源列表
        """
        query = self.db.query(CrawlerConfig)
        
        # 状态筛选
        if status:
            query = query.filter(CrawlerConfig.is_active == (status == "online"))
        
        # 搜索筛选
        if search:
            search_filter = and_(
                CrawlerConfig.name.contains(search),
            )
            query = query.filter(search_filter)
        
        # 分页
        offset = (page - 1) * page_size
        sources = query.offset(offset).limit(page_size).all()
        
        # 转换为响应模型
        result = []
        for source in sources:
            # 从数据库获取真实统计数据
            success_rate = self._calculate_real_success_rate(source.id)
            response_time = self._get_avg_response_time(source.id)
            last_check_time = self._get_last_check_time(source.id)
            
            response = CrawlerSourceResponse(
                id=source.id,
                name=source.name,
                url=source.url,
                description=source.description,
                source_type="http",  # 默认类型，后续可从config_data解析
                status="online" if source.is_active else "offline",
                priority=1,  # 默认优先级，后续可从config_data解析
                timeout=30,  # 默认超时，后续可从config_data解析
                retry_times=3,  # 默认重试次数，后续可从config_data解析
                success_rate=success_rate,
                response_time=response_time,
                last_check_time=last_check_time,
                created_at=source.created_at,
                updated_at=source.updated_at
            )
            result.append(response)
        
        return result
    
    def _calculate_real_success_rate(self, source_id: int) -> float:
        """
        计算数据源的真实成功率
        
        Args:
            source_id: 数据源ID
            
        Returns:
            float: 成功率百分比
        """
        # 查询最近30天的日志
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        logs = self.db.query(CrawlerTaskLog).filter(
            and_(
                CrawlerTaskLog.source_id == source_id,
                CrawlerTaskLog.started_at >= thirty_days_ago
            )
        ).all()
        
        if not logs:
            # 如果没有日志，尝试从统计表中获取数据
            stats = self.db.query(CrawlerSourceStat).filter(
                CrawlerSourceStat.source_id == source_id
            ).order_by(desc(CrawlerSourceStat.date)).limit(30).all()
            
            if not stats:
                return 0.0
            
            total_requests = sum(stat.total_requests for stat in stats)
            successful_requests = sum(stat.successful_requests for stat in stats)
            
            if total_requests == 0:
                return 0.0
            
            return round((successful_requests / total_requests) * 100, 2)
        
        total_requests = len(logs)
        successful_requests = sum(1 for log in logs if log.status == "success")
        
        if total_requests == 0:
            return 0.0
        
        return round((successful_requests / total_requests) * 100, 2)
    
    def _get_avg_response_time(self, source_id: int) -> float:
        """
        获取平均响应时间
        
        Args:
            source_id: 数据源ID
            
        Returns:
            float: 平均响应时间（毫秒）
        """
        # 查询最近的成功请求日志
        logs = self.db.query(CrawlerTaskLog).filter(
            and_(
                CrawlerTaskLog.source_id == source_id,
                CrawlerTaskLog.status == "success",
                CrawlerTaskLog.response_time_ms.isnot(None)
            )
        ).order_by(desc(CrawlerTaskLog.started_at)).limit(100).all()
        
        if not logs:
            return 0.0
        
        response_times = [log.response_time_ms for log in logs if log.response_time_ms]
        if not response_times:
            return 0.0
        
        return round(sum(response_times) / len(response_times), 2)
    
    def _get_last_check_time(self, source_id: int) -> Optional[datetime]:
        """
        获取最后一次检查时间
        
        Args:
            source_id: 数据源ID
            
        Returns:
            Optional[datetime]: 最后检查时间
        """
        # 查询最近的任务日志
        latest_log = self.db.query(CrawlerTaskLog).filter(
            CrawlerTaskLog.source_id == source_id
        ).order_by(desc(CrawlerTaskLog.started_at)).first()
        
        if latest_log:
            return latest_log.started_at
        
        # 如果没有日志，返回数据源的更新时间
        source = self.get_source_by_id(source_id)
        return source.updated_at if source else None

    def get_source_by_id(self, source_id: int) -> Optional[CrawlerConfig]:
        """
        根据ID获取数据源
        
        Args:
            source_id: 数据源ID
            
        Returns:
            Optional[CrawlerConfig]: 数据源对象
        """
        return self.db.query(CrawlerConfig).filter(
            CrawlerConfig.id == source_id
        ).first()
    
    def create_source(self, source_data: CrawlerSourceCreate, created_by: int) -> CrawlerConfig:
        """
        创建数据源
        
        Args:
            source_data: 数据源创建数据
            created_by: 创建者ID
            
        Returns:
            CrawlerConfig: 创建的数据源
        """
        # 检查名称唯一性
        existing = self.db.query(CrawlerConfig).filter(
            CrawlerConfig.name == source_data.name
        ).first()
        if existing:
            raise ValueError("数据源名称已存在")
        
        # 创建新数据源
        config_data = getattr(source_data, 'config', {}) or {}
        
        db_source = CrawlerConfig(
            name=source_data.name,
            description=source_data.description,
            url=source_data.url,
            frequency=3600,  # 默认1小时
            is_active=source_data.status == "online",
            config_data=str(config_data),
            created_by=created_by
        )
        
        self.db.add(db_source)
        self.db.commit()
        self.db.refresh(db_source)
        
        return db_source
    
    def update_source(self, source_id: int, source_data: CrawlerSourceUpdate, 
                     updated_by: int) -> Optional[CrawlerConfig]:
        """
        更新数据源
        
        Args:
            source_id: 数据源ID
            source_data: 数据源更新数据
            updated_by: 更新者ID
            
        Returns:
            Optional[CrawlerConfig]: 更新后的数据源
        """
        db_source = self.get_source_by_id(source_id)
        if not db_source:
            return None
        
        # 更新字段
        update_data = source_data.dict(exclude_unset=True)
        
        if 'name' in update_data:
            # 检查名称唯一性（排除自身）
            existing = self.db.query(CrawlerConfig).filter(
                and_(
                    CrawlerConfig.name == update_data['name'],
                    CrawlerConfig.id != source_id
                )
            ).first()
            if existing:
                raise ValueError("数据源名称已存在")
            db_source.name = update_data['name']
        
        if 'description' in update_data:
            db_source.description = update_data['description']
        
        if 'url' in update_data:
            db_source.url = update_data['url']
        
        if 'status' in update_data:
            db_source.is_active = update_data['status'] == "online"
        
        if 'config' in update_data:
            db_source.config_data = str(update_data['config'])
        
        db_source.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(db_source)
        
        return db_source
    
    def delete_source(self, source_id: int) -> bool:
        """
        删除数据源
        
        Args:
            source_id: 数据源ID
            
        Returns:
            bool: 是否删除成功
        """
        db_source = self.get_source_by_id(source_id)
        if not db_source:
            return False
        
        self.db.delete(db_source)
        self.db.commit()
        return True
    
    def check_health(self, source_id: int) -> Dict[str, Any]:
        """
        检查数据源健康状态（基于历史数据评估）
        
        Args:
            source_id: 数据源ID
            
        Returns:
            Dict[str, Any]: 健康检查结果
        """
        db_source = self.get_source_by_id(source_id)
        if not db_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="数据源不存在"
            )
        
        # 基于最近24小时的实际数据进行健康评估
        yesterday = datetime.now() - timedelta(hours=24)
        
        recent_logs = self.db.query(CrawlerTaskLog).filter(
            and_(
                CrawlerTaskLog.source_id == source_id,
                CrawlerTaskLog.started_at >= yesterday
            )
        ).all()
        
        if not recent_logs:
            # 如果没有近期数据，检查数据源是否启用
            status_value = "online" if db_source.is_active else "offline"
            return {
                "status": status_value,
                "response_time_ms": 0,
                "status_code": 200 if db_source.is_active else 503,
                "timestamp": self._get_current_timestamp(),
                "message": "无近期运行数据，基于配置状态评估"
            }
        
        # 计算真实指标
        total_requests = len(recent_logs)
        successful_requests = sum(1 for log in recent_logs if log.status == "success")
        failed_requests = total_requests - successful_requests
        
        # 计算成功率
        success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        
        # 计算平均响应时间
        response_times = [log.response_time_ms for log in recent_logs if log.response_time_ms]
        avg_response_time = round(sum(response_times) / len(response_times), 2) if response_times else 0
        
        # 评估健康状态
        if success_rate >= 90:
            health_status = "healthy"
            status_code = 200
        elif success_rate >= 70:
            health_status = "warning"
            status_code = 200
        else:
            health_status = "critical"
            status_code = 503
        
        # 获取最近一次运行信息
        last_run = max(recent_logs, key=lambda x: x.started_at) if recent_logs else None
        last_run_time = last_run.started_at.isoformat() if last_run else None
        
        return {
            "status": health_status,
            "response_time_ms": avg_response_time,
            "status_code": status_code,
            "timestamp": self._get_current_timestamp(),
            "metrics": {
                "total_requests_24h": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate_percent": round(success_rate, 2),
                "avg_response_time_ms": avg_response_time
            },
            "last_run_at": last_run_time,
            "message": f"基于24小时内{total_requests}次运行数据统计"
        }
    
    def update_status(self, source_id: int, new_status: str, updated_by: int) -> bool:
        """
        更新数据源状态
        
        Args:
            source_id: 数据源ID
            new_status: 新状态
            updated_by: 更新者ID
            
        Returns:
            bool: 是否更新成功
        """
        db_source = self.get_source_by_id(source_id)
        if not db_source:
            return False
        
        db_source.is_active = (new_status == "online")
        db_source.updated_by = updated_by
        
        self.db.commit()
        return True
    
    def batch_update_status(self, source_ids: List[int], new_status: str, 
                          updated_by: int) -> int:
        """
        批量更新数据源状态
        
        Args:
            source_ids: 数据源ID列表
            new_status: 新状态
            updated_by: 更新者ID
            
        Returns:
            int: 更新的数量
        """
        is_active = (new_status == "online")
        
        updated_count = self.db.query(CrawlerConfig).filter(
            CrawlerConfig.id.in_(source_ids)
        ).update({
            CrawlerConfig.is_active: is_active,
            CrawlerConfig.updated_by: updated_by
        }, synchronize_session=False)
        
        self.db.commit()
        return updated_count
    
    def batch_test_connections(self, source_ids: List[int]) -> Dict[str, Any]:
        """
        批量测试数据源连接
        
        Args:
            source_ids: 数据源ID列表
            
        Returns:
            Dict[str, Any]: 测试结果
        """
        results = []
        
        for source_id in source_ids:
            try:
                health_result = self.check_health(source_id)
                results.append({
                    "source_id": source_id,
                    "status": health_result["status"],
                    "response_time_ms": health_result["response_time_ms"],
                    "success": health_result["status"] == "online"
                })
            except Exception as e:
                results.append({
                    "source_id": source_id,
                    "status": "error",
                    "error": str(e),
                    "success": False
                })
        
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "total": len(source_ids),
            "success": success_count,
            "failed": len(source_ids) - success_count,
            "results": results
        }
    
    def export_report(self, format: str = "csv") -> Dict[str, Any]:
        """
        导出数据源报告
        
        Args:
            format: 导出格式
            
        Returns:
            Dict[str, Any]: 报告数据
        """
        sources = self.db.query(CrawlerConfig).all()
        
        report_data = {
            "format": format,
            "generated_at": self._get_current_timestamp(),
            "total_sources": len(sources),
            "sources": []
        }
        
        for source in sources:
            report_data["sources"].append({
                "id": source.id,
                "name": source.name,
                "url": source.url,
                "status": "online" if source.is_active else "offline",
                "created_at": source.created_at.isoformat() if source.created_at else None,
                "updated_at": source.updated_at.isoformat() if source.updated_at else None
            })
        
        return report_data