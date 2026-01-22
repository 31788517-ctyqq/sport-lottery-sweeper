# 竞彩足球扫盘系统 - 快速开始指南

## 环境要求

- Docker >= 20.10.0
- Docker Compose >= 2.0.0
- Python >= 3.8
- Node.js >= 16.0.0
- npm >= 8.0.0

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd soccer-scanning-system
```

### 2. 一键启动
```bash
# 使用主控制脚本
./dev.sh start

# 或者直接使用启动脚本
./scripts/start-with-monitoring.sh
```

### 3. 查看服务状态
```bash
./dev.sh status

# 或者
./scripts/status.sh
```

### 4. 查看日志
```bash
# 查看所有服务日志
./dev.sh logs

# 查看特定服务日志
./dev.sh logs backend
./dev.sh logs frontend
```

### 5. 停止服务
```bash
./dev.sh stop
```

## 开发环境说明

### 服务端口

| 服务 | 端口 | 访问地址 |
|------|------|----------|
| 前端应用 | 3000 | http://localhost:3000 |
| 后端API | 8000 | http://localhost:8000 |
| API文档 | 8000 | http://localhost:8000/docs |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| RabbitMQ | 5672 | localhost:5672 |
| MongoDB | 27017 | localhost:27017 |
| Elasticsearch | 9200 | http://localhost:9200 |
| RabbitMQ管理界面 | 15672 | http://localhost:15672 |
| Flower (Celery监控) | 5555 | http://localhost:5555 |
| Kibana | 5601 | http://localhost:5601 |
| Prometheus | 9090 | http://localhost:9090 |
| Grafana | 3001 | http://localhost:3001 |

### 主要脚本

- `dev.sh` - 主控制脚本
- `scripts/start-dev.sh` - 开发环境启动脚本
- `scripts/stop-dev.sh` - 服务停止脚本
- `scripts/status.sh` - 状态查看脚本
- `scripts/monitor-services.sh` - 服务监控脚本
- `scripts/verify-env.sh` - 环境验证脚本

### 日志文件

所有日志文件位于 `logs/` 目录：

- `backend.log` - 后端服务日志
- `frontend.log` - 前端服务日志
- `monitor.log` - 监控日志
- `error.log` - 错误日志
- `startup.log` - 启动日志
- `status.log` - 状态日志

### 配置文件

- `.env` - 环境变量配置
- `.env.development` - 开发环境配置
- `docker-compose.dev.yml` - 开发环境Docker配置
- `config/` - 各种服务配置文件

### 开发建议

1. **代码格式化**
```bash
# 后端
cd backend
black .
isort .

# 前端
cd frontend
npm run lint
npm run format
```

2. **测试运行**
```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

3. **数据库操作**
```bash
# 创建迁移
cd backend
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 创建管理员
python scripts/create_admin.py 用户名 邮箱 密码
```

## 常见问题

### 1. 端口冲突
如果遇到端口冲突，请检查并停止占用端口的服务：
```bash
# 查看端口占用
lsof -i :<端口号>

# 修改端口
vim .env
```

### 2. 权限问题
如果遇到Docker权限问题：
```bash
# 添加用户到docker组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker
```

### 3. 依赖问题
如果遇到依赖安装失败：
```bash
# 清理npm缓存
npm cache clean --force

# 清理pip缓存
pip cache purge

# 重新安装
pip install -r requirements.txt
npm install
```

### 4. 服务启动失败
1. 检查配置文件
2. 查看日志文件
3. 验证环境设置：
```bash
./dev.sh verify
```

## 开发规范

### 1. 提交代码
```bash
# 安装pre-commit hooks
pip install pre-commit
pre-commit install

# 运行代码检查
pre-commit run --all-files
```

### 2. 分支管理
- 主分支: `main`
- 开发分支: `develop`
- 功能分支: `feature/<功能名>`
- 修复分支: `hotfix/<问题描述>`

### 3. 代码审查
- 所有代码必须通过CI/CD检查
- 提交信息必须符合规范
- PR必须包含适当的测试

## 监控与调试

### 1. 服务监控
```bash
# 启动监控
./scripts/monitor-services.sh

# 查看监控状态
./dev.sh status
```

### 2. 日志查看
```bash
# 查看实时日志
./dev.sh logs <服务名>

# 查看错误日志
./dev.sh logs error
```

### 3. 性能分析
- 使用Prometheus收集指标
- 使用Grafana可视化数据
- 配置告警规则

## 生产环境部署

### 1. 构建镜像
```bash
# 构建后端镜像
docker build -t soccer-scanning-system/backend ./backend

# 构建前端镜像
docker build -t soccer-scanning-system/frontend ./frontend
```

### 2. 部署服务
```bash
# 使用生产配置
docker-compose -f docker-compose.yml up -d

# 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 创建管理员账户
docker-compose exec backend python scripts/create_admin.py admin admin@example.com secure_password
```

## 技术支持

如果遇到问题：

1. 查看文档目录：`docs/`
2. 检查已知问题：`docs/troubleshooting.md`
3. 提交问题：GitHub Issues

## 更多资源

- [开发文档](docs/development-setup.md)
- [API文档](docs/api/)
- [架构设计](docs/architecture/)
- [部署指南](docs/deployment/)