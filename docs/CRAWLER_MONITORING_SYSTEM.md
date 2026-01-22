# 爬虫监控系统使用说明

## 概述

本项目已实现了一套完整的爬虫监控系统，包括实时监控、告警机制、数据统计和可视化仪表板。该系统能够自动监控爬虫运行状态，及时发现问题并通过多种渠道发送告警通知。

## 系统架构

### 核心组件

1. **数据采集层**
   - `CrawlerTaskLog`: 爬虫任务执行日志
   - `CrawlerSourceStat`: 数据源统计信息
   - `CrawlerMetric`: 监控指标数据

2. **告警规则层**
   - `CrawlerAlertRule`: 告警规则配置
   - `CrawlerAlertRecord`: 告警记录

3. **服务层**
   - `CrawlerAlertService`: 告警服务业务逻辑
   - `EnhancedCrawlerService`: 增强的爬虫服务（集成监控）

4. **任务层**
   - `alert_monitoring_tasks`: 告警监控定时任务

5. **API层**
   - 告警管理API (`/admin/crawler-alert/*`)
   - 监控仪表板API (`/admin/monitoring/*`)

## 告警规则类型

### 1. 错误率告警 (error_rate)
- **用途**: 监控爬虫请求失败率
- **阈值示例**: 20% (警告), 50% (严重)
- **时间窗口**: 60分钟
- **适用场景**: 检测数据源不可用、网络问题等

### 2. 响应时间告警 (response_time)
- **用途**: 监控爬虫响应时间性能
- **阈值示例**: 5000ms (警告), 10000ms (严重)
- **时间窗口**: 60分钟
- **适用场景**: 检测性能下降、服务器负载过高等

### 3. 连续失败告警 (consecutive_failures)
- **用途**: 监控连续失败次数
- **阈值示例**: 5次 (警告), 10次 (严重)
- **时间窗口**: 120分钟
- **适用场景**: 检测系统性故障、配置错误等

### 4. 数据质量告警 (data_quality)
- **用途**: 监控数据质量分数
- **阈值示例**: 80分 (警告), 60分 (严重)
- **时间窗口**: 120分钟
- **适用场景**: 检测数据不完整、格式错误等

## 安装和配置

### 1. 数据库迁移

系统已通过Alembic迁移添加了必要的监控表：

```bash
# 查看迁移文件
ls alembic/versions/*alert*.py

# 如果需要重新应用迁移
cd backend
alembic upgrade head
```

### 2. 初始化默认告警规则

```bash
# 运行初始化脚本
cd sport-lottery-sweeper
python scripts/init_default_alert_rules.py
```

### 3. Celery任务配置

在 `celery_app.py` 中确保已导入告警监控任务：

```python
from . import alert_monitoring_tasks
```

## 使用方法

### 1. 告警规则管理

#### 创建告警规则
```bash
POST /admin/crawler-alert/rules
Content-Type: application/json
Authorization: Bearer {token}

{
  "name": "自定义错误率告警",
  "description": "监控特定数据源的错误率",
  "metric_type": "error_rate",
  "threshold": 15.0,
  "comparison_operator": "gt",
  "time_window_minutes": 30,
  "source_ids": [1, 2, 3],
  "alert_level": "warning",
  "notification_channels": ["email", "slack"]
}
```

#### 获取告警规则列表
```bash
GET /admin/crawler-alert/rules?active_only=true
Authorization: Bearer {token}
```

#### 更新告警规则
```bash
PUT /admin/crawler-alert/rules/{rule_id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "threshold": 25.0,
  "is_active": true
}
```

#### 删除告警规则
```bash
DELETE /admin/crawler-alert/rules/{rule_id}
Authorization: Bearer {token}
```

### 2. 告警检查

#### 手动触发告警检查
```bash
POST /admin/crawler-alert/check
Authorization: Bearer {token}
```

#### 获取告警记录
```bash
GET /admin/crawler-alert/records?status=active&limit=50
Authorization: Bearer {token}
```

#### 解决告警
```bash
POST /admin/crawler-alert/records/{alert_id}/resolve
Authorization: Bearer {token}
```

### 3. 监控仪表板

#### 获取监控概览
```bash
GET /admin/monitoring/dashboard/overview
Authorization: Bearer {token}
```

#### 获取数据源性能
```bash
GET /admin/monitoring/dashboard/source-performance?hours=24
Authorization: Bearer {token}
```

#### 获取告警趋势
```bash
GET /admin/monitoring/dashboard/alert-trends?days=7
Authorization: Bearer {token}
```

#### 获取实时指标
```bash
GET /admin/monitoring/dashboard/realtime-metrics
Authorization: Bearer {token}
```

#### 获取主要问题排行
```bash
GET /admin/monitoring/dashboard/top-issues?limit=10
Authorization: Bearer {token}
```

## Celery定时任务

### 已配置的监控任务

1. **告警检查任务**
   ```python
   tasks.alert_monitoring.check_crawler_alerts
   ```
   - 建议频率: 每5分钟执行一次
   - 功能: 检查所有告警规则，触发符合条件的告警

2. **指标收集任务**
   ```python
   tasks.alert_monitoring.collect_crawler_metrics
   ```
   - 建议频率: 每1分钟执行一次
   - 功能: 收集爬虫运行时指标并存储

3. **清理旧记录任务**
   ```python
   tasks.alert_monitoring.cleanup_old_alert_records
   ```
   - 建议频率: 每天执行一次
   - 功能: 清理过期的告警记录

4. **每日报告任务**
   ```python
   tasks.alert_monitoring.generate_daily_alert_report
   ```
   - 建议频率: 每天凌晨执行
   - 功能: 生成昨日告警统计报告

### 配置Celery Beat

在 `celery_app.py` 中添加定时任务配置：

```python
from celery.schedules import crontab

beat_schedule = {
    # 其他任务...
    
    # 告警检查 - 每5分钟
    'check-crawler-alerts': {
        'task': 'tasks.alert_monitoring.check_crawler_alerts',
        'schedule': 300.0,  # 5分钟
    },
    
    # 指标收集 - 每分钟
    'collect-crawler-metrics': {
        'task': 'tasks.alert_monitoring.collect_crawler_metrics',
        'schedule': 60.0,  # 1分钟
    },
    
    # 清理旧记录 - 每天凌晨2点
    'cleanup-old-alert-records': {
        'task': 'tasks.alert_monitoring.cleanup_old_alert_records',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # 每日报告 - 每天上午8点
    'generate-daily-alert-report': {
        'task': 'tasks.alert_monitoring.generate_daily_alert_report',
        'schedule': crontab(hour=8, minute=0),
    },
}
```

## 集成到现有爬虫

### 使用增强的爬虫服务

```python
from backend.services.enhanced_crawler_service import create_enhanced_crawler_service

# 在爬虫任务中使用
async def execute_crawler_with_monitoring(source_id: int, task_func, *args, **kwargs):
    db = SessionLocal()
    try:
        enhanced_service = create_enhanced_crawler_service(db)
        
        # 执行爬虫任务并自动记录监控指标
        result = enhanced_service.execute_crawler_task(
            task_id=task_id,
            source_id=source_id,
            task_func=task_func,
            *args, **kwargs
        )
        
        return result
        
    finally:
        db.close()
```

### 手动记录指标

```python
from backend.api.v1.crawler_alert import record_metric

# 在任何地方记录自定义指标
await record_metric(
    metric_data={
        "source_id": 1,
        "metric_type": "custom_metric",
        "metric_value": 95.5,
        "tags": {"category": "performance"}
    }
)
```

## 通知配置

### 邮件通知

在 `NotificationService` 中配置SMTP：

```python
# 在 notification_service.py 中
SMTP_CONFIG = {
    'host': 'smtp.gmail.com',
    'port': 587,
    'username': 'your-email@gmail.com',
    'password': 'your-app-password',
    'use_tls': True
}
```

### Slack通知

配置Slack Webhook URL：

```python
# 在 crawler_alert_service.py 中
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Webhook通知

配置自定义的Webhook端点：

```python
# 在系统配置中设置webhook URL
{
    "notification_channels": ["webhook"],
    "webhook_url": "https://your-system.com/webhooks/alerts"
}
```

## 监控最佳实践

### 1. 告警规则调优

- **阈值设置**: 根据实际业务需求设置合理的阈值，避免误报
- **时间窗口**: 根据爬虫执行频率调整时间窗口大小
- **冷却时间**: 设置适当的冷却时间避免告警风暴
- **分级告警**: 使用不同级别区分问题的严重程度

### 2. 性能考虑

- **指标收集频率**: 不要过于频繁地收集指标，避免影响系统性能
- **历史数据保留**: 定期清理旧的监控数据和告警记录
- **缓存策略**: 合理使用缓存减少数据库查询

### 3. 运维建议

- **定期检查**: 定期检查告警规则的有效性
- **告警疲劳**: 避免过多的低优先级告警导致运维人员疲劳
- **自动化处理**: 对于常见问题可以配置自动恢复机制
- **容量规划**: 根据监控数据做容量规划和性能优化

## 故障排除

### 常见问题

1. **告警不触发**
   - 检查告警规则是否激活
   - 确认数据源ID匹配
   - 验证阈值和条件设置
   - 检查冷却时间设置

2. **告警频繁触发**
   - 调整阈值到更合理的值
   - 增加时间窗口
   - 延长冷却时间
   - 检查是否存在系统性问题

3. **通知发送失败**
   - 检查邮件/SMS服务配置
   - 验证网络连接
   - 查看服务日志获取详细错误信息

4. **性能指标异常**
   - 检查数据库连接
   - 验证爬虫任务是否正常执行
   - 确认监控代码正确集成

### 日志位置

- 应用日志: `logs/` 目录
- Celery任务日志: 通过 `--loglevel=info` 参数控制
- 数据库日志: 取决于数据库配置

## API测试

可以使用以下命令测试API：

```bash
# 健康检查
curl http://localhost:8000/health

# 获取告警规则
curl -H "Authorization: Bearer {token}" \
     http://localhost:8000/admin/crawler-alert/rules

# 手动触发告警检查
curl -X POST -H "Authorization: Bearer {token}" \
     http://localhost:8000/admin/crawler-alert/check

# 获取监控概览
curl -H "Authorization: Bearer {token}" \
     http://localhost:8000/admin/monitoring/dashboard/overview
```

## 扩展开发

### 添加新的监控指标

1. 在 `CrawlerMetric` 模型中支持新的指标类型
2. 在 `CrawlerAlertService` 中添加对应的检查方法
3. 更新前端仪表板展示
4. 配置相应的告警规则

### 自定义通知渠道

1. 在 `NotificationService` 中添加新的通知方法
2. 在 `crawler_alert_service.py` 的 `_send_alert_notification` 方法中添加处理逻辑
3. 在告警规则的 `notification_channels` 中添加新渠道标识

## 总结

这套监控系统提供了完整的爬虫运行监控解决方案，具备：

- ✅ 实时数据采集和存储
- ✅ 灵活的告警规则配置
- ✅ 多渠道通知机制
- ✅ 可视化监控仪表板
- ✅ 自动化的定时任务
- ✅ 易于扩展的架构设计

通过合理配置和使用，可以有效提升爬虫系统的可靠性和运维效率。