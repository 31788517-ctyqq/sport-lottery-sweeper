"""
情报业务服务
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..models.intelligence import Intelligence, IntelligenceType, IntelligenceSource

logger = logging.getLogger(__name__)

class IntelligenceService:
    """情报服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_intelligence_by_id(self, intelligence_id: int) -> Optional[Intelligence]:
        """根据ID获取情报"""
        return self.db.query(Intelligence).filter(Intelligence.id == intelligence_id).first()
    
    def get_intelligence_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Intelligence]:
        """获取日期范围内的情报"""
        return self.db.query(Intelligence).filter(
            Intelligence.created_at >= start_date,
            Intelligence.created_at <= end_date
        ).all()
    
    def create_or_update_intelligence(self, intelligence_data: Dict) -> Dict:
        """创建或更新情报"""
        # 实现情报数据的创建或更新逻辑
        pass
    
    def mark_intelligence_outdated(self, match_id: int) -> int:
        """标记比赛相关情报为过期"""
        try:
            result = self.db.query(Intelligence).filter(
                Intelligence.match_id == match_id,
                Intelligence.status == "active"
            ).update({
                "status": "outdated",
                "updated_at": datetime.utcnow()
            })
            self.db.commit()
            return result
        except Exception as e:
            self.db.rollback()
            logger.error(f"标记情报过期失败: {str(e)}")
            return 0