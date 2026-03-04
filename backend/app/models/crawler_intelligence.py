from datetime import datetime
from app import db

class CrawlerIntelligence(db.Model):
    __tablename__ = 'crawler_intelligence'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, comment='统计日期')
    source_id = db.Column(db.Integer, nullable=False, comment='数据源ID')
    total_count = db.Column(db.Integer, default=0, comment='抓取总数')
    success_count = db.Column(db.Integer, default=0, comment='成功数')
    failed_count = db.Column(db.Integer, default=0, comment='失败数')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'source_id': self.source_id,
            'total_count': self.total_count,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'created_at': self.created_at.isoformat()
        }