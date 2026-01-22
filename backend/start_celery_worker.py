"""
启动 Celery Worker 脚本
用于异步执行训练任务
运行方式：python -m backend.start_celery_worker
"""
from backend.celery_app import celery_app

if __name__ == '__main__':
    celery_app.start()
