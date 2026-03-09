# 北单三维筛选器后端完整使用指南

## 🎯 项目概述

本项目是一个完整的北单三维筛选器后端系统，基于FastAPI框架开发，包含真实数据集成、数据库持久化、用户认证、性能优化等完整功能。

## 📋 已完成功能清单

### ✅ 核心功能
- [x] **数据模型扩展** - 完整的请求/响应模型定义
- [x] **实时数据接口** - GET /api/v1/beidan-filter/real-time-count
- [x] **选项数据接口** - 日期时间、联赛、强度等级、胜平差选项
- [x] **高级筛选接口** - POST /api/v1/beidan-filter/advanced-filter（核心）
- [x] **策略管理接口** - 增删改查和示例策略（带JWT认证）
- [x] **数据导出接口** - CSV/JSON/Excel格式导出
- [x] **错误处理和验证** - 统一的异常处理和数据验证

### ✅ 系统集成
- [x] **真实数据源** - 北单API服务类和数据转换
- [x] **数据库集成** - PostgreSQL + SQLAlchemy ORM
- [x] **用户认证** - JWT Token认证系统
- [x] **性能优化** - Redis缓存 + 数据库索引
- [x] **单元测试** - 完整的测试用例覆盖
- [x] **配置管理** - 环境变量配置系统

## 🏗️ 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │────│   FastAPI App    │────│  Database       │
│   Vue.js         │    │   (beidan_filter)│    │  PostgreSQL     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Cache Layer    │
                       │    Redis          │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ External APIs    │
                       │  北单数据源       │
                       └──────────────────┘
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd c:/Users/11581/Downloads/sport-lottery-sweeper/backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-beidan.txt
```

### 2. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑.env文件，修改以下关键配置：
# - DATABASE_URL: 数据库连接字符串
# - SECRET_KEY: JWT密钥（至少32字符）
# - REDIS_HOST: Redis服务器地址
# - BEIDAN_API_BASE_URL: 北单API地址
```

### 3. 数据库设置

```bash
# 创建数据库（PostgreSQL示例）
createdb sport_lottery

# 运行数据库迁移
cd backend
alembic upgrade head

# 或使用SQLAlchemy创建表
python -c "from backend.database import engine; from backend.models.beidan_strategy import Base; Base.metadata.create_all(bind=engine)"
```

### 4. 启动服务

```bash
# 开发模式启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式启动
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

# 或使用Docker
docker-compose up -d
```

### 5. 验证安装

```bash
# 检查API健康状态
curl http://localhost:8000/health

# 查看API文档
open http://localhost:8000/docs

# 测试基础接口
curl http://localhost:8000/api/v1/beidan-filter/strength-options
```

## 📚 API接口文档

### 基础信息
- **Base URL**: `http://localhost:8000/api/v1/beidan-filter`
- **认证方式**: Bearer Token (JWT)
- **响应格式**: JSON

### 主要接口列表

| 接口 | 方法 | 认证 | 描述 |
|------|------|------|------|
| `/real-time-count` | GET | ❌ | 获取实时场次数 |
| `/date-time-options` | GET | ❌ | 获取日期时间选项 |
| `/league-options` | GET | ❌ | 获取联赛选项 |
| `/strength-options` | GET | ❌ | 获取强度等级选项 |
| `/win-pan-diff-options` | GET | ❌ | 获取胜平差选项 |
| `/advanced-filter` | POST | ✅ | 高级筛选（核心） |
| `/strategies` | GET | ✅ | 获取策略列表 |
| `/strategies` | POST | ✅ | 保存策略 |
| `/strategies/{id}` | DELETE | ✅ | 删除策略 |
| `/strategies/examples` | GET | ❌ | 获取示例策略 |
| `/export/csv` | POST | ✅ | 导出CSV |
| `/export/json` | POST | ✅ | 导出JSON |
| `/export/excel` | POST | ✅ | 导出Excel |

### 认证示例

```bash
# 1. 登录获取Token（需要实现登录接口）
TOKEN=$(curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=test" | jq -r '.access_token')

# 2. 使用Token访问受保护接口
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/beidan-filter/strategies
```

## 🗄️ 数据库设计

### 主要数据表

#### beidan_strategies (策略表)
```sql
CREATE TABLE beidan_strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    three_dimensional JSON NOT NULL,
    other_conditions JSON NOT NULL,
    sort_config JSON NOT NULL,
    user_id VARCHAR(50) DEFAULT 'default_user',
    is_public BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    success_rate VARCHAR(10) DEFAULT '0%',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### beidan_strategy_execution_logs (执行日志表)
```sql
CREATE TABLE beidan_strategy_execution_logs (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES beidan_strategies(id) ON DELETE CASCADE,
    user_id VARCHAR(50) DEFAULT 'default_user',
    execution_params JSON,
    result_stats JSON,
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_ms INTEGER
);
```

## 🔧 配置说明

### 环境变量详解

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `DATABASE_URL` | string | - | 数据库连接URL |
| `REDIS_HOST` | string | localhost | Redis服务器地址 |
| `SECRET_KEY` | string | - | JWT签名密钥 |
| `BEIDAN_API_BASE_URL` | string | https://m.100qiu.com/api | 北单API地址 |
| `DEBUG` | bool | false | 调试模式开关 |
| `LOG_LEVEL` | string | INFO | 日志级别 |

### 缓存策略

- **比赛数据缓存**: 5分钟
- **策略数据缓存**: 10分钟  
- **统计信息缓存**: 30分钟
- **联赛选项缓存**: 1小时

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/unit/api/v1/test_beidan_filter_api.py -v

# 运行测试并生成覆盖率报告
pytest --cov=backend --cov-report=html

# 运行异步测试
pytest -xvs tests/ -k "async"
```

### 测试数据

测试使用Mock数据和内存数据库，无需外部依赖即可运行。

## 🚀 性能优化

### 已实现优化
- ✅ Redis缓存层减少数据库查询
- ✅ 数据库索引优化查询性能
- ✅ 异步处理提高并发能力
- ✅ 连接池管理数据库连接
- ✅ 请求限流防止过载

### 进一步优化建议
- 🔄 数据库读写分离
- 🔄 CDN加速静态资源
- 🔄 查询结果分页优化
- 🔄 数据预加载和预热

## 🔒 安全考虑

### 已实现安全措施
- ✅ JWT Token认证
- ✅ 请求参数验证
- ✅ SQL注入防护（SQLAlchemy ORM）
- ✅ XSS防护
- ✅ CORS跨域控制
- ✅ 请求频率限制

### 安全建议
- 🔐 定期轮换JWT密钥
- 🔐 使用HTTPS传输
- 🔐 敏感数据加密存储
- 🔐 定期安全审计

## 📈 监控和维护

### 健康检查
```bash
# API健康检查
curl http://localhost:8000/health

# 数据库连接检查
curl http://localhost:8000/health/db

# Redis连接检查
curl http://localhost:8000/health/redis
```

### 日志查看
```bash
# 应用日志
tail -f logs/app.log

# 错误日志
grep ERROR logs/app.log

# 访问日志
cat logs/access.log | jq .
```

## 🛠️ 故障排除

### 常见问题

1. **数据库连接失败**
   ```bash
   # 检查数据库服务状态
   sudo systemctl status postgresql
   # 检查连接字符串
   echo $DATABASE_URL
   ```

2. **Redis连接失败**
   ```bash
   # 检查Redis服务
   redis-cli ping
   # 检查防火墙设置
   telnet $REDIS_HOST $REDIS_PORT
   ```

3. **JWT认证失败**
   ```bash
   # 检查密钥长度
   echo $SECRET_KEY | wc -c
   # 检查Token格式
   echo $TOKEN | cut -d'.' -f1 | base64 -d
   ```

4. **API响应慢**
   ```bash
   # 检查缓存命中率
   redis-cli info stats | grep keyspace_hits
   # 检查数据库连接池
   # 查看慢查询日志
   ```

## 🤝 贡献指南

### 开发流程
1. Fork项目并创建特性分支
2. 编写代码和测试用例
3. 运行测试确保通过
4. 提交Pull Request

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用Black格式化代码
- 编写有意义的提交信息
- 为新功能添加测试用例

## 📞 技术支持

- **文档**: http://localhost:8000/docs
- **问题反馈**: 创建GitHub Issue
- **技术讨论**: 项目Discord/微信群

---

**版本**: v1.0.0  
**更新时间**: 2025-01-15  
**维护者**: Sport Lottery Sweeper Team