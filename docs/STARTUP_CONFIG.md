# 体育彩票扫盘系统 - 启动规范文档

> **项目启动统一配置** | 版本: 1.0.0 | 更新时间: 2026-02-06

## 🚀 整体架构

### 技术栈
- **前端**: Vue 3 + Vite + TypeScript + Tailwind CSS
- **后端**: Python 3.11 + FastAPI + Uvicorn
- **数据库**: SQLite (开发环境) / PostgreSQL (生产环境)
- **缓存**: Redis 7+ (可选)
- **部署**: Docker + Docker Compose

### 端口分配
- **前端开发服务器**: 3000
- **后端API服务**: 8000
- **数据库**: 默认使用SQLite文件或PostgreSQL 5432端口
- **代理转发**: 前端自动代理到后端8000端口

## 📋 主启动文件

### 后端入口
- **主文件**: `backend/main.py`
- **启动端口**: 8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health/live
- **启动命令**:
  ```bash
  python backend/main.py
  # 或使用脚本
  python backend_start.py
  ```

### 前端入口
- **开发服务器**: 端口3000
- **API代理**: 自动转发到后端8000端口
- **启动命令**:
  ```bash
  cd frontend && npm run dev
  # 或使用脚本
  start-frontend.bat
  ```

## 🔧 启动顺序和依赖

### 1. 环境准备
- 确保Python 3.11+ 和 Node.js 18+ 已安装
- 确保pip和npm可用
- 安装项目依赖

### 2. 数据库初始化
- **开发环境**: 项目使用SQLite数据库，文件位于项目根目录的[sport_lottery.db](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/sport_lottery.db)
- **容器环境**: 使用PostgreSQL数据库
- 首次启动前需要根据环境初始化数据库表结构

### 3. 启动顺序
1. **后端服务** (端口8000)
2. **前端服务** (端口3000，自动代理到后端)

## 🛠️ 启动命令详解

### 后端启动

#### 直接启动
```bash
cd backend
python main.py
```

#### 使用启动脚本
```bash
python backend_start.py
```

#### 使用npm脚本
```bash
npm run backend:dev
```

### 前端启动

#### 直接启动
```bash
cd frontend
npm run dev
```

#### 使用启动脚本 (Windows)
```bash
start-frontend.bat
```

#### 使用npm脚本
```bash
npm run frontend:dev
```

### 一键启动 (推荐)
```bash
npm run dev
```
或使用PowerShell脚本：
```bash
./start-dev.ps1
```

## 🌐 API路由规范

### 后端API路由
- **根路径**: http://localhost:8000
- **API前缀**: /api/v1
- **用户管理**: /api/v1/admin/users
- **前端用户管理**: /api/v1/admin/frontend-users
- **简单用户API**: /api/v1/admin/simple-users
- **健康检查**: /health/live 或 /api/v1/health/live
- **API文档**: /docs (Swagger UI) 和 /redoc (ReDoc)

### 前端代理配置
- **前端地址**: http://localhost:3000
- **API代理**: `/api` 请求自动转发到 `http://127.0.0.1:8000`
- **代理配置文件**: `frontend/vite.config.js`

## 🗄️ 数据库配置

### 本地开发环境
- **数据库类型**: SQLite
- **数据库文件**: `sport_lottery.db` (位于项目根目录)
- **连接方式**: 通过[database_utils.py](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/backend/database_utils.py)模块
- **连接池**: 自动管理

### 容器化环境
- **数据库类型**: PostgreSQL 15+
- **容器名称**: soccer-postgres
- **端口映射**: 5432:5432
- **连接方式**: 通过环境变量DATABASE_URL配置

### 数据库初始化脚本
- **管理员初始化**: `scripts/admin/init_admin_and_roles.py`
- **默认管理员账号**: 
  - 用户名：admin
  - 密码：admin123
  - 权限：同时拥有admin和super_admin角色

## ⚙️ 环境变量配置

### 主要环境变量
- `PORT`: 后端服务端口，默认8000
- `VITE_DEV_SERVER_PORT`: 前端开发服务器端口，默认3000
- `VITE_API_BASE_URL`: 前端API基础URL，默认`http://localhost:8000`
- `DATABASE_URL`: 数据库连接URL（开发环境使用SQLite文件，容器环境使用PostgreSQL）
- `SECRET_KEY`: JWT密钥
- `DEBUG`: 调试模式开关

### 配置文件位置
- **主配置**: `.env` (项目根目录)
- **前端配置**: `frontend/.env` (如有)
- **后端配置**: `backend/.env` (如有)

## 🐳 Docker部署配置

### Docker服务
- **Nginx反向代理**: 容器名 soccer-nginx，端口80/443
- **Backend服务**: 容器名 soccer-backend，端口8000
- **Frontend服务**: 容器名 soccer-frontend，端口3000
- **PostgreSQL数据库**: 容器名 soccer-postgres，端口5432
- **Redis缓存**: 容器名 soccer-redis，端口6379
- **MongoDB**: 容器名 soccer-mongo，端口27017
- **Celery Worker**: 容器名 soccer-celery-worker
- **Celery Beat**: 容器名 soccer-celery-beat
- **Flower监控**: 容器名 soccer-flower，端口5555
- **爬虫服务**: 容器名 soccer-crawler

### Docker启动命令
```bash
# 开发环境启动所有服务
docker-compose up -d --build

# 生产环境启动
docker-compose -f docker-compose.prod.yml up -d --build

# 只启动特定服务
docker-compose up -d postgres backend
```

### Docker网络
- 所有容器连接到 `soccer-network` 网络
- 容器间通过容器名互相访问（如 backend 访问 postgres）

## 🔄 启动方式对比

| 特性 | 本地启动 | 容器启动 |
|------|----------|----------|
| 数据库 | SQLite | PostgreSQL |
| 依赖管理 | 本地安装 | 容器内置 |
| 环境一致性 | 受本地环境影响 | 完全一致 |
| 性能 | 直接运行，性能更好 | 容器化开销 |
| 复杂服务 | 需额外配置 | 一键启动 |

### 统一配置建议
为避免冲突，建议：

1. **开发环境**：使用本地启动方式，便于调试
2. **测试/生产环境**：使用容器启动方式，保证一致性
3. **配置管理**：确保两种环境的业务逻辑配置保持一致

## 🔍 常见启动问题排查

### 端口占用问题
- 检查8000端口是否被占用: `netstat -an | grep 8000`
- 检查3000端口是否被占用: `netstat -an | grep 3000`
- 如端口被占用，使用脚本清理: `force_kill_port_8000.bat`

### 数据库连接问题
- **本地环境**: 确认[sport_lottery.db](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/sport_lottery.db)文件是否存在
- **容器环境**: 确认PostgreSQL服务是否正常运行
- 检查数据库权限是否正确
- 运行数据库检查脚本: `check_database.py`

### API代理问题
- 确认前端代理配置正确指向后端
- 检查网络连通性
- 查看浏览器控制台是否有CORS错误

## 🧪 服务验证

### 启动后验证命令
```bash
# 检查所有服务状态
python scripts/project_health_check.py

# 检查后端健康状态
curl http://localhost:8000/health/live

# 检查API文档是否可访问
curl http://localhost:8000/docs
```

### 访问地址
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **前端页面**: http://localhost:3000
- **健康检查**: http://localhost:8000/health/live