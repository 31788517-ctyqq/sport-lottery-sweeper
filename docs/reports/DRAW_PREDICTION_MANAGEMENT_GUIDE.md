# 平局预测管理模块使用指南

> 本文档提供平局预测管理模块的完整使用说明，包括功能概述、系统架构、安装配置、使用方法和常见问题。

---

## 📋 目录

- [功能概述](#功能概述)
- [系统架构](#系统架构)
- [安装与配置](#安装与配置)
- [功能使用说明](#功能使用说明)
  - [数据特征工程](#数据特征工程)
  - [模型训练与评估](#模型训练与评估)
  - [模型管理与部署](#模型管理与部署)
  - [预测监控](#预测监控)
- [API 接口文档](#api-接口文档)
- [后台任务队列](#后台任务队列)
- [告警机制](#告警机制)
- [常见问题](#常见问题)
- [后续优化方向](#后续优化方向)

---

## 功能概述

平局预测管理模块是一个完整的机器学习模型管理与监控系统，支持从数据特征提取、模型训练、模型部署到预测结果监控的全链路管理。

### 核心功能

| 功能模块 | 描述 | 状态 |
|---------|------|------|
| 数据特征工程 | 管理训练模型所需的特征数据，支持 CRUD 操作和搜索过滤 | ✅ 已完成 |
| 模型训练与评估 | 创建训练任务，支持多种算法，实时查看训练日志和状态 | ✅ 已完成 |
| 模型管理与部署 | 管理模型版本，支持上线、下线、回滚操作 | ✅ 已完成 |
| 预测监控 | 实时监控预测结果，展示命中率趋势，支持日期范围筛选 | ✅ 已完成 |
| 后台任务队列 | 使用 Celery 异步执行训练任务，避免阻塞主线程 | ✅ 已完成 |
| 自动更新结果 | 定时从数据源获取比赛结果，更新预测记录 | ✅ 已完成 |
| 异常告警 | 监控命中率，低于阈值时触发告警 | ✅ 已完成 |
| 可视化分析 | ECharts 展示命中率趋势图 | ✅ 已完成 |

---

## 系统架构

### 整体架构

```
┌─────────────────────────────────────────────────┐
│                 前端（Vue 3）            │
│  ┌───────────────────────────────────────┐  │
│  │  数据特征工程  模型训练与评估  │  │
│  │  模型管理      预测监控      │  │
│  └───────────────┬─────────────────────┘  │
│                │  HTTP/REST API             │
│                ↓                            │
└────────────────┬───────────────────────────────┘
                 │
         ┌───────┴────────┐
         │  FastAPI 后端  │
         └───────┬────────┘
                 │
    ┌──────────┼──────────┐
    │          │          │
    ↓          ↓          ↓
  Redis     PostgreSQL  Celery Worker
(Broker)   (Database)   (异步任务)
    │          │          │
    └──────────┴──────────┘
              │
              ↓
    ┌───────────────────┐
    │  对象存储 (S3)  │  (可选）
    └───────────────────┘
```

### 技术栈

- **前端**: Vue 3 + Element Plus + ECharts + Axios
- **后端**: FastAPI + SQLAlchemy + Celery + Redis
- **数据库**: PostgreSQL
- **任务队列**: Celery (Broker: Redis)
- **对象存储**: AWS S3 / 阿里云 OSS (可选）

---

## 安装与配置

### 前置条件

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### 1. 安装依赖

#### 后端依赖

```bash
cd backend
pip install -r requirements.txt
```

主要依赖包：
- `fastapi>=0.105.0` - Web 框架
- `celery>=5.3.6` - 任务队列
- `redis>=5.0.1` - Redis 客户端
- `sqlalchemy>=2.0.23` - ORM
- `psycopg2-binary>=2.9.9` - PostgreSQL 驱动

#### 前端依赖

```bash
cd frontend
npm install
```

主要依赖包：
- `vue@^3.0.0` - 前端框架
- `element-plus` - UI 组件库
- `echarts` - 图表库
- `axios` - HTTP 客户端

### 2. 数据库配置

确保 PostgreSQL 服务运行，并在 `backend/.env` 中配置：

```env
DATABASE_URL=postgresql://user:password@localhost:5432/sport_lottery
```

### 3. Redis 配置

启动 Redis 服务：

```bash
# Windows
redis-server

# Linux/Mac
redis-server --daemonize yes
```

在 `backend/.env` 中配置：

```env
REDIS_URL=redis://localhost:6379/0
```

### 4. 数据库迁移

创建数据库表：

```bash
cd backend
python create_missing_tables.py
# 或者使用 Alembic
alembic upgrade head
```

---

## 功能使用说明

### 数据特征工程

#### 访问路径

后台管理系统 → 平局预测管理 → 数据特征工程

#### 功能说明

1. **特征列表**: 以表格形式展示所有数据特征，包括：
   - ID
   - 特征名称
   - 描述
   - 来源类型
   - 创建时间

2. **搜索过滤**: 支持按特征名称关键字搜索，实时过滤结果

3. **新增特征**: 点击"新增特征"按钮，填写表单：
   - 特征名称（必填）
   - 描述（可选）
   - 来源类型（必填）

4. **编辑特征**: 点击某行的"编辑"按钮，修改特征信息

5. **删除特征**: 点击某行的"删除"按钮，确认后删除

#### API 接口

| 方法 | 路径 | 说明 |
|-----|------|------|
| GET | `/api/v1/admin/draw-prediction/features` | 获取特征列表 |
| POST | `/api/v1/admin/draw-prediction/features` | 创建新特征 |
| PUT | `/api/v1/admin/draw-prediction/features/{id}` | 更新特征 |
| DELETE | `/api/v1/admin/draw-prediction/features/{id}` | 删除特征 |

#### 数据模型

```python
class DrawFeature(Base):
    __tablename__ = "draw_features"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    source_type = Column(String(64), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

---

### 模型训练与评估

#### 访问路径

后台管理系统 → 平局预测管理 → 模型训练与评估

#### 功能说明

1. **训练任务列表**: 展示所有训练任务，包括：
   - 任务名称
   - 状态（PENDING/RUNNING/SUCCESS/FAILED）
   - 开始时间
   - 结束时间
   - 性能指标

2. **创建训练任务**: 点击"创建训练任务"按钮，填写表单：
   - 任务名称
   - 选择特征集（多选）
   - 选择算法（XGBoost / LightGBM / LogisticRegression）
   - 超参数（JSON 格式）

3. **查看日志**: 点击某任务的"日志"按钮，弹出日志窗口，实时显示训练过程：
   - 数据加载
   - 特征工程
   - 模型训练
   - 性能指标

4. **自动状态轮询**: 前端每 10 秒自动刷新任务列表，状态变化时 Tag 颜色随之改变

5. **异步执行**: 训练任务提交到 Celery 异步执行，不阻塞主线程

#### API 接口

| 方法 | 路径 | 说明 |
|-----|------|------|
| POST | `/api/v1/admin/draw-prediction/training-jobs` | 创建训练任务 |
| GET | `/api/v1/admin/draw-prediction/training-jobs` | 获取任务列表 |
| GET | `/api/v1/admin/draw-prediction/training-jobs/{id}/logs` | 获取训练日志 |
| PUT | `/api/v1/admin/draw-prediction/training-jobs/{id}/status` | 更新任务状态（测试用） |

#### 数据模型

```python
class DrawTrainingJob(Base):
    __tablename__ = "draw_training_jobs"
    
    id = Column(Integer, primary_key=True)
    job_name = Column(String(128), nullable=False)
    feature_set_ids = Column(JSON)  # 特征ID列表
    algorithm = Column(String(64), nullable=False)
    hyperparameters = Column(JSON)  # 超参数字典
    status = Column(Enum(TrainingJobStatus), default=PENDING)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    metrics = Column(JSON)  # 训练后评估指标
    celery_task_id = Column(String(255))  # Celery 任务ID
    created_by = Column(Integer, ForeignKey("admin_users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

### 模型管理与部署

#### 访问路径

后台管理系统 → 平局预测管理 → 模型管理与部署

#### 功能说明

1. **模型版本列表**: 展示所有模型版本，包括：
   - 版本标签（v1, v2...）
   - 训练任务ID
   - 性能指标
   - 状态（active/inactive）
   - 部署时间

2. **上线模型**: 点击某版本的"上线"按钮：
   - 该版本状态变为 active
   - 同任务的其他版本自动变为 inactive
   - 记录部署时间

3. **回滚模型**: 点击某版本的"回滚"按钮：
   - 该版本重新上线
   - 原上线版本自动下线
   - 更新部署时间

4. **查看详情**: 点击某行的"详情"按钮，弹出对话框显示：
   - 版本标签
   - 训练任务ID
   - 模型路径
   - 状态
   - 性能指标（JSON 格式）

5. **自动创建版本**: 训练任务成功后，系统自动创建对应的模型版本记录

#### API 接口

| 方法 | 路径 | 说明 |
|-----|------|------|
| GET | `/api/v1/admin/draw-prediction/models` | 获取模型版本列表 |
| POST | `/api/v1/admin/draw-prediction/models/{id}/deploy` | 上线模型 |
| POST | `/api/v1/admin/draw-prediction/models/{id}/rollback` | 回滚模型 |

#### 数据模型

```python
class DrawModelVersion(Base):
    __tablename__ = "draw_model_versions"
    
    id = Column(Integer, primary_key=True)
    version_tag = Column(String(64), nullable=False)
    training_job_id = Column(Integer, ForeignKey("draw_training_jobs.id"))
    model_path = Column(String(256), nullable=False)
    performance_metrics = Column(JSON)
    status = Column(String(32), default="inactive")
    deployed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

### 预测监控

#### 访问路径

后台管理系统 → 平局预测管理 → 预测监控

#### 功能说明

1. **统计卡片**: 顶部展示四个关键指标：
   - 总预测数
   - 命中数
   - 命中率（百分比）
   - 待确认

2. **命中率趋势图**: ECharts 折线图展示：
   - 按日期分组统计命中率
   - 平滑曲线展示趋势
   - 支持窗口大小自适应

3. **预测结果列表**: 表格展示所有预测记录，包括：
   - 比赛 ID
   - 平局概率（百分比）
   - 实际结果（平局/主胜/客胜/未开赛）
   - 是否命中（命中/未中/等待）
   - 比赛时间
   - 预测时间

4. **日期范围筛选**: 选择开始和结束日期，过滤预测结果

5. **实时计算**: 命中率根据已结束的比赛实时计算

#### API 接口

| 方法 | 路径 | 说明 |
|-----|------|------|
| GET | `/api/v1/admin/draw-prediction/predictions` | 获取预测结果列表 |

#### 数据模型

```python
class DrawPredictionResult(Base):
    __tablename__ = "draw_prediction_results"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(String(128), nullable=False)
    predicted_draw_prob = Column(Float, nullable=False)
    actual_result = Column(String(16))  # draw/home/away
    prediction_meta = Column(JSON)
    predicted_at = Column(DateTime, default=datetime.utcnow)
    match_time = Column(DateTime, nullable=False)
```

---

## API 接口文档

完整的 API 文档请访问 Swagger UI：

```
http://localhost:8000/docs
```

### 认证

所有 API 需要认证，在请求头中携带 Token：

```
Authorization: Bearer <your_token>
```

### 通用响应格式

#### 成功响应

```json
{
  "id": 1,
  "name": "历史交锋特征",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 错误响应

```json
{
  "detail": "Feature not found"
}
```

---

## 后台任务队列

### Celery Worker

#### 启动 Worker

```bash
cd backend
celery -A backend.celery_app worker --loglevel=info
```

#### 启动 Flower 监控

```bash
celery -A backend.celery_app flower --port=5555
```

访问 Flower 界面：`http://localhost:5555`

#### 定时任务配置

定时任务在 `backend/tasks/draw_prediction_tasks.py` 中配置：

| 任务名 | 执行时间 | 说明 |
|-------|---------|------|
| update_prediction_results_daily | 每天凌晨 2:00 | 更新比赛结果 |
| monitor_accuracy_daily | 每天上午 9:00 | 监控命中率并告警 |

---

## 告警机制

### 告警规则

- **监控窗口**: 最近 7 天
- **告警阈值**: 命中率 < 70%
- **告警级别**: 警告

### 告警触发流程

```
1. 定时任务每天上午 9:00 执行
2. 计算最近 7 天的命中率
3. 判断是否低于 70% 阈值
4. 如果低于阈值，触发告警
5. 记录告警日志（可扩展为邮件/企业微信）
```

### 告警信息示例

```json
{
  "should_alert": true,
  "accuracy": 0.65,
  "threshold": 0.70,
  "message": "最近7天的命中率 (65.0%) 低于阈值 (70.0%)，请注意模型性能！"
}
```

---

## 常见问题

### 1. 如何添加新的数据特征？

**答**: 在"数据特征工程"页面点击"新增特征"按钮，填写表单后提交。特征将自动保存到数据库。

### 2. 训练任务一直在 PENDING 状态？

**答**: 检查 Celery Worker 是否启动：
```bash
# 检查进程
ps aux | grep celery

# 查看 Flower 监控
http://localhost:5555
```

### 3. 如何手动更改训练任务状态（测试用）？

**答**: 使用 PUT 接口：
```bash
curl -X PUT "http://localhost:8000/api/v1/admin/draw-prediction/training-jobs/1/status" \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"status": "success"}'
```

### 4. 如何回滚到之前的模型版本？

**答**: 在"模型管理与部署"页面，找到目标版本，点击"回滚"按钮。该版本将重新上线，其他版本自动下线。

### 5. 预测结果的 actual_result 如何自动更新？

**答**: 系统每天凌晨 2:00 执行定时任务，从数据源获取比赛结果并更新。当前实现为模拟，实际项目中对接爬虫或第三方 API。

### 6. 如何修改告警阈值？

**答**: 编辑 `backend/services/alert_service.py` 文件：
```python
ALERT_THRESHOLD = 0.70  # 修改此值
ALERT_WINDOW_DAYS = 7   # 修改监控窗口
```

### 7. 如何集成对象存储？

**答**: 在训练任务完成后，上传模型文件到 S3 或阿里云 OSS，并将 URL 保存到 `DrawModelVersion.model_path` 字段。

---

## 后续优化方向

### 1. 模型文件上传到对象存储

**目标**: 将训练好的模型上传到云存储（AWS S3 / 阿里云 OSS）

**实现要点**:
- 集成 `boto3` 或 `oss2` SDK
- 生成可下载的 URL（签名 URL）
- 记录文件大小和上传时间

### 2. 告警通知

**目标**: 当命中率低于阈值时，通过多种渠道发送告警

**实现要点**:
- 邮件服务（SMTP）
- 企业微信机器人（Webhook）
- 短信服务（阿里云短信）
- 告警级别划分（警告/严重/紧急）

### 3. 训练任务优化

**目标**: 提升训练效率和模型质量

**实现要点**:
- 超参数自动调优
- 支持 GPU 加速训练
- 训练过程可视化（TensorBoard）
- 分布式训练支持

### 4. 预测结果增强

**目标**: 提供更丰富的预测分析

**实现要点**:
- 批量导入历史比赛数据
- 对比多个模型的预测结果
- 预测置信度展示
- 支持导出 Excel 报表

### 5. 数据可视化增强

**目标**: 提供更多维度的数据分析

**实现要点**:
- 命中率热力图
- 特征重要性分析图
- 模型性能对比图
- 异常预测检测

---

## 更新日志

| 版本 | 日期 | 更新内容 |
|-----|------|---------|
| v1.0 | 2024-01-21 | 初始版本，实现完整功能链路 |
| v1.1 | 2024-01-21 | 增加 Celery 异步任务队列 |
| v1.2 | 2024-01-21 | 添加 ECharts 可视化和告警机制 |

---

## 联系与反馈

如有问题或建议，请联系：

- GitHub Issues: [项目地址]/issues
- 技术支持: [邮箱地址]

---

**文档版本**: v1.0  
**最后更新**: 2024-01-21  
**维护者**: 平局预测管理模块团队
