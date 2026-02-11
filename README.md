# 竞彩足球扫盘系统

## 项目概述

竞彩足球扫盘系统是一个专业的足球数据采集、分析和预测平台，为竞彩足球提供全面的数据支持与智能决策辅助。

## 技术架构

- **前端**: Vue 3 + Vite + TypeScript + Tailwind CSS
- **后端**: Python 3.11 + FastAPI + Uvicorn
- **数据库**: SQLite（开发环境）/ PostgreSQL 15+（生产环境）、Redis 7+（缓存/消息）
- **异步任务**: Celery + RabbitMQ/Redis
- **爬虫框架**: Scrapy + Playwright + BeautifulSoup4
- **部署**: Docker + Docker Compose + Nginx

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- pnpm

### 环境配置

1. 复制环境配置文件：

```bash
cp .env.example .env
# 编辑 .env 文件以适应你的环境
```

2. 验证环境配置：

```bash
python scripts/validate_env_config.py
```

3. 验证数据库路径一致性（避免多个数据库副本导致数据不一致）：

```bash
python check_database_paths.py
```

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

#### 方法一：使用统一启动脚本

```bash
# 启动开发模式（默认）
python scripts/start_backend.py --env development

# 启动测试模式
python scripts/start_backend.py --env testing

# 启动生产模式
python scripts/start_backend.py --env production

# 指定端口启动
python scripts/start_backend.py --env development --port 8001
```

#### 方法二：使用脚本启动

```bash
# 启动开发模式
./scripts/start-dev-simple.sh
```

#### 方法三：手动启动

1. 启动后端服务：

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

或者使用以下命令：

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

2. 启动前端服务：

```bash
cd frontend
pnpm run dev
```

### 访问地址

- **后端 API**: http://127.0.0.1:8000
- **API 文档**: http://127.0.0.0:8000/docs
- **前端界面**: http://127.0.0.1:3000
- **健康检查**: http://127.0.0.1:8000/health

## 开发规范

### 模拟与真实逻辑分离

为确保代码质量和环境一致性，我们采用以下规范：

1. 在关键服务中，添加日志明确标识当前执行的是模拟还是真实逻辑
2. 使用 `IS_MOCK` 环境变量控制是否启用模拟逻辑
3. 在日志中明确标注 "SIMULATED" 或 "REAL" 以区分执行模式

### API路由规范

- **管理端API**: `/api/v1/admin/*`
  - 用户管理: `/api/v1/admin/users`
  - 数据源管理: `/api/v1/admin/data-sources`
  - IP池管理: `/api/v1/admin/ip-pools`
  - 日志管理: `/api/v1/admin/system/logs`

## 项目结构

**数据库文件位置规范**：主数据库文件 `sport_lottery.db` 统一位于 `data/` 目录下（`data/sport_lottery.db`）。所有代码应通过配置系统访问数据库，禁止硬编码路径。项目根目录的旧数据库文件已删除，避免数据不一致。

```
sport-lottery-sweeper/
├── data/
│   └── sport_lottery.db  # 主数据库文件（统一位置）
├── backend/               # 后端源代码
│   ├── main.py           # 应用入口点
│   ├── api/              # API路由定义
│   ├── models/           # 数据模型
│   ├── schemas/          # Pydantic模型
│   ├── database_utils.py # 数据库连接工具
│   └── config.py         # 配置管理
├── frontend/             # 前端源代码
├── scripts/              # 脚本目录
│   ├── start_backend.py  # 统一启动脚本
│   └── validate_env_config.py # 环境配置验证
├── .env                  # 环境配置文件
├── .env.example          # 环境配置示例文件
├── requirements.txt      # Python依赖
├── package.json          # 前端依赖
├── docker/               # Docker配置
├── docs/                 # 文档
└── README.md
```

## 环境配置

项目支持三种环境模式：

- **development**: 开发环境，启用热重载和详细日志
- **testing**: 测试环境，使用测试数据库
- **production**: 生产环境，启用性能优化和安全设置

## 部署

### Docker部署

```bash
# 构建并启动所有服务
docker-compose -f docker/docker-compose.yml up -d --build
```

## 测试

```bash
# 运行单元测试
python -m pytest backend/tests/unit/

# 运行集成测试
python -m pytest backend/tests/integration/

# 运行前端测试
cd frontend && pnpm run test
```

## 贡献

请参考 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目贡献。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
