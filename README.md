# 竞彩足球扫盘系统

## 项目概述

竞彩足球扫盘系统是一个专业的足球数据采集、分析和预测平台，为竞彩足球提供全面的数据支持与智能决策辅助。

## 技术架构

- **前端**: Vue 3 + Vite + TypeScript + Tailwind CSS
- **后端**: Python 3.11 + FastAPI + Uvicorn
- **数据库**: PostgreSQL 15+（主库）、Redis 7+（缓存/消息）
- **异步任务**: Celery + RabbitMQ/Redis
- **爬虫框架**: Scrapy + Playwright + BeautifulSoup4
- **部署**: Docker + Docker Compose + Nginx

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- pnpm

### 安装步骤

1. 克隆项目：

```bash
git clone <repository-url>
cd sport-lottery-sweeper
```

2. 创建并激活虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

3. 安装Python依赖：

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. 安装前端依赖：

```bash
cd frontend
pnpm install
cd ..
```

### 启动服务

#### 方法一：使用脚本启动

```bash
# 启动开发模式
./scripts/start-dev-simple.sh
```

#### 方法二：手动启动

1. 启动后端服务：

```bash
cd src/backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

或者使用以下命令：

```bash
uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```

2. 启动前端服务：

```bash
cd frontend
pnpm run dev
```

### 访问地址

- **后端 API**: http://127.0.0.1:8000
- **API 文档**: http://127.0.0.1:8000/docs
- **前端界面**: http://127.0.0.1:3000
- **健康检查**: http://127.0.0.1:8000/health

## 项目结构

```
sport-lottery-sweeper/
├── src/
│   └── backend/           # 后端源代码
│       ├── main.py        # 应用入口点
│       ├── config.py      # 配置文件
│       ├── database.py    # 数据库配置
│       ├── api/           # API路由
│       ├── core/          # 核心功能
│       ├── models/        # 数据模型
│       ├── schemas/       # 数据模式
│       ├── services/      # 业务服务
│       └── tasks/         # 异步任务
├── frontend/              # 前端代码
├── scripts/               # 启动和部署脚本
├── docker/                # Docker配置
├── docs/                  # 文档
├── config/                # 配置文件
├── tests/                 # 测试代码
├── requirements.txt       # Python依赖
├── pyproject.toml         # 项目配置
└── README.md
```

## 性能优化特性

- **延迟导入**: 按需加载模块，减少启动时间
- **异步初始化**: 高效的异步初始化服务
- **缓存机制**: 高效的缓存管理器
- **时间监测**: 详细的启动时间监测功能

## 部署

### Docker部署

本项目支持通过 Docker 快速构建与运行，确保不同环境下行为一致。

#### 1. 基础启动
```bash
cd docker
docker-compose up -d
```

#### 2. 使用自动初始化入口脚本
为确保容器启动时自动完成数据库结构迁移、种子数据导入与健康检查，项目提供了 `scripts/docker/entrypoint.sh` 作为容器入口。
该脚本会按顺序执行：
1. `alembic upgrade head` （数据库结构迁移）
2. `python scripts/seed/seed_runner.py` （防重复导入示例数据）
3. `python scripts/health_check/db_health_check.py` （健康检查）
4. `uvicorn backend.main:app --host 0.0.0.0 --port 8000` （启动服务）

如果任一步失败，容器将终止启动，确保环境健康后才提供 API。

#### 3. Dockerfile 示例（后端）
```Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（如 gcc/sqlite 开发库）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# 确保入口脚本可执行
RUN chmod +x scripts/docker/entrypoint.sh

# 设置入口
ENTRYPOINT ["/app/scripts/docker/entrypoint.sh"]
```

#### 4. docker-compose.yml 示例（后端服务片段）
```yaml
version: "3.9"
services:
  backend:
    build: .
    container_name: sport_lottery_backend
    ports:
      - "8000:8000"
    volumes:
      - ./sport_lottery.db:/app/sport_lottery.db  # 可选：持久化数据库文件
    environment:
      - ENV=development
```

#### 5. 启动命令
在包含 `docker-compose.yml` 的目录下执行：
```bash
docker-compose up -d --build
```
后端 API 可通过 http://127.0.0.1:8000 访问，API 文档在 http://127.0.0.1:8000/docs。

> **注意**：如果数据库文件需要持久化，请挂载卷或修改 `entrypoint.sh` 逻辑以支持外部数据库（如 PostgreSQL）。生产环境建议切换至 PostgreSQL 并调整 `alembic.ini` 的连接串。

## 数据库管理与恢复

本项目采用 **Alembic** 进行数据库结构版本管理，并使用独立的 seed 脚本管理示例数据，确保数据结构与数据分离，便于开发与生产环境维护。

### 目录结构
```
data/seed/sport_lottery_sample_data.sql   # 示例数据
scripts/seed/seed_runner.py               # 防重复数据导入脚本
scripts/health_check/db_health_check.py   # 数据库健康检查脚本
scripts/recovery/reset_and_recover.py     # 一键恢复脚本
```

### 启动流程
项目提供了 `start_backend.bat`（Windows）用于一键完成以下步骤：
1. **数据库结构迁移** → `alembic upgrade head`
2. **种子数据导入** → `python scripts/seed/seed_runner.py`（仅在表为空时导入）
3. **数据库健康检查** → `python scripts/health_check/db_health_check.py`
4. **启动后端服务** → `uvicorn backend.main:app`

运行：
```bat
start_backend.bat
```

### 手动执行迁移与数据初始化
```bash
# 进入项目根目录
cd path/to/sport-lottery-sweeper

# 1. 执行数据库结构迁移
alembic upgrade head

# 2. 导入种子数据（防重复）
python scripts/seed/seed_runner.py

# 3. 健康检查
python scripts/health_check/db_health_check.py
```

### 数据库健康检查
检查内容包括：
- Alembic 当前版本是否为 `fd2e6eb3e2ee (head)`
- 数据库表 `leagues`、`teams`、`matches` 是否存在
- 示例数据是否已导入并统计记录数

运行：
```bash
python scripts/health_check/db_health_check.py
```
返回码 `0` 表示健康，`1` 表示存在问题。

### 一键恢复脚本
当数据库损坏或结构异常时，可使用恢复脚本快速重置：
```bash
python scripts/recovery/reset_and_recover.py
```
脚本会：
1. 删除现有数据库文件
2. 重新创建 Alembic 空迁移并标记版本
3. 导入种子数据
4. 执行健康检查

⚠️ 执行前会要求手动确认，以防误删数据。

### 注意事项
- **结构变更**必须通过 Alembic 迁移脚本完成，禁止手动修改数据库结构。
- **示例数据**仅用于开发/测试，生产环境请使用真实数据初始化流程。
- 未来可考虑将 SQLite 替换为 PostgreSQL 以获得更好的并发与扩展性。

## CI/CD 检查

项目集成了 GitHub Actions 自动化检查，确保每次代码变更不会破坏数据库结构、数据初始化或测试环境。

### 检查流程
在每次 `push` 到 `main`/`develop` 分支或发起 Pull Request 时，将自动执行：

1. **环境准备**
   - 安装 Python 依赖（含 `pytest`, `pytest-asyncio`, `alembic` 等）
   - 自动补全 `pyproject.toml` 中的 `asyncio_mode = "auto"` 配置（解决异步测试问题）

2. **数据库迁移检查**
   - 使用临时 SQLite 数据库执行 `alembic upgrade head`，确保迁移脚本可正常运行

3. **种子数据导入 & 健康检查**
   - 运行 `scripts/seed/seed_runner.py` 导入示例数据（防重复）
   - 执行 `scripts/health_check/db_health_check.py` 验证表结构与数据完整性

4. **测试运行**
   - 执行 `pytest` 运行所有单元/集成/E2E 测试（含异步测试）
   - 生成覆盖率报告并上传至 Codecov（可选）

5. **可选：一键恢复验证**
   - 在临时环境中执行 `scripts/recovery/reset_and_recover.py`，确保恢复流程可用

### Workflow 文件位置
```
scripts/ci/db_ci_check.yml
```

### 触发条件
- `push` 到 `main` 或 `develop` 分支
- `pull_request` 面向 `main` 分支

### 本地运行 CI 检查
可在本地模拟 CI 流程以确保通过率：
```bash
# 安装依赖
pip install -r requirements.txt
pip install pytest pytest-asyncio coverage alembic

# 补全 pytest 配置（仅需一次）
echo '[tool.pytest.ini_options]' >> pyproject.toml
echo 'asyncio_mode = "auto"' >> pyproject.toml

# 依次执行
alembic upgrade head
python scripts/seed/seed_runner.py
python scripts/health_check/db_health_check.py
pytest tests/ --cov=backend --cov-report=term-missing
```

> **注意**：CI 环境使用独立的临时数据库文件，不会影响本地开发数据。
> 异步测试之前存在的配置问题已在 CI 中自动修复，建议同步到本地 `pyproject.toml` 以避免差异。

## 贡献

欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证

MIT

## 📋 开发规范与文件生成指南

为保证项目结构统一与代码可维护性，请所有开发者与 AI 助手遵循 [文件生成指令示例清单](./FILE_GENERATION_GUIDE.md) 进行新文件的创建。
该清单基于项目的 `<always_applied_workspace_rules>` 制定，涵盖 Vue 组件、页面、API、工具函数、测试等所有模块的路径与命名规范。

> ✅ 使用清单可确保文件始终生成到正确目录，避免结构混乱与后期重构成本。