# 开发环境脚本使用指南

## 脚本说明

本系统提供了多个脚本来简化开发和部署过程：

### 主要脚本

1. `start-dev.sh` - 完整开发环境启动脚本
2. `start-dev-simple.sh` - 简化版启动脚本
3. `start-with-monitoring.sh` - 带监控的启动脚本
4. `stop-dev.sh` - 停止所有服务
5. `status.sh` - 查看服务状态
6. `monitor-services.sh` - 服务监控脚本

## 快速开始

### 1. 环境准备

```bash
# 复制环境变量文件
cp .env.example .env

# 或者使用开发环境专用配置
cp .env.development .env
```

### 2. 启动开发环境

#### 方式一：完整启动（推荐）
```bash
./scripts/start-dev.sh
```

#### 方式二：简化启动
```bash
./scripts/start-dev-simple.sh
```

#### 方式三：带监控启动
```bash
./scripts/start-with-monitoring.sh
```

### 3. 查看服务状态

```bash
./scripts/status.sh
```

### 4. 停止服务

```bash
./scripts/stop-dev.sh
```

## 脚本功能详解

### start-dev.sh

完整启动脚本，功能包括：
- 环境检查
- 基础服务启动（PostgreSQL、Redis、RabbitMQ等）
- 数据库初始化
- 后端服务启动
- 前端服务启动
- 服务健康检查
- 日志记录

### start-dev-simple.sh

简化启动脚本，适用于本地开发环境：
- 基本环境检查
- 后端服务启动
- 前端服务启动
- 基本健康检查

### start-with-monitoring.sh

带监控的启动脚本：
- 包含完整启动功能
- 自动启动服务监控
- 实时资源监控
- 异常告警

### stop-dev.sh

服务停止脚本：
- 优雅停止所有服务
- 清理临时文件
- 清理PID文件

### status.sh

服务状态查看脚本：
- Docker容器状态
- 应用服务状态
- 端口占用情况
- 资源使用情况
- 最近日志信息

### monitor-services.sh

服务监控脚本：
- 定期检查服务状态
- 资源使用监控
- 日志文件管理
- 自动告警

## 日志管理

所有脚本都会在 `logs/` 目录下生成日志文件：

- `startup.log` - 启动日志
- `error.log` - 错误日志
- `monitor.log` - 监控日志
- `backend.log` - 后端服务日志
- `frontend.log` - 前端服务日志

## 环境变量

主要环境变量：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_USER=soccer_user
DB_PASSWORD=soccer_pass
DB_NAME=soccer_db

# API配置
API_V1_STR=/api/v1
SECRET_KEY=dev-secret-key
DEBUG=true

# 服务端口
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

## 常见问题

1. **端口冲突**
   - 检查端口占用：`lsof -i :<port>`
   - 修改配置文件中的端口设置

2. **权限问题**
   - 添加用户到docker组：`sudo usermod -aG docker $USER`
   - 重新登录或执行：`newgrp docker`

3. **服务启动失败**
   - 查看日志：`tail -f logs/error.log`
   - 检查配置：`cat .env`

## 开发建议

1. **开发流程**
   ```bash
   # 启动环境
   ./scripts/start-with-monitoring.sh
   
   # 查看状态
   ./scripts/status.sh
   
   # 开发完成后
   ./scripts/stop-dev.sh
   ```

2. **日志查看**
   ```bash
   # 实时查看后端日志
   tail -f logs/backend.log
   
   # 查看错误日志
   tail -f logs/error.log
   ```

3. **调试模式**
   - 后端：设置 `DEBUG=true` 和 `ENVIRONMENT=development`
   - 前端：使用 `npm run dev` 启动

## 监控告警

监控系统支持以下告警：
- 服务不可用
- 资源使用过高
- 错误日志过多
- 日志文件过大

## 最佳实践

1. **使用Git hooks**
   ```bash
   # 安装pre-commit hooks
   pip install pre-commit
   pre-commit install
   ```

2. **代码规范**
   ```bash
   # 后端代码检查
   cd backend
   black .
   isort .
   
   # 前端代码检查
   cd frontend
   npm run lint
   npm run format
   ```

3. **定期维护**
   - 定期清理日志文件
   - 更新依赖包
   - 备份重要数据