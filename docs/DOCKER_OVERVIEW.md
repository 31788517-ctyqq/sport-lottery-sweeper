# 体育彩票系统 Docker 配置总览

## 概述

本项目提供了完整的 Docker 容器化部署方案，包括开发、测试、预发布和生产环境的多种配置。项目采用了微服务架构，通过 Docker Compose 进行多容器编排。

## Docker 配置文件结构

### 主要 Docker 配置文件

1. **Dockerfile** - 基础后端服务构建配置
2. **Dockerfile.backend** - 后端服务生产环境构建配置
3. **Dockerfile.frontend** - 前端服务构建配置
4. **Dockerfile.production** - 生产环境构建配置

### Docker Compose 配置文件

1. **docker/docker-compose.yml** - 基础 Docker Compose 配置
2. **docker-compose.dev.yml** - 开发环境配置
3. **docker-compose.staging.yml** - 预发布环境配置
4. **docker-compose.prod.yml** - 生产环境配置
5. **docker-compose.production.yml** - 生产环境简化配置
6. **docker-compose.override.yml** - Docker Compose 覆盖配置

## 环境配置详解

### 1. 开发环境 (docker-compose.dev.yml)

- **服务组成**：
  - backend: FastAPI 后端服务
  - frontend: Vue.js 前端服务
  - crawler: 爬虫服务

- **特点**：
  - 使用 Dockerfile.dev 构建
  - 挂载本地代码卷便于实时开发
  - 重启策略：除非停止
  - 适合开发调试

### 2. 预发布环境 (docker-compose.staging.yml)

- **服务组成**：
  - backend: 后端 API 服务
  - frontend: 前端服务
  - postgres: PostgreSQL 数据库
  - redis: 缓存服务
  - celery-worker: 异步任务处理器
  - celery-beat: 定时任务调度器
  - nginx: 反向代理

- **特点**：
  - 环境隔离，模拟生产环境
  - 包含完整的后端服务栈
  - 端口映射避免冲突（如 8001:8000）

### 3. 生产环境 (docker-compose.prod.yml)

- **服务组成**：
  - backend: 后端 API 服务（3副本）
  - frontend: 前端服务（2副本）
  - postgres: PostgreSQL 数据库
  - redis: 缓存服务
  - celery-worker: Celery 工作进程（2副本）
  - celery-beat: 定时任务调度
  - prometheus: 监控服务
  - grafana: 监控仪表板
  - nginx: 反向代理（2副本）

- **特点**：
  - 高可用配置（多副本部署）
  - 健康检查机制
  - 资源限制和预留
  - 完整监控体系
  - 安全认证配置

## Dockerfile 详解

### 根目录 Dockerfile
- 基于 python:3.11-slim 镜像
- 使用国内 PyPI 镜像源加速安装
- 复制整个项目代码
- 暴露 8000 端口
- 启动命令为 `python main.py`

### Dockerfile.backend
- 专为后端服务优化
- 包含生产环境依赖
- 配置 Gunicorn 服务器
- 设置适当的并发和资源限制

### Dockerfile.frontend
- Node.js 环境构建前端应用
- 使用 Nginx 作为静态文件服务器
- 优化构建过程和体积

## 特殊配置

### .dockerignore
- 忽略不必要的文件和目录
- 减少镜像大小和构建时间
- 提高安全性

### 监控配置
- Prometheus 用于指标收集
- Grafana 用于可视化展示
- 完整的性能监控体系

## 部署指南

### 开发环境启动
```bash
cd docker
docker-compose up -d
```

### 生产环境部署
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### 使用 Makefile
项目还包含 Makefile，提供了便捷的 Docker 操作命令：

```makefile
# 示例命令
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
```

## 安全考虑

- 敏感信息通过环境变量或 .env 文件管理
- Redis 密码保护
- 数据库访问控制
- SSL/TLS 配置

## 扩展性设计

- 支持多环境配置
- 可水平扩展的服务设计
- 容器健康检查机制
- 日志集中管理

## 总结

该项目的 Docker 配置非常完善，涵盖了从开发到生产的完整生命周期，具有良好的可维护性和扩展性。