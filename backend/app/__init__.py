from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .api.admin import init_admin_crawler
import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# 导入配置
try:
    from backend.config import settings
    DATABASE_URI = settings.DATABASE_URL.replace('sqlite:///', 'sqlite:///')
except ImportError:
    # 回退方案
    DATABASE_URI = "sqlite:///data/sport_lottery.db"

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # 注册爬虫管理后台 API
    init_admin_crawler(app)
    
    # TODO: 注册其他模块蓝图
    
    return app