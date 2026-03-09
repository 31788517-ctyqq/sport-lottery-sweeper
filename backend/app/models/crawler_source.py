from datetime import datetime
from app import db

class CrawlerSource(db.Model):
    __tablename__ = 'crawler_source'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, comment='数据源名称')
    url = db.Column(db.Text, nullable=False, comment='数据源地址')
    status = db.Column(db.String(20), default='offline', comment='online/offline')
    last_crawl_time = db.Column(db.DateTime, nullable=True)
    success_rate = db.Column(db.Float, default=0.0, comment='成功率')
    response_time = db.Column(db.Float, default=0.0, comment='平均响应时间(ms)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'status': self.status,
            'last_crawl_time': self.last_crawl_time.isoformat() if self.last_crawl_time else None,
            'success_rate': self.success_rate,
            'response_time': self.response_time,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }