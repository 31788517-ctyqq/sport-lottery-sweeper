# 体育彩票爬虫管理系统 - 管理员API文档

## 📋 概述

本文档描述体育彩票爬虫管理系统的所有管理员API端点、参数和响应格式。API基于FastAPI构建，采用JWT认证，支持完整的CRUD操作和实时监控。

---

## 🔌 API基础信息

**基础URL**: `http://localhost:8000/api/v1/admin`

**认证方式**: JWT Bearer Token

**响应格式**: JSON

**默认编码**: UTF-8

**API版本**: v1

---

## 🔐 认证

所有管理员API端点都需要JWT认证。

### 获取Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 使用Token

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  http://localhost:8000/api/v1/admin/users
```

---

## 🗂️ API端点概览

| 模块 | 端点前缀 | 主要功能 |
|------|----------|----------|
| 认证 | `/auth` | 用户登录、权限验证 |
| 管理员用户 | `/users` | 用户管理 |
| 爬虫数据源 | `/crawler/sources` | 数据源CRUD、健康检查 |
| 爬虫任务 | `/crawler/tasks` | 任务调度、执行日志 |
| 数据情报 | `/crawler/intelligence` | 统计分析、趋势分析 |
| 系统配置 | `/crawler/configs` | 全局配置管理 |
| 代理管理 | `/proxy` | 代理池管理 |
| 赛事数据 | `/matches` | 比赛数据查询 |

---

## 👥 认证管理

### 用户登录

**端点**: `POST /auth/login`

**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### 获取当前用户信息

**端点**: `GET /auth/me`

**响应**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "real_name": "管理员",
  "role": "SUPER_ADMIN",
  "status": "ACTIVE",
  "last_login_at": "2026-01-21T10:00:00",
  "permissions": ["read", "write", "delete"]
}
```

---

## 🕷️ 爬虫数据源管理

### 获取数据源列表

**端点**: `GET /crawler/sources`

**查询参数**:
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| status | string | 否 | - | 状态筛选 (online/offline) |
| search | string | 否 | - | 搜索关键词 |
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 20 | 每页数量 |

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "name": "500彩票网",
      "url": "https://www.500.com",
      "description": "500彩票网数据源",
      "source_type": "http",
      "status": "online",
      "priority": 1,
      "timeout": 30,
      "retry_times": 3,
      "success_rate": 95.5,
      "response_time": 245.6,
      "last_check_time": "2026-01-21T09:30:00",
      "created_at": "2026-01-01T00:00:00",
      "updated_at": "2026-01-21T09:30:00"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

### 创建数据源

**端点**: `POST /crawler/sources`

**请求体**:
```json
{
  "name": "string",
  "url": "string",
  "description": "string",
  "source_type": "http",
  "status": "online",
  "priority": 1,
  "timeout": 30,
  "retry_times": 3,
  "config": {
    "headers": {"User-Agent": "..."},
    "proxy": false
  }
}
```

### 健康检查

**端点**: `POST /crawler/sources/{source_id}/check`

**响应**:
```json
{
  "status": "healthy",
  "response_time_ms": 245.6,
  "status_code": 200,
  "timestamp": "2026-01-21T10:00:00",
  "metrics": {
    "total_requests_24h": 144,
    "successful_requests": 138,
    "failed_requests": 6,
    "success_rate_percent": 95.83,
    "avg_response_time_ms": 245.6
  },
  "last_run_at": "2026-01-21T09:00:00",
  "message": "基于24小时内144次运行数据统计"
}
```

---

## 📊 数据情报与统计分析

### 获取统计概览

**端点**: `GET /crawler/intelligence/stats`

**响应**:
```json
{
  "total_crawled": 15420,
  "today_crawled": 156,
  "today_success": 148,
  "today_failed": 8,
  "overall_success_rate": 96.2,
  "active_sources": 5,
  "error_distribution": [
    {
      "name": "网络错误",
      "value": 45,
      "color": "#ff4757"
    },
    {
      "name": "解析错误",
      "value": 23,
      "color": "#ff6348"
    },
    {
      "name": "超时错误",
      "value": 12,
      "color": "#fd79a8"
    }
  ]
}
```

### 获取趋势分析

**端点**: `GET /crawler/intelligence/trends`

**查询参数**:
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| days | integer | 否 | 7 | 天数范围 |

**响应**:
```json
{
  "dates": ["2026-01-15", "2026-01-16", "2026-01-17", ...],
  "success_rates": [95.5, 96.2, 94.8, ...],
  "data_volumes": [120, 135, 142, ...],
  "response_times": [250, 245, 260, ...]
}
```

### 导出数据

**端点**: `GET /crawler/intelligence/export`

**查询参数**:
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| format | string | 否 | csv | 导出格式 (csv/json) |

**响应**: CSV文件流

---

## ⚙️ 系统配置管理

### 获取配置列表

**端点**: `GET /crawler/configs`

**查询参数**:
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| config_type | string | 否 | - | 配置类型筛选 |

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "config_key": "crawler_timeout",
      "config_value": 30,
      "description": "爬虫请求超时时间（秒）",
      "config_type": "timeout",
      "created_at": "2026-01-01T00:00:00",
      "updated_at": "2026-01-21T10:00:00"
    }
  ]
}
```

### 更新配置

**端点**: `PUT /crawler/configs/{config_id}`

**请求体**:
```json
{
  "config_value": 60,
  "description": "更新超时时间为60秒"
}
```

---

## 🗄️ 数据库表结构

### 核心表结构

#### 1. admin_users (管理员用户表)
```sql
CREATE TABLE admin_users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL, -- SUPER_ADMIN, ADMIN, MODERATOR, AUDITOR, OPERATOR
    status VARCHAR(20) NOT NULL, -- ACTIVE, INACTIVE, SUSPENDED, LOCKED
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

#### 2. crawler_configs (爬虫数据源表)
```sql
CREATE TABLE crawler_configs (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    url VARCHAR(500) NOT NULL,
    frequency INTEGER NOT NULL DEFAULT 3600,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    config_data TEXT,
    created_by INTEGER,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

#### 3. crawler_tasks (爬虫任务表)
```sql
CREATE TABLE crawler_tasks (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    source_id INTEGER NOT NULL,
    task_type VARCHAR(50) NOT NULL DEFAULT 'crawl',
    cron_expression VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(20) NOT NULL DEFAULT 'stopped',
    last_run_time DATETIME,
    next_run_time DATETIME,
    run_count INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    config TEXT,
    created_by INTEGER,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

#### 4. crawler_task_logs (任务执行日志表)
```sql
CREATE TABLE crawler_task_logs (
    id INTEGER PRIMARY KEY,
    task_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL, -- running, success, failed, timeout
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    duration_seconds FLOAT,
    records_processed INTEGER,
    records_success INTEGER,
    records_failed INTEGER,
    error_message TEXT,
    error_details TEXT, -- JSON
    response_time_ms FLOAT,
    created_by INTEGER,
    created_at DATETIME NOT NULL
);
```

#### 5. crawler_source_stats (数据源统计表)
```sql
CREATE TABLE crawler_source_stats (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL,
    date DATE NOT NULL,
    total_requests INTEGER NOT NULL DEFAULT 0,
    successful_requests INTEGER NOT NULL DEFAULT 0,
    failed_requests INTEGER NOT NULL DEFAULT 0,
    avg_response_time_ms FLOAT,
    total_records INTEGER NOT NULL DEFAULT 0,
    last_success_at DATETIME,
    last_failure_at DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    UNIQUE(source_id, date)
);
```

---

## 📈 实时监控指标

### 数据源健康指标
- **成功率**: 基于最近24小时真实运行数据计算
- **响应时间**: 平均响应时间（毫秒）
- **最后检查时间**: 最近一次健康检查时间
- **错误分布**: 基于真实错误日志智能分类

### 任务执行指标
- **运行次数**: 任务累计执行次数
- **成功/失败计数**: 真实的执行结果统计
- **持续时间**: 每次执行的耗时统计
- **处理记录数**: 每次抓取的数据量统计

### 系统性能指标
- **并发任务数**: 当前运行的任务数量
- **队列长度**: 等待执行的任务数量
- **内存使用**: 系统资源占用情况
- **数据库连接**: 连接池状态

---

## 🚨 错误处理

### HTTP状态码
| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 权限不足 |
| 404 | 资源未找到 |
| 409 | 资源冲突 |
| 422 | 数据验证错误 |
| 500 | 服务器内部错误 |

### 错误响应格式
```json
{
  "detail": "错误描述信息",
  "code": "ERROR_CODE",
  "timestamp": "2026-01-21T10:00:00"
}
```

---

## 🔄 实时特性

### WebSocket事件
- `task_started`: 任务开始执行
- `task_completed`: 任务执行完成
- `task_failed`: 任务执行失败
- `source_status_changed`: 数据源状态变更
- `system_alert`: 系统告警

### Server-Sent Events (SSE)
支持实时数据流推送，用于仪表板实时更新。

---

## 📝 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0.0 | 2026-01-21 | 初始版本：完整的管理员API、真实数据库操作 |

---

**最后更新**: 2026-01-21
**维护团队**: 技术开发部