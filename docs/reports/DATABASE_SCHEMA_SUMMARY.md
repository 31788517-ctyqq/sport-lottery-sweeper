# 项目数据库结构总结

## 1. 概述

该项目是一个竞彩足球扫盘系统，专业用于足球数据采集、分析和预测。数据库设计围绕着足球比赛、球队、联赛和相关情报展开，同时也包含了后台管理、爬虫配置、用户认证等功能模块。

## 2. 核心数据模型

### 2.1 比赛相关模型

#### Match（比赛表）
- **表名**: `matches`
- **主要字段**:
  - 比赛标识符（match_identifier）
  - 主客场球队ID（home_team_id, away_team_id）
  - 联赛ID（league_id）
  - 场馆ID（venue_id）
  - 比赛日期时间（match_date, match_time, scheduled_kickoff）
  - 比赛状态（status）
  - 比赛类型（type）
  - 重要性（importance）
  - 比分信息（home_score, away_score, halftime_score）
  - 外部数据源信息（external_id, external_source）
  - 发布状态（is_published）
- **关系**:
  - 与League一对一（外键league_id）
  - 与Team两个一对多关系（home_team_id, away_team_id）
  - 与Venue一对一（外键venue_id）
  - 与Intelligence一对多
  - 与Odds一对多
  - 与Prediction一对多

#### League（联赛表）
- **表名**: `leagues`
- **主要字段**:
  - 名称（name, code, short_name）
  - 国家地区（country, country_code, region）
  - 联赛级别（level）
  - 赛季信息（current_season, season_start, season_end）
  - 状态（is_active, is_popular）
  - 统计信息（total_views, total_followers）
- **关系**:
  - 与Match一对多
  - 与Team一对多

#### Team（球队表）
- **表名**: `teams`
- **主要字段**:
  - 名称（name, short_name, code, full_name）
  - 国家城市（country, country_code, city）
  - 历史信息（founded_year）
  - 场馆信息（stadium）
  - 人员信息（coach, owner）
  - 图片资源（logo_url, image_url等）
  - 联赛ID（league_id）
  - 状态（is_active, is_popular）
- **关系**:
  - 与League一对一（外键league_id）
  - 与Match两个一对多关系（home_matches, away_matches）
  - 与Player一对多
  - 与Intelligence一对多

#### Venue（场馆表）
- **表名**: `venues`
- **主要字段**:
  - 基本信息（name, capacity, city, country, address, coordinates）
  - 场地信息（surface_type, roof_type）
  - 建筑信息（year_built, architect）
  - 图片资源（image_urls, logo_url）
  - 设施信息（facilities）
  - 状态（is_active, is_neutral）
- **关系**:
  - 与Match一对多

### 2.2 情报与预测模型

#### Intelligence（情报表）
- **表名**: `intelligence`
- **主要字段**:
  - 比赛ID（match_id）
  - 球队ID（team_id）
  - 情报类型（type）
  - 情报来源（source）
  - 置信度（confidence_level）
  - 重要性（importance_level）
  - 内容（content）
  - 影响分析（impact_on_home, impact_on_away）
  - 权重（weight）
  - 审核状态（review_status）
  - 发布状态（is_published）
- **关系**:
  - 与Match一对一（外键match_id）
  - 与Team一对一（外键team_id）
  - 与User一对一（外键author_id）

#### Odds（赔率表）
- **表名**: `odds`
- **主要字段**:
  - 比赛ID（match_id）
  - 赔率公司ID（company_id）
  - 赔率值（odds_home_win, odds_draw, odds_away_win）
  - 概率（probability_home, probability_draw, probability_away）
  - 时间戳（timestamp）
  - 变化方向（movement_direction）
  - 指数（index_value）
  - 变化幅度（movement_amount）
  - 更新次数（update_count）
- **关系**:
  - 与Match一对一（外键match_id）
  - 与OddsCompany一对一（外键company_id）

#### Prediction（预测表）
- **表名**: `predictions`
- **主要字段**:
  - 比赛ID（match_id）
  - 预测类型（prediction_type）
  - 预测结果（predicted_outcome）
  - 预测概率（confidence_level）
  - 方法说明（method_description）
  - 实际结果（actual_outcome）
  - 准确性（accuracy）
  - 评分（rating）
- **关系**:
  - 与Match一对一（外键match_id）

### 2.3 用户与权限模型

#### AdminUser（管理员用户表）
- **表名**: `admin_users`
- **主要字段**:
  - 基本信息（username, email, real_name, phone）
  - 密码哈希（password_hash）
  - 角色（role）
  - 状态（status）
  - 安全设置（two_factor_enabled, login_allowed_ips）
  - 登录信息（last_login_at, login_count）
  - 创建者ID（created_by）
- **关系**:
  - 与AdminOperationLog一对多
  - 与AdminLoginLog一对多

#### AdminOperationLog（管理员操作日志表）
- **表名**: `admin_operation_logs`
- **主要字段**:
  - 管理员ID（admin_id）
  - 操作信息（action, resource_type, resource_id）
  - 请求信息（method, path, query_params, request_body）
  - 响应信息（status_code, response_data）
  - 环境信息（ip_address, user_agent）
  - 变更信息（changes_before, changes_after）
- **关系**:
  - 与AdminUser一对一（外键admin_id）

#### AdminLoginLog（管理员登录日志表）
- **表名**: `admin_login_logs`
- **主要字段**:
  - 管理员ID（admin_id）
  - 登录信息（login_at, login_ip, success）
  - 地理位置信息（country, city）
  - 设备信息（device_type, os, browser）
  - 安全信息（two_factor_used, ip_whitelisted）
- **关系**:
  - 与AdminUser一对一（外键admin_id）

### 2.4 爬虫相关模型

#### CrawlerConfig（爬虫配置表）
- **表名**: `crawler_configs`
- **主要字段**:
  - 名称和描述（name, description）
  - URL和频率（url, frequency）
  - 状态（is_active）
  - 配置数据（config_data，JSON格式）
  - 创建者ID（created_by）
- **关系**:
  - 与AdminUser一对一（外键created_by）

#### CrawlerTask（爬虫任务表）
- **表名**: `crawler_tasks`
- **主要字段**:
  - 任务名称和描述（name, description）
  - 配置ID（config_id）
  - 状态（status）
  - 调度信息（schedule_expression, next_run_at）
  - 最后运行信息（last_run_at, last_run_duration）
  - 执行统计（total_runs, successful_runs）
- **关系**:
  - 与CrawlerConfig一对一（外键config_id）

#### CrawlerTaskLog（爬虫任务日志表）
- **表名**: `crawler_task_logs`
- **主要字段**:
  - 任务ID（task_id）
  - 状态（status）
  - 执行时间信息（started_at, completed_at, duration_seconds）
  - 处理记录统计（records_processed, records_success, records_failed）
  - 响应时间（response_time_ms）
  - 错误信息（error_message）
- **关系**:
  - 与CrawlerTask一对一（外键task_id）

### 2.5 数据审核模型

#### DataReview（数据审核表）
- **表名**: `data_reviews`
- **主要字段**:
  - 数据类型（data_type）
  - 数据ID（data_id）
  - 数据表名（data_table）
  - 数据快照（data_snapshot，JSON格式）
  - 审核状态（review_status）
  - 审核人ID（reviewer_id）
  - 审核信息（review_notes, reviewed_at）
  - 验证分数（validation_score）
- **关系**:
  - 与User一对一（外键reviewer_id）

## 3. 数据库设计特点

### 3.1 索引策略
- 为频繁查询的字段建立了索引（如ID、时间戳、状态字段）
- 创建了复合索引以优化常见查询模式
- 为外键字段建立了索引以加速JOIN操作

### 3.2 关系设计
- 采用了一对多、多对一和多对多关系
- 使用了外键约束确保数据完整性
- 定义了适当的级联操作（如onDelete='SET NULL'或'CASCADE'）

### 3.3 审计功能
- 大多数模型继承了BaseAuditModel，自动记录创建和更新时间
- 管理员操作和登录都有专门的日志表进行记录

### 3.4 扩展性考虑
- 使用了枚举类型来表示固定选项（如比赛状态、情报类型等）
- 预留了JSON字段以支持灵活的数据存储
- 配置信息使用Text字段存储，支持复杂配置

## 4. 数据库配置

项目使用SQLAlchemy ORM，支持多种数据库（主要是PostgreSQL和SQLite）。模型定义遵循SQLAlchemy 2.0规范，使用了现代的typing注解和Mapped类型。

总体而言，这是一个结构完整、设计合理的数据库架构，支持了竞彩足球扫盘系统的各种功能需求。