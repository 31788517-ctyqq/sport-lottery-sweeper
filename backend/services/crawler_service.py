"""
爬虫服务基类
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ..models.admin_user import AdminUser


class BaseCrawlerService:
    """爬虫服务基类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳字符串"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def _calculate_success_rate(self, success_count: int, total_count: int) -> float:
        """计算成功率"""
        if total_count == 0:
            return 0.0
        return round(success_count / total_count * 100, 2)