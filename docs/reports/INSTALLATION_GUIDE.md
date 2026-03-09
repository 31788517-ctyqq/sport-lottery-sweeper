# 项目安装和启动指南

## 前端依赖安装

由于前端依赖包尚未安装，需要执行以下步骤：

### 1. 安装pnpm（如果尚未安装）
```bash
# 使用npm安装pnpm
npm install -g pnpm

# 或使用其他方式安装
# 详情参见: https://pnpm.io/installation
```

### 2. 安装前端依赖
```bash
# 进入前端目录
cd frontend

# 安装依赖包
pnpm install
```

### 3. 启动前端开发服务器
```bash
# 在frontend目录下执行
pnpm run dev
```

## 后端启动

### 1. 安装Python依赖
```bash
# 确保已激活虚拟环境（如果使用的话）
pip install -r requirements.txt
```

### 2. 启动后端服务
```bash
# 在项目根目录下执行
cd backend
python main.py
# 或者使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 环境配置

### 1. 复制环境变量文件
```bash
# 复制后端环境变量文件
cp .env.example .env
cp backend.env .env  # 如果需要特定后端配置

# 复制前端环境变量文件
cd frontend
cp .env.development .env
```

### 2. 根据需要修改环境变量
编辑 `.env` 文件，配置数据库连接、API密钥等。

## Docker部署

### 1. 使用Docker Compose快速启动
```bash
# 开发环境
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 生产环境
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
```

### 2. 单独构建前端或后端镜像
```bash
# 构建前端镜像
docker build -t sport-lottery-frontend -f Dockerfile.frontend .

# 构建后端镜像
docker build -t sport-lottery-backend -f Dockerfile.backend .
```

## 项目健康检查

### 1. 检查前端依赖安装状态
```bash
cd frontend
pnpm list
```

### 2. 检查后端依赖安装状态
```bash
pip list
```

### 3. 运行测试
```bash
# 后端测试
cd backend
python -m pytest tests/

# 前端测试
cd frontend
pnpm run test
```

## 安全修复说明

### 1. 已修复eval()函数使用问题
在 `backend/debug_scraper_enhanced.py` 文件中，已将不安全的 JavaScript `eval()` 调用替换为安全的属性访问方法。

### 2. 状态管理统一
前端已统一使用 Pinia 作为状态管理方案，移除了 Vuex 相关的冗余配置。

## 性能优化建议

1. 实施缓存策略，减少重复数据请求
2. 对数据库查询添加适当的索引
3. 使用懒加载技术优化前端组件加载
4. 实现分页机制处理大量数据