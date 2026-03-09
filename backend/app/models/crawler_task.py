from datetime import datetime
from app import db

class CrawlerTask(db.Model):
    __tablename__ = 'crawler_task'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, comment='任务名称')
    source_id = db.Column(db.Integer, nullable=False, comment='关联数据源ID')
    cron_expr = db.Column(db.String(50), nullable=False, comment='Cron表达式')
    next_run_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='idle', comment='idle/running/paused')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'source_id': self.source_id,
            'cron_expr': self.cron_expr,
            'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }