# 数据库索引优化和业务视图创建指南

## 📋 概述

本文档详细说明了体育彩票扫盘系统数据库索引优化、业务视图创建和数据清理策略的实施方法。

### 优化目标
- **性能提升**: 查询响应时间减少60-80%
- **存储优化**: 清理过期数据，回收存储空间
- **分析增强**: 通过业务视图简化复杂查询
- **监控完善**: 建立系统健康监控体系

## 🔍 第一阶段：索引策略审计

### 1.1 现有索引分析

#### 索引分布概况
根据审计结果，系统包含以下主要表的索引情况：

| 表名 | 记录数 | 现有索引数 | 关键字段 |
|------|--------|------------|----------|
| users | ~1,000 | 15+ | username, email, status, role |
| matches | ~5,000 | 12+ | match_date, status, league_id |
| leagues | ~100 | 8+ | country, is_active, level |
| teams | ~500 | 8+ | country, league_id, is_active |
| user_login_logs | ~10,000 | 6+ | user_id, login_at, success |
| user_activities | ~50,000 | 6+ | user_id, activity_time, resource_type |

#### 发现的索引问题
1. **缺少复合索引**: 多字段查询条件缺乏优化
2. **时间范围查询慢**: 登录日志和活动记录按时间查询效率低
3. **状态筛选低效**: 比赛状态+日期组合查询无合适索引
4. **关联查询缺索引**: 团队-比赛关联查询性能差

### 1.2 高优先级索引建议

#### 用户相关索引
```sql
-- 用户名和邮箱唯一性保证（如果还没有）
CREATE UNIQUE INDEX idx_users_username_unique ON users(username);
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- 用户状态和角色组合查询
CREATE INDEX idx_users_status_role ON users(status, role);

-- 用户登录时间范围查询
CREATE INDEX idx_users_last_login ON users(last_login_at);
```

#### 比赛相关索引
```sql
-- 比赛日期和状态组合（最常用查询）
CREATE INDEX idx_matches_date_status ON matches(match_date, status);

-- 联赛和日期组合查询
CREATE INDEX idx_matches_league_date ON matches(league_id, match_date);

-- 主客队和日期组合（避免笛卡尔积）
CREATE INDEX idx_matches_teams_date ON matches(home_team_id, away_team_id, match_date);

-- 比赛重要性和发布状态
CREATE INDEX idx_matches_importance_published ON matches(importance, is_published);
```

#### 登录日志索引
```sql
-- 用户登录时间序列分析
CREATE INDEX idx_login_logs_user_time ON user_login_logs(user_id, login_at);

-- IP地址登录分析
CREATE INDEX idx_login_logs_ip_time ON user_login_logs(login_ip, login_at);

-- 登录成功状态分析
CREATE INDEX idx_login_logs_success_time ON user_login_logs(success, login_at);
```

## 📊 第二阶段：关键业务视图

### 2.1 视图设计原则

1. **性能优先**: 预聚合常用查询结果
2. **业务逻辑**: 封装复杂的业务计算
3. **数据安全**: 隐藏敏感字段，提供干净的数据接口
4. **维护性**: 视图逻辑集中管理，便于修改

### 2.2 核心业务视图详解

#### vw_active_matches_today - 今日活跃比赛视图
**用途**: 首页展示今日所有比赛，支持按重要性排序

```sql
CREATE VIEW vw_active_matches_today AS
SELECT 
    m.id,
    m.match_identifier,
    m.match_date,
    m.scheduled_kickoff,
    m.status,
    m.importance,
    l.name as league_name,
    l.code as league_code,
    ht.name as home_team_name,
    at.name as away_team_name,
    m.home_score,
    m.away_score,
    m.is_featured,
    m.popularity
FROM matches m
LEFT JOIN leagues l ON m.league_id = l.id
LEFT JOIN teams ht ON m.home_team_id = ht.id
LEFT JOIN teams at ON m.away_team_id = at.id
WHERE m.match_date = date('now')
AND m.is_published = 1
ORDER BY m.importance DESC, m.scheduled_kickoff ASC;
```

**使用场景**:
- 首页今日比赛列表
- 移动端比赛推送
- 比赛提醒功能

#### vw_user_login_stats - 用户登录统计视图
**用途**: 分析用户登录行为和活跃度模式

```sql
CREATE VIEW vw_user_login_stats AS
SELECT 
    u.id as user_id,
    u.username,
    u.email,
    u.role,
    u.status,
    COUNT(ull.id) as total_logins,
    COUNT(CASE WHEN ull.success = 1 THEN 1 END) as successful_logins,
    COUNT(CASE WHEN ull.success = 0 THEN 1 END) as failed_logins,
    MAX(ull.login_at) as last_login,
    MIN(ull.login_at) as first_login,
    COUNT(DISTINCT DATE(ull.login_at)) as active_days
FROM users u
LEFT JOIN user_login_logs ull ON u.id = ull.user_id
GROUP BY u.id, u.username, u.email, u.role, u.status;
```

**使用场景**:
- 用户活跃度分析
- 安全风险评估
- 运营数据统计

#### vw_match_intelligence_summary - 比赛情报汇总视图
**用途**: 整合比赛相关所有情报，便于分析和展示

```sql
CREATE VIEW vw_match_intelligence_summary AS
SELECT 
    m.id as match_id,
    m.match_identifier,
    m.match_date,
    m.status,
    l.name as league_name,
    ht.name as home_team_name,
    at.name as away_team_name,
    COUNT(i.id) as total_intelligence_items,
    COUNT(CASE WHEN i.confidence_level >= 0.8 THEN 1 END) as high_confidence_items,
    COUNT(CASE WHEN i.category = 'injury' THEN 1 END) as injury_items,
    COUNT(CASE WHEN i.category = 'transfer' THEN 1 END) as transfer_items,
    COUNT(CASE WHEN i.category = 'weather' THEN 1 END) as weather_items,
    MAX(i.created_at) as latest_intelligence
FROM matches m
LEFT JOIN leagues l ON m.league_id = l.id
LEFT JOIN teams ht ON m.home_team_id = ht.id
LEFT JOIN teams at ON m.away_team_id = at.id
LEFT JOIN intelligence i ON m.id = i.match_id
WHERE m.is_published = 1
GROUP BY m.id, m.match_identifier, m.match_date, m.status, l.name, ht.name, at.name;
```

**使用场景**:
- 比赛详情页情报展示
- 情报质量分析
- 预测模型特征工程

#### vw_popular_leagues - 热门联赛视图
**用途**: 展示最受欢迎的联赛排行，支持运营决策

```sql
CREATE VIEW vw_popular_leagues AS
SELECT 
    l.id,
    l.name,
    l.code,
    l.country,
    l.level,
    l.total_matches,
    l.total_views,
    l.total_followers,
    l.is_popular,
    COUNT(m.id) as upcoming_matches,
    AVG(CASE WHEN m.home_score IS NOT NULL AND m.away_score IS NOT NULL 
        THEN CAST(m.home_score AS FLOAT) / (m.home_score + m.away_score + 0.001) 
        ELSE NULL END) as avg_home_win_rate
FROM leagues l
LEFT JOIN matches m ON l.id = m.league_id 
    AND m.match_date >= date('now')
    AND m.status = 'scheduled'
WHERE l.is_active = 1
GROUP BY l.id, l.name, l.code, l.country, l.level, l.total_matches, 
         l.total_views, l.total_followers, l.is_popular
ORDER BY l.is_popular DESC, l.level ASC, l.total_views DESC;
```

**使用场景**:
- 联赛推荐算法
- 内容运营重点
- 用户兴趣分析

#### vw_system_health_metrics - 系统健康指标视图
**用途**: 实时监控数据库和系统运行状态

```sql
CREATE VIEW vw_system_health_metrics AS
SELECT 
    'Database Size' as metric_name,
    ROUND(CAST(page_count * page_size AS FLOAT) / 1024 / 1024, 2) as metric_value,
    'MB' as unit,
    datetime('now') as measured_at
FROM pragma_page_count(), pragma_page_size()
UNION ALL
SELECT 
    'Total Users' as metric_name,
    COUNT(*) as metric_value,
    'count' as unit,
    datetime('now') as measured_at
FROM users
UNION ALL
SELECT 
    'Active Matches Today' as metric_name,
    COUNT(*) as metric_value,
    'count' as unit,
    datetime('now') as measured_at
FROM matches 
WHERE match_date = date('now') AND is_published = 1
UNION ALL
SELECT 
    'Failed Login Attempts (24h)' as metric_name,
    COUNT(*) as metric_value,
    'count' as unit,
    datetime('now') as measured_at
FROM user_login_logs 
WHERE success = 0 AND login_at >= datetime('now', '-24 hours');
```

**使用场景**:
- 系统监控仪表板
- 运维告警阈值
- 容量规划参考

## 🧹 第三阶段：数据清理策略

### 3.1 数据保留政策

| 数据类型 | 保留期限 | 清理频率 | 说明 |
|----------|----------|----------|------|
| 登录日志 | 90天 | 每周 | 保留足够时间用于安全分析 |
| 用户活动 | 180天 | 每月 | 保留半年用于行为分析 |
| 失败登录 | 30天 | 每日 | 快速清理减少噪音 |
| 爬虫日志 | 60天 | 每月 | 调试需要，不需长期保存 |
| 临时数据 | 7天 | 每日 | 自动清理临时文件 |

### 3.2 清理脚本实现

#### 自动化清理任务
```python
# 添加到定时任务 (crontab 或 Windows Task Scheduler)
# 每周日凌晨2点执行数据清理
0 2 * * 0 cd /path/to/project && python scripts/run_data_cleanup.py

# 每日凌晨1点清理失败登录记录
0 1 * * * cd /path/to/project && python scripts/cleanup_failed_logins.py
```

#### 清理SQL示例
```sql
-- 清理90天前的登录日志
DELETE FROM user_login_logs 
WHERE login_at < datetime('now', '-90 days');

-- 清理180天前的用户活动
DELETE FROM user_activities 
WHERE activity_time < datetime('now', '-180 days');

-- 清理30天前的失败登录
DELETE FROM user_login_logs 
WHERE success = 0 AND login_at < datetime('now', '-30 days');

-- 执行清理后优化
VACUUM;
ANALYZE;
```

### 3.3 数据归档策略

对于需要长期保存的历史数据，建议采用归档策略：

1. **月度归档**: 将上月数据导出到归档表
2. **压缩存储**: 使用SQLite的VACUUM压缩归档数据
3. **冷热分离**: 热数据在主库，冷数据在归档库
4. **快速恢复**: 保持归档数据的可查询性

## ⚡ 第四阶段：性能优化实施

### 4.1 索引创建最佳实践

1. **监控索引使用**: 定期检查索引是否被有效使用
2. **避免过度索引**: 每个额外索引都会降低写入性能
3. **定期重建**: SQLite索引会碎片化，需要定期重建
4. **测试验证**: 在生产环境应用前先在测试环境验证

### 4.2 查询优化建议

#### 常见查询模式优化
```sql
-- ❌ 低效查询：没有合适索引
SELECT * FROM matches 
WHERE match_date BETWEEN '2024-01-01' AND '2024-01-31'
AND status = 'finished'
ORDER BY importance DESC;

-- ✅ 优化后：使用复合索引
-- 创建索引: CREATE INDEX idx_matches_date_status_importance ON matches(match_date, status, importance);
SELECT id, match_identifier, home_team_id, away_team_id, home_score, away_score
FROM matches 
WHERE match_date BETWEEN '2024-01-01' AND '2024-01-31'
AND status = 'finished'
ORDER BY importance DESC;
```

#### 分页查询优化
```sql
-- ❌ 深度分页性能差
SELECT * FROM user_activities 
ORDER BY activity_time DESC 
LIMIT 20 OFFSET 10000;

-- ✅ 使用游标分页
SELECT * FROM user_activities 
WHERE activity_time < '2024-01-20 10:00:00'
ORDER BY activity_time DESC 
LIMIT 20;
```

### 4.3 数据库配置优化

#### SQLite优化配置
```python
# 在数据库连接中添加优化参数
import sqlite3

conn = sqlite3.connect(
    'sport_lottery.db',
    timeout=30.0,  # 增加超时时间
    isolation_level=None,  # 自动提交模式
    check_same_thread=False  # 允许多线程访问
)

# 启用性能优化PRAGMA
cursor = conn.cursor()
cursor.execute("PRAGMA journal_mode=WAL")  # 写前日志模式
cursor.execute("PRAGMA synchronous=NORMAL")  # 同步模式
cursor.execute("PRAGMA cache_size=10000")   # 增加缓存大小
cursor.execute("PRAGMA temp_store=MEMORY")  # 临时表存储在内存
```

## 📈 第五阶段：监控和维护

### 5.1 性能监控指标

1. **查询响应时间**: 关键业务查询的平均响应时间
2. **索引命中率**: 查询使用索引的比例
3. **数据库大小**: 数据文件增长趋势
4. **并发连接数**: 同时访问的用户数量
5. **锁等待时间**: 数据库锁竞争情况

### 5.2 定期维护任务

| 任务 | 频率 | 说明 |
|------|------|------|
| 索引分析 | 每周 | 检查索引使用情况和效率 |
| 统计更新 | 每日 | 执行ANALYZE更新查询计划 |
| 空间回收 | 每月 | 执行VACUUM回收碎片空间 |
| 日志清理 | 每日 | 清理应用和数据库日志 |
| 备份验证 | 每周 | 验证备份文件的完整性 |

### 5.3 故障排除指南

#### 常见问题及解决方案

1. **查询变慢**
   - 检查是否有合适的索引
   - 分析查询执行计划
   - 考虑数据量增长导致的性能下降

2. **数据库锁定**
   - 检查长时间运行的事务
   - 优化批量操作的分批大小
   - 考虑读写分离策略

3. **磁盘空间不足**
   - 执行数据清理任务
   - 检查是否有异常大的日志文件
   - 考虑数据归档策略

## 🚀 执行检查清单

### 部署前检查
- [ ] 备份生产数据库
- [ ] 在测试环境验证所有索引和视图
- [ ] 准备回滚方案
- [ ] 通知相关团队成员

### 执行过程
- [ ] 选择业务低峰期执行
- [ ] 逐个应用索引，观察系统负载
- [ ] 验证业务视图返回正确结果
- [ ] 监控数据库性能指标

### 部署后验证
- [ ] 测试关键业务功能的响应时间
- [ ] 验证数据完整性和一致性
- [ ] 更新监控和告警阈值
- [ ] 记录优化效果和后续建议

## 📞 技术支持

如在执行过程中遇到问题，请参考以下资源：
- 项目技术文档: `docs/` 目录
- 数据库模型定义: `backend/models/` 目录
- 执行脚本: `scripts/database_index_optimizer.py`
- 优化工具: `scripts/run_database_optimization.py`

---

**版本**: v1.0  
**创建时间**: 2024年1月  
**维护团队**: 体育彩票扫盘系统开发组