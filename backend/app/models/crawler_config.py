from datetime import datetime
from app import db

class CrawlerConfig(db.Model):
    __tablename__ = 'crawler_config'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, comment='配置名称')
    config_type = db.Column(db.String(20), nullable=False, comment='global/single')  # global 或 single
    content = db.Column(db.JSON, nullable=False, comment='配置内容(JSON)')
    version = db.Column(db.Integer, default=1, comment='版本号')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'config_type': self.config_type,
            'content': self.content,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }