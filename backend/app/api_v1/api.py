from fastapi import APIRouter
from .endpoints import login, users, lottery, crawler_task, crawler_task_logs, beidan_filter_api  # noqa

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# 竞彩相关API
api_router.include_router(lottery.router, prefix="/lottery", tags=["lottery"])

# 爬虫任务相关API
api_router.include_router(crawler_task.router, prefix="/crawler-tasks", tags=["crawler-tasks"])
api_router.include_router(crawler_task_logs.router, prefix="/crawler-task-logs", tags=["crawler-task-logs"])

# 北单过滤API
api_router.include_router(beidan_filter_api.router, prefix="/beidan-filter", tags=["beidan-filter"])