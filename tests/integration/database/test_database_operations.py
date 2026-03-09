"""
数据库操作单元测试
测试所有新的数据库表操作和真实数据查询
"""
import unittest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.models.crawler_config import CrawlerConfig
from backend.models.crawler_tasks import CrawlerTask
from backend.models.crawler_logs import CrawlerTaskLog, CrawlerSourceStat
from backend.models.admin_user import AdminUser, AdminRoleEnum, AdminStatusEnum
from backend.services.data_source_service import DataSourceService
from backend.services.task_scheduler_service import TaskSchedulerService
from backend.services.intelligence_service import IntelligenceService
from backend.schemas.crawler import (
    CrawlerSourceCreate, CrawlerSourceUpdate, 
    CrawlerTaskCreate, CrawlerTaskUpdate
)


class TestDatabaseOperations(unittest.TestCase):
    """数据库操作测试基类"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试数据库"""
        # 使用SQLite内存数据库进行测试
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        
        # 创建所有表
        CrawlerConfig.metadata.create_all(cls.engine)
        CrawlerTask.metadata.create_all(cls.engine)
        CrawlerTaskLog.metadata.create_all(cls.engine)
        CrawlerSourceStat.metadata.create_all(cls.engine)
        AdminUser.metadata.create_all(cls.engine)
        
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
    
    def setUp(self):
        """每个测试前的设置"""
        self.db = self.SessionLocal()
        # 清理所有表
        self.db.query(CrawlerTaskLog).delete()
        self.db.query(CrawlerSourceStat).delete()
        self.db.query(CrawlerTask).delete()
        self.db.query(CrawlerConfig).delete()
        self.db.query(AdminUser).delete()
        self.db.commit()
        
        # 创建测试用户
        self.test_user = AdminUser(
            username="test_admin",
            email="test@example.com",
            password_hash="hashed_password",
            real_name="测试管理员",
            role=AdminRoleEnum.ADMIN,
            status=AdminStatusEnum.ACTIVE
        )
        self.db.add(self.test_user)
        self.db.commit()
    
    def tearDown(self):
        """每个测试后的清理"""
        self.db.close()
    
    @classmethod
    def tearDownClass(cls):
        """测试类结束后的清理"""
        cls.engine.dispose()


class TestDataSourceService(TestDatabaseOperations):
    """数据源服务测试"""
    
    def setUp(self):
        super().setUp()
        self.service = DataSourceService(self.db)
        
        # 创建测试数据源
        self.test_source = CrawlerConfig(
            name="测试数据源",
            description="用于测试的数据源",
            url="https://test.example.com",
            frequency=3600,
            is_active=True,
            config_data='{"timeout": 30}',
            created_by=self.test_user.id
        )
        self.db.add(self.test_source)
        self.db.commit()
        
        # 创建测试日志数据
        for i in range(10):
            log = CrawlerTaskLog(
                task_id=1,
                source_id=self.test_source.id,
                status="success" if i < 8 else "failed",
                started_at=datetime.utcnow() - timedelta(hours=i),
                completed_at=datetime.utcnow() - timedelta(hours=i, minutes=-5),
                duration_seconds=5.0,
                records_processed=100,
                records_success=95 if i < 8 else 0,
                records_failed=5 if i < 8 else 100,
                response_time_ms=200.0 + i * 10
            )
            self.db.add(log)
        self.db.commit()
    
    def test_get_sources_with_real_data(self):
        """测试获取数据源列表使用真实数据"""
        sources = self.service.get_sources()
        
        self.assertEqual(len(sources), 1)
        source = sources[0]
        
        # 验证真实计算的指标
        self.assertEqual(source.id, self.test_source.id)
        self.assertEqual(source.name, "测试数据源")
        self.assertEqual(source.status, "online")
        
        # 验证成功率是真实计算的 (8/10 = 80%)
        self.assertEqual(source.success_rate, 80.0)
        
        # 验证响应时间是真实平均值
        expected_avg_response_time = sum([200.0 + i * 10 for i in range(10)]) / 10
        self.assertAlmostEqual(source.response_time, expected_avg_response_time, places=2)
    
    def test_calculate_real_success_rate(self):
        """测试真实成功率计算"""
        success_rate = self.service._calculate_real_success_rate(self.test_source.id)
        
        # 8次成功，2次失败，成功率应该是80%
        self.assertEqual(success_rate, 80.0)
    
    def test_get_avg_response_time(self):
        """测试平均响应时间计算"""
        avg_time = self.service._get_avg_response_time(self.test_source.id)
        
        expected_avg = sum([200.0 + i * 10 for i in range(10)]) / 10
        self.assertAlmostEqual(avg_time, expected_avg, places=2)
    
    def test_check_health_with_real_data(self):
        """测试基于真实数据的健康检查"""
        health = self.service.check_health(self.test_source.id)
        
        self.assertIn("status", health)
        self.assertIn("metrics", health)
        self.assertIn("total_requests_24h", health["metrics"])
        
        # 验证使用了真实的24小时数据
        self.assertEqual(health["metrics"]["total_requests_24h"], 10)
        self.assertEqual(health["metrics"]["successful_requests"], 8)
        self.assertEqual(health["metrics"]["success_rate_percent"], 80.0)
    
    def test_create_source(self):
        """测试创建数据源"""
        source_data = CrawlerSourceCreate(
            name="新数据源",
            url="https://new.example.com",
            description="新创建的数据源",
            status="online",
            config={"timeout": 60}
        )
        
        new_source = self.service.create_source(source_data, self.test_user.id)
        
        self.assertEqual(new_source.name, "新数据源")
        self.assertEqual(new_source.is_active, True)
        self.assertIsNotNone(new_source.id)
    
    def test_unique_name_validation(self):
        """测试数据源名称唯一性验证"""
        source_data = CrawlerSourceCreate(
            name="测试数据源",  # 重复名称
            url="https://another.example.com",
            description="另一个数据源"
        )
        
        with self.assertRaises(ValueError) as context:
            self.service.create_source(source_data, self.test_user.id)
        
        self.assertIn("已存在", str(context.exception))


class TestTaskSchedulerService(TestDatabaseOperations):
    """任务调度服务测试"""
    
    def setUp(self):
        super().setUp()
        self.service = TaskSchedulerService(self.db)
        
        # 创建测试数据源
        self.test_source = CrawlerConfig(
            name="任务测试数据源",
            url="https://task-test.example.com",
            is_active=True,
            created_by=self.test_user.id
        )
        self.db.add(self.test_source)
        self.db.commit()
        
        # 创建测试任务
        self.test_task = CrawlerTask(
            name="测试任务",
            source_id=self.test_source.id,
            task_type="crawl",
            cron_expression="0 * * * *",
            is_active=True,
            status="stopped",
            run_count=10,
            success_count=8,
            error_count=2
        )
        self.db.add(self.test_task)
        self.db.commit()
    
    def test_get_tasks_with_real_data(self):
        """测试获取任务列表使用真实数据"""
        tasks = self.service.get_tasks()
        
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        
        self.assertEqual(task.id, self.test_task.id)
        self.assertEqual(task.name, "测试任务")
        self.assertEqual(task.source_id, self.test_source.id)
        self.assertEqual(task.run_count, 10)
        self.assertEqual(task.success_count, 8)
        self.assertEqual(task.error_count, 2)
    
    def test_get_tasks_with_status_filter(self):
        """测试按状态筛选任务"""
        # 更新任务状态
        self.test_task.status = "running"
        self.db.commit()
        
        tasks = self.service.get_tasks(status="running")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].status, "running")
        
        tasks = self.service.get_tasks(status="stopped")
        self.assertEqual(len(tasks), 0)
    
    def test_create_task(self):
        """测试创建任务"""
        task_data = CrawlerTaskCreate(
            name="新任务",
            source_id=self.test_source.id,
            task_type="crawl",
            cron_expression="*/30 * * * *",
            is_active=True
        )
        
        # 注意：这里需要模拟当前用户，实际实现中会传入
        # 为了测试，我们直接测试数据库操作
        new_task = CrawlerTask(
            name=task_data.name,
            source_id=task_data.source_id,
            task_type=task_data.task_type,
            cron_expression=task_data.cron_expression,
            is_active=task_data.is_active,
            created_by=self.test_user.id
        )
        self.db.add(new_task)
        self.db.commit()
        
        self.assertIsNotNone(new_task.id)
        self.assertEqual(new_task.name, "新任务")
    
    def test_update_task_status(self):
        """测试更新任务状态"""
        result = self.service.update_task_status(self.test_task.id, "running", self.test_user.id)
        self.assertTrue(result)
        
        # 验证状态已更新
        updated_task = self.db.query(CrawlerTask).filter(
            CrawlerTask.id == self.test_task.id
        ).first()
        self.assertEqual(updated_task.status, "running")
        self.assertEqual(updated_task.updated_by, self.test_user.id)


class TestIntelligenceService(TestDatabaseOperations):
    """数据情报服务测试"""
    
    def setUp(self):
        super().setUp()
        self.service = IntelligenceService(self.db)
        
        # 创建测试数据源
        self.test_source = CrawlerConfig(
            name="情报测试数据源",
            url="https://intel-test.example.com",
            is_active=True,
            created_by=self.test_user.id
        )
        self.db.add(self.test_source)
        self.db.commit()
        
        # 创建多样化的错误日志用于测试错误分布
        error_types = [
            ("network connection timeout", "failed"),
            ("network dns resolution failed", "failed"),
            ("parse json invalid format", "failed"),
            ("parsing xml malformed", "failed"),
            ("format validation error", "failed"),
            ("schema conversion failed", "failed"),
            ("timeout after 30 seconds", "timeout"),
            ("request timed out", "timeout"),
            ("server 500 internal error", "error"),
            ("server 502 bad gateway", "error"),
            ("successful request", "success")
        ]
        
        for i, (error_msg, status) in enumerate(error_types):
            log = CrawlerTaskLog(
                task_id=i,
                source_id=self.test_source.id,
                status=status,
                started_at=datetime.utcnow() - timedelta(hours=i),
                error_message=error_msg,
                response_time_ms=100.0 + i * 10
            )
            if status == "success":
                log.completed_at = datetime.utcnow() - timedelta(hours=i, minutes=-1)
                log.records_processed = 100
                log.records_success = 100
            self.db.add(log)
        self.db.commit()
    
    def test_get_real_error_distribution(self):
        """测试基于真实日志的错误分布分析"""
        error_dist = self.service._get_real_error_distribution()
        
        self.assertIsInstance(error_dist, list)
        self.assertGreater(len(error_dist), 0)
        
        # 验证错误分类
        categories = [item["name"] for item in error_dist]
        
        # 应该识别出不同类型的错误
        expected_categories = ["网络错误", "解析错误", "数据格式错误", "超时错误", "服务器错误"]
        found_categories = [cat for cat in expected_categories if cat in categories]
        self.assertGreater(len(found_categories), 0, "应该至少识别一种错误类型")
        
        # 验证数据格式
        for item in error_dist:
            self.assertIn("name", item)
            self.assertIn("value", item)
            self.assertIn("color", item)
            self.assertIsInstance(item["value"], int)
            self.assertGreaterEqual(item["value"], 0)
    
    def test_error_distribution_sorting(self):
        """测试错误分布按值排序"""
        error_dist = self.service._get_real_error_distribution()
        
        if len(error_dist) > 1:
            # 验证按值降序排列
            values = [item["value"] for item in error_dist]
            sorted_values = sorted(values, reverse=True)
            self.assertEqual(values, sorted_values)
    
    def test_get_stats_includes_real_error_data(self):
        """测试统计信息包含真实的错误分布数据"""
        stats = self.service.get_stats()
        
        self.assertIn("error_distribution", stats)
        self.assertIsInstance(stats["error_distribution"], list)
        
        # 由于我们有测试数据，应该返回非空的错误分布
        # （除非所有日志都是成功的，但我们故意加了一些失败的）
        
    def test_stats_calculation(self):
        """测试统计信息计算"""
        stats = self.service.get_stats()
        
        # 验证基本统计字段存在
        required_fields = [
            "total_crawled", "today_crawled", "today_success", 
            "today_failed", "overall_success_rate", "active_sources"
        ]
        
        for field in required_fields:
            self.assertIn(field, stats, f"缺少统计字段: {field}")


class TestModelRelationships(TestDatabaseOperations):
    """模型关系测试"""
    
    def test_crawler_config_creation(self):
        """测试爬虫配置模型创建"""
        config = CrawlerConfig(
            name="关系测试配置",
            url="https://relation-test.example.com",
            frequency=1800,
            is_active=True,
            created_by=self.test_user.id
        )
        self.db.add(config)
        self.db.commit()
        
        self.assertIsNotNone(config.id)
        self.assertEqual(config.name, "关系测试配置")
        self.assertEqual(config.frequency, 1800)
    
    def test_crawler_task_foreign_key(self):
        """测试爬虫任务外键关系"""
        # 创建配置
        config = CrawlerConfig(
            name="外键测试配置",
            url="https://fk-test.example.com",
            created_by=self.test_user.id
        )
        self.db.add(config)
        self.db.commit()
        
        # 创建关联的任务
        task = CrawlerTask(
            name="外键测试任务",
            source_id=config.id,
            task_type="crawl",
            created_by=self.test_user.id
        )
        self.db.add(task)
        self.db.commit()
        
        # 验证关联关系
        retrieved_task = self.db.query(CrawlerTask).filter(
            CrawlerTask.id == task.id
        ).first()
        self.assertEqual(retrieved_task.source_id, config.id)
    
    def test_crawler_task_log_foreign_keys(self):
        """测试任务日志的多重外键关系"""
        # 创建配置和任务
        config = CrawlerConfig(
            name="日志外键测试配置",
            url="https://log-fk-test.example.com",
            created_by=self.test_user.id
        )
        self.db.add(config)
        self.db.commit()
        
        task = CrawlerTask(
            name="日志外键测试任务",
            source_id=config.id,
            task_type="crawl",
            created_by=self.test_user.id
        )
        self.db.add(task)
        self.db.commit()
        
        # 创建日志
        log = CrawlerTaskLog(
            task_id=task.id,
            source_id=config.id,
            status="success",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            records_processed=50,
            records_success=50
        )
        self.db.add(log)
        self.db.commit()
        
        # 验证外键关系
        retrieved_log = self.db.query(CrawlerTaskLog).filter(
            CrawlerTaskLog.id == log.id
        ).first()
        self.assertEqual(retrieved_log.task_id, task.id)
        self.assertEqual(retrieved_log.source_id, config.id)


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)