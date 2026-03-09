"""
填充日志数据的脚本
用于为日志管理模块提供测试数据
"""

import sys
import json
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.mutable import MutableDict
from faker import Faker

# 添加项目根目录到路径
sys.path.append('.')

from backend.database import get_db
from backend.models.base import Base
from backend.models.log_entry import LogEntry
from backend.models.admin_user import AdminLoginLog, AdminOperationLog
from backend.models.crawler_logs import CrawlerTaskLog
from backend.models.sp_modification_logs import SPModificationLog

fake = Faker('zh_CN')

def create_sample_logs(db_session, count=100):
    """创建示例日志数据"""
    print(f"正在创建 {count} 条系统日志...")
    
    levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
    modules = [
        "API.MatchController", "API.UserController", "API.SPController", 
        "Service.DataProcessor", "Service.Scheduler", "Service.Crawler",
        "Database.Connection", "Auth.Service", "Cache.Manager"
    ]
    
    for i in range(count):
        log_entry = LogEntry(
            timestamp=fake.date_time_between(start_date='-7d', end_date='now'),
            level=random.choice(levels),
            module=random.choice(modules),
            message=fake.sentence(nb_words=10),
            extra_data=json.dumps({
                "user_id": random.randint(1, 100),
                "session_id": fake.uuid4(),
                "ip_address": fake.ipv4(),
                "user_agent": fake.user_agent(),
                "request_path": fake.uri_path() or "/api/test/path",
                "execution_time": round(random.uniform(10, 5000), 2)
            })
        )
        db_session.add(log_entry)
        
        if (i + 1) % 20 == 0:
            print(f"已创建 {i + 1} 条系统日志...")
    
    db_session.commit()
    print("系统日志创建完成")


def create_sample_user_logs(db_session, count=50):
    """创建示例用户操作日志"""
    print(f"正在创建 {count} 条用户操作日志...")
    
    actions = ["create", "update", "delete", "export", "view", "login", "logout"]
    resource_types = ["user", "match", "intelligence", "odds", "system", "log"]
    methods = ["GET", "POST", "PUT", "DELETE"]
    paths = ["/api/v1/users", "/api/v1/matches", "/api/v1/intelligence", "/api/v1/odds", "/api/v1/system/logs"]
    
    for i in range(count):
        log_entry = AdminOperationLog(
            admin_id=random.randint(1, 10),
            action=random.choice(actions),
            resource_type=random.choice(resource_types),
            resource_id=str(random.randint(1, 1000)),
            resource_name=f"Resource {random.randint(1, 100)}",
            method=random.choice(methods),
            path=random.choice(paths),
            status_code=random.choice([200, 201, 400, 401, 403, 404, 500]),
            ip_address=fake.ipv4(),
            user_agent=fake.user_agent(),
            created_at=fake.date_time_between(start_date='-7d', end_date='now'),
            duration_ms=random.randint(50, 5000)
        )
        db_session.add(log_entry)
        
        if (i + 1) % 10 == 0:
            print(f"已创建 {i + 1} 条用户操作日志...")
    
    db_session.commit()
    print("用户操作日志创建完成")


def create_sample_security_logs(db_session, count=30):
    """创建示例安全日志"""
    print(f"正在创建 {count} 条安全日志...")
    
    for i in range(count):
        success = random.choice([True, False])
        log_entry = AdminLoginLog(
            admin_id=random.randint(1, 10),
            login_at=fake.date_time_between(start_date='-7d', end_date='now'),
            login_ip=fake.ipv4(),
            success=success,
            failure_reason=fake.sentence(nb_words=5) if not success else None,
            user_agent=fake.user_agent()
        )
        db_session.add(log_entry)
        
        if (i + 1) % 10 == 0:
            print(f"已创建 {i + 1} 条安全日志...")
    
    db_session.commit()
    print("安全日志创建完成")


def create_sample_api_logs(db_session, count=40):
    """创建示例API日志"""
    print(f"正在创建 {count} 条API日志...")
    
    statuses = ["success", "failed", "timeout"]
    
    for i in range(count):
        started = fake.date_time_between(start_date='-7d', end_date='now')
        completed = fake.date_time_between(start_date=started, end_date='now') if random.random() > 0.2 else None
        duration = (completed - started).total_seconds() if completed else None
        records = random.randint(10, 1000) if random.random() > 0.5 else 0
        
        log_entry = CrawlerTaskLog(
            task_id=random.randint(1, 100),
            source_id=random.randint(1, 5),
            status=random.choice(statuses),
            started_at=started,
            completed_at=completed,
            duration_seconds=duration,
            records_processed=records if records > 0 else None,
            records_success=random.randint(0, records) if records > 0 else None,
            records_failed=random.randint(0, records) if records > 0 else None,
            response_time_ms=round(random.uniform(100, 5000), 2),
            error_message=fake.sentence(nb_words=5) if random.random() < 0.3 else None,
            error_details=None,  # 设置为None以避免MutableDict问题
            created_by=random.randint(1, 10) if random.random() > 0.5 else None,
            created_at=fake.date_time_between(start_date='-7d', end_date='now')
        )
        db_session.add(log_entry)
        
        if (i + 1) % 10 == 0:
            print(f"已创建 {i + 1} 条API日志...")
    
    db_session.commit()
    print("API日志创建完成")


def main():
    """主函数"""
    print("开始填充日志数据...")
    
    # 导入配置获取数据库URL
    try:
        from backend.config import settings
        database_url = settings.DATABASE_URL
    except ImportError:
        # 回退方案
        from backend.config import DATA_DIR, ABS_DB_PATH
        database_url = f"sqlite:///{ABS_DB_PATH}"
    
    # 直接创建数据库引擎和会话，绕过get_db
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)  # 创建所有表（如果不存在）
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 创建不同类型日志
        create_sample_logs(db, 100)
        # 创建用户操作日志（已修复MutableDict问题）
        create_sample_user_logs(db, 50)
        create_sample_security_logs(db, 30)
        create_sample_api_logs(db, 40)
        
        print("所有日志数据填充完成！")
    except Exception as e:
        print(f"填充日志数据时发生错误: {repr(e)}")
        db.rollback()
    finally:
        try:
            db.close()
        except:
            pass


if __name__ == "__main__":
    main()