from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.resources import Link, Model
from fastapi_admin.widgets import displays, inputs
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import Base, engine  # 你的数据库引擎和Base
from backend.models import User, Match, Intelligence, CrawlerConfig  # 你的模型
from backend.core.admin_auth import admin_required  # 你的认证依赖

# 创建FastAPI实例（如果已有main.py的app，就复用并挂载admin）
app = FastAPI()

# 配置admin
admin_app.configure(
    logo_url="/static/logo.png",
    template_folders=["templates"],  # 可选自定义模板
    providers=[],
)

# 注册模型资源
@app.on_event("startup")
async def startup():
    await Base.metadata.create_all(engine)  # 确保表存在

# 示例：User模型管理
class UserResource(Model):
    label = "用户"
    model = User
    fields = [
        "id",
        "username",
        displays.ImageColumn("avatar", path="avatar"),
        "email",
        "is_active",
        "created_at",
    ]
    list_per_page = 20

admin_app.register(UserResource)

# 示例：Match模型管理
class MatchResource(Model):
    label = "比赛"
    model = Match
    fields = [
        "id",
        "league",
        "home_team",
        "away_team",
        "match_time",
        "status",
    ]

admin_app.register(MatchResource)

# 示例：Intelligence模型管理
class IntelligenceResource(Model):
    label = "情报"
    model = Intelligence
    fields = [
        "id",
        "match_id",
        "source",
        "content",
        "created_at",
    ]

admin_app.register(IntelligenceResource)

# 挂载到主应用
app.mount("/admin", admin_app)
