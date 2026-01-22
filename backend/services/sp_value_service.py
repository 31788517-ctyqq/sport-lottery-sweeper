"""
SP值管理服务
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..models.matches import Match
from ..models.odds_companies import OddsCompany
from ..models.sp_records import SPRecord, SPModificationLog
from ..models.users import User
from ..schemas.sp_record import SPRecordCreate, SPRecordUpdate

logger = logging.getLogger(__name__)


class SPValueService:
    """SP值管理服务"""
    
    async def record_sp_value(self, db: Session, match_id: int, company_id: int,
                           handicap_type: str, handicap_value: float,
                           sp_value: float) -> SPRecord:
        """记录SP值"""
        try:
            # 验证比赛和公司存在
            match = db.query(Match).filter(Match.id == match_id).first()
            company = db.query(OddsCompany).filter(OddsCompany.id == company_id).first()
            
            if not match:
                raise ValueError(f"比赛ID {match_id} 不存在")
            if not company:
                raise ValueError(f"公司ID {company_id} 不存在")
            
            # 创建SP记录
            sp_record = SPRecord(
                match_id=match_id,
                company_id=company_id,
                handicap_type=handicap_type,
                handicap_value=handicap_value,
                sp_value=sp_value,
                recorded_at=datetime.utcnow()
            )
            
            db.add(sp_record)
            db.commit()
            db.refresh(sp_record)
            
            logger.info(f"记录SP值: 比赛{match_id}, 公司{company_id}, SP={sp_value}")
            
            return sp_record
            
        except Exception as e:
            db.rollback()
            logger.error(f"记录SP值失败: {str(e)}")
            raise
    
    async def modify_sp_value(self, db: Session, record_id: int, new_value: float,
                            operator_id: int, reason: str = None) -> SPRecord:
        """修改SP值并记录日志"""
        try:
            # 获取原记录
            sp_record = db.query(SPRecord).filter(SPRecord.id == record_id).first()
            if not sp_record:
                raise ValueError(f"SP记录ID {record_id} 不存在")
            
            # 验证操作员存在
            operator = db.query(User).filter(User.id == operator_id).first()
            if not operator:
                raise ValueError(f"操作员ID {operator_id} 不存在")
            
            # 记录修改日志
            modification_log = SPModificationLog(
                sp_record_id=record_id,
                original_value=sp_record.sp_value,
                modified_value=new_value,
                modified_by=operator_id,
                reason=reason
            )
            
            # 更新SP值
            sp_record.sp_value = new_value
            
            db.add(modification_log)
            db.commit()
            db.refresh(sp_record)
            
            logger.info(f"修改SP值: 记录{record_id}, {sp_record.sp_value} -> {new_value}, 操作员{operator_id}")
            
            return sp_record
            
        except Exception as e:
            db.rollback()
            logger.error(f"修改SP值失败: {str(e)}")
            raise
    
    async def get_sp_history(self, db: Session, match_id: int, 
                           company_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取比赛SP值历史"""
        query = db.query(SPRecord).join(OddsCompany).filter(
            SPRecord.match_id == match_id
        )
        
        if company_id:
            query = query.filter(SPRecord.company_id == company_id)
        
        records = query.order_by(SPRecord.recorded_at.asc()).all()
        
        history = []
        for record in records:
            history.append({
                "id": record.id,
                "company_name": record.company.name,
                "company_short_name": record.company.short_name,
                "handicap_type": record.handicap_type,
                "handicap_value": float(record.handicap_value) if record.handicap_value else None,
                "sp_value": float(record.sp_value),
                "recorded_at": record.recorded_at.isoformat(),
                "is_modified": len(record.modification_logs) > 0
            })
        
        return history
    
    async def get_sp_trend(self, db: Session, match_id: int, 
                          company_id: Optional[int] = None) -> Dict[str, Any]:
        """获取SP值走势数据"""
        history = await self.get_sp_history(db, match_id, company_id)
        
        if not history:
            return {"data": [], "statistics": {}}
        
        # 计算统计数据
        sp_values = [item["sp_value"] for item in history]
        statistics = {
            "min": min(sp_values),
            "max": max(sp_values),
            "avg": sum(sp_values) / len(sp_values),
            "count": len(sp_values),
            "change_count": len([v for v in sp_values if v != sp_values[0]]) - 1
        }
        
        return {
            "data": history,
            "statistics": statistics
        }
    
    async def get_latest_sp_values(self, db: Session, match_id: int) -> List[Dict[str, Any]]:
        """获取比赛最新的SP值（各公司）"""
        # 子查询获取每个公司的最新记录时间
        latest_times = db.query(
            SPRecord.company_id,
            func.max(SPRecord.recorded_at).label("latest_time")
        ).filter(
            SPRecord.match_id == match_id
        ).group_by(SPRecord.company_id).subquery()
        
        # 获取最新记录
        records = db.query(SPRecord).join(
            latest_times,
            (SPRecord.company_id == latest_times.c.company_id) & 
            (SPRecord.recorded_at == latest_times.c.latest_time)
        ).all()
        
        result = []
        for record in records:
            result.append({
                "company_id": record.company_id,
                "company_name": record.company.name,
                "company_short_name": record.company.short_name,
                "handicap_type": record.handicap_type,
                "handicap_value": float(record.handicap_value) if record.handicap_value else None,
                "sp_value": float(record.sp_value),
                "recorded_at": record.recorded_at.isoformat()
            })
        
        return sorted(result, key=lambda x: x["sp_value"])
    
    async def detect_anomalies(self, db: Session, match_id: int, 
                             threshold: float = 0.2) -> List[Dict[str, Any]]:
        """检测SP值异常变动"""
        history = await self.get_sp_history(db, match_id)
        
        anomalies = []
        for i in range(1, len(history)):
            prev_value = history[i-1]["sp_value"]
            curr_value = history[i]["sp_value"]
            
            if prev_value > 0:
                change_rate = abs(curr_value - prev_value) / prev_value
                
                if change_rate > threshold:
                    anomalies.append({
                        "time": history[i]["recorded_at"],
                        "company": history[i]["company_name"],
                        "prev_value": prev_value,
                        "curr_value": curr_value,
                        "change_rate": round(change_rate * 100, 2),
                        "severity": "high" if change_rate > 0.5 else "medium"
                    })
        
        return anomalies