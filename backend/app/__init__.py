from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .api.admin import init_admin_crawler

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sport_lottery.db'  # 或你的数据库地址
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # 注册爬虫管理后台 API
    init_admin_crawler(app)
    
    # TODO: 注册其他模块蓝图
    
    return app