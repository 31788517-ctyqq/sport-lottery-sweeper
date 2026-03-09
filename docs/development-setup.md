# 开发环境搭建指南

## 环境要求

- Docker >= 20.10.0
- Docker Compose >= 2.0.0
- Python >= 3.8
- Node.js >= 16.0.0
- npm >= 8.0.0

## 快速开始

1. 克隆项目
```bash
git clone <repository-url>
cd soccer-scanning-system
```

2. 环境准备
```bash
# 复制环境变量文件
cp .env.example .env

# 创建必要的目录
mkdir -p logs
mkdir -p data/{postgres,redis,rabbitmq,mongodb,elasticsearch}
```

3. 启动基础服务
```bash
# 启动数据库、缓存、消息队列等服务
docker-compose -f docker-compose.dev.yml up -d db redis rabbitmq mongodb elasticsearch

# 等待服务就绪
docker-compose -f docker-compose.dev.yml ps
```

4. 启动后端服务
```bash
cd backend

# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head

# 初始化基础数据
python scripts/init_db.py

# 创建管理员账户
python scripts/create_admin.py admin admin@example.com admin123

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. 启动前端服务
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 使用启动脚本

如果您想一键启动所有服务，可以使用提供的启动脚本：

1. 环境检查（首次运行）
```bash
./scripts/check-requirements.sh
```

2. 启动所有服务
```bash
./scripts/start-dev.sh
```

3. 停止所有服务
```bash
./scripts/stop-dev.sh
```

## 服务访问

启动完成后，您可以通过以下地址访问各个服务：

- 前端应用: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- RabbitMQ管理界面: http://localhost:15672
- Flower (Celery监控): http://localhost:5555
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

## 开发建议

1. **代码格式化**
```bash
# 后端
cd backend
black . --line-length 79
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
npm run test:e2e
```

3. **日志查看**
```bash
# 基础服务日志
docker-compose -f docker-compose.dev.yml logs -f

# 后端日志
tail -f logs/backend.log

# 前端日志
tail -f logs/frontend.log
```

## 常见问题

1. **端口冲突**
如果遇到端口冲突，请检查并停止占用端口的服务：
```bash
# 查看端口占用
lsof -i :<端口号>

# 修改端口
vim docker-compose.dev.yml
```

2. **权限问题**
如果遇到Docker权限问题：
```bash
# 将用户添加到docker组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker
```

3. **依赖问题**
如果遇到依赖安装失败：
```bash
# 清理npm缓存
npm cache clean --force

# 清理pip缓存
pip cache purge

# 重新安装
pip install --no-cache-dir -r requirements.txt
npm install --force
```

4. **数据库连接问题**
如果遇到数据库连接错误：
```bash
# 检查数据库状态
docker-compose -f docker-compose.dev.yml ps db

# 查看数据库日志
docker-compose -f docker-compose.dev.yml logs db

# 重启数据库服务
docker-compose -f docker-compose.dev.yml restart db
```

## 开发规范

1. **提交代码**
```bash
# 安装pre-commit钩子
pip install pre-commit
pre-commit install

# 运行检查
pre-commit run --all-files
```

2. **分支管理**
- 主分支: `main`
- 开发分支: `develop`
- 功能分支: `feature/<功能名>`
- 修复分支: `hotfix/<问题描述>`

3. **代码审查**
- 所有代码必须通过CI/CD检查
- 提交信息必须符合规范
- PR必须包含适当的测试

## 环境变量

主要环境变量说明：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_USER=soccer_user
DB_PASSWORD=soccer_pass
DB_NAME=soccer_db

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_pass

# API配置
API_V1_STR=/api/v1
SECRET_KEY=your-secret-key-here

# 前端配置
VITE_API_URL=http://localhost:8000
```

## 性能优化

1. **后端优化**
- 使用连接池
- 启用查询缓存
- 配置适当的日志级别

2. **前端优化**
- 启用代码分割
- 配置适当的缓存策略
- 使用CDN加速

## 监控与调试

1. **应用监控**
- 使用Prometheus收集指标
- 使用Grafana可视化数据
- 配置告警规则

2. **日志管理**
- 使用ELK Stack收集日志
- 配置日志级别
- 设置日志轮转