"""
日志服务层
处理日志数据的增删改查操作
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from ..models.log_entry import LogEntry
from ..schemas.log_entry import LogEntryCreate, LogEntryUpdate


class LogService:
    """日志服务类"""
    
    def __init__(self, db: Session):
        self.db = db

    def create_log_entry(self, log_entry: LogEntryCreate) -> LogEntry:
        """创建日志条目"""
        db_log_entry = LogEntry(**log_entry.dict())
        self.db.add(db_log_entry)
        self.db.commit()
        self.db.refresh(db_log_entry)
        return db_log_entry

    def get_log_entry(self, log_id: int) -> Optional[LogEntry]:
        """根据ID获取日志条目"""
        return self.db.query(LogEntry).filter(LogEntry.id == log_id).first()

    def get_log_entries(
        self,
        skip: int = 0,
        limit: int = 100,
        level: Optional[str] = None,
        module: Optional[str] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> tuple[List[LogEntry], int]:
        """获取日志条目列表"""
        query = self.db.query(LogEntry)
        
        # 应用过滤条件
        if level:
            query = query.filter(LogEntry.level.ilike(f"%{level}%"))
        if module:
            query = query.filter(LogEntry.module.ilike(f"%{module}%"))
        if user_id:
            query = query.filter(LogEntry.user_id == user_id)
        if start_date:
            query = query.filter(LogEntry.timestamp >= start_date)
        if end_date:
            query = query.filter(LogEntry.timestamp <= end_date)
        if search:
            query = query.filter(or_(
                LogEntry.message.ilike(f"%{search}%"),
                LogEntry.module.ilike(f"%{search}%")
            ))
        
        # 获取总数
        total = query.count()
        
        # 应用分页
        logs = query.order_by(LogEntry.timestamp.desc()).offset(skip).limit(limit).all()
        
        return logs, total

    def get_log_statistics(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        total_count = self.db.query(LogEntry).count()
        
        # 按级别统计
        from sqlalchemy import func
        level_stats = self.db.query(
            LogEntry.level,
            func.count(LogEntry.id).label('count')
        ).group_by(LogEntry.level).all()
        
        # 按模块统计
        module_stats = self.db.query(
            LogEntry.module,
            func.count(LogEntry.id).label('count')
        ).group_by(LogEntry.module).all()
        
        # 近7天日志数量
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_logs = self.db.query(LogEntry).filter(
            LogEntry.timestamp >= seven_days_ago
        ).count()
        
        return {
            "total_logs": total_count,
            "level_stats": [{"level": stat[0], "count": stat[1]} for stat in level_stats],
            "module_stats": [{"module": stat[0], "count": stat[1]} for stat in module_stats],
            "recent_logs_7_days": recent_logs
        }

    def delete_log_entry(self, log_id: int) -> bool:
        """删除日志条目"""
        log_entry = self.db.query(LogEntry).filter(LogEntry.id == log_id).first()
        if log_entry:
            self.db.delete(log_entry)
            self.db.commit()
            return True
        return False

    def bulk_delete_logs(
        self,
        level: Optional[str] = None,
        module: Optional[str] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """批量删除日志"""
        query = self.db.query(LogEntry)
        
        # 应用过滤条件
        if level:
            query = query.filter(LogEntry.level.ilike(f"%{level}%"))
        if module:
            query = query.filter(LogEntry.module.ilike(f"%{module}%"))
        if user_id:
            query = query.filter(LogEntry.user_id == user_id)
        if start_date:
            query = query.filter(LogEntry.timestamp >= start_date)
        if end_date:
            query = query.filter(LogEntry.timestamp <= end_date)
        
        count = query.delete(synchronize_session=False)
        self.db.commit()
        return count