# append_models.py
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

models_code = """

# --- 后台管理模块模型 ---

class AdminData(Base):
    """通用数据记录（后台管理用）"""
    __tablename__ = "admin_data"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50))
    status = Column(String(20), default="active")  # active/inactive
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AdminData(name='{self.name}', type='{self.type}')"


class SystemConfig(Base):
    """系统配置项"""
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(500))
    description = Column(String(300))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', value='{self.value}')"


class CrawlerConfig(Base):
    """爬虫配置"""
    __tablename__ = "crawler_configs"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), nullable=False)
    url_pattern = Column(String(500), nullable=False)
    interval = Column(Integer, default=60)  # 分钟
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CrawlerConfig(source='{self.source_name}', interval={self.interval})"


class IntelligenceRecord(Base):
    """智能分析记录（后台管理用，独立于比赛情报）"""
    __tablename__ = "intelligence_records"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String(100), nullable=False)
    accuracy = Column(String(20))  # 如 '82%'
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="完成")  # 完成/运行中

    def __repr__(self):
        return f"<IntelligenceRecord(model='{self.model}', accuracy='{self.accuracy}')"
"""

with open(BASE_DIR / "backend" / "models.py", "a", encoding="utf-8") as f:
    f.write(models_code)

print("Models appended successfully.")