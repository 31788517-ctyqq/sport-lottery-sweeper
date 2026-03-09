# 多IDE开发环境问题和解决方案指南

## 问题概述

在使用多个IDE（如Codex、通义灵码、CodeBuddy）和多个账号进行开发时，经常出现项目打不开、路由错误、端口冲突、4xx/5xx错误等问题，影响开发效率。

## 问题原因分析

### 1. 环境配置不一致
- Python虚拟环境路径不一致
- Node.js/npm版本不同
- 系统环境变量设置不同
- 依赖包版本不一致

### 2. 项目状态不一致
- Git分支状态不一致
- 本地修改未同步
- 依赖包版本不一致
- 缓存状态不同

### 3. 服务状态冲突
- 端口被占用（如8000、3000端口）
- 服务进程未正确关闭
- 数据库连接冲突
- 缓存状态不一致

### 4. IDE配置差异
- 编辑器配置不同
- 插件版本不一致
- 编译/构建缓存不同
- 文件编码设置不同

## 多IDE协同开发文档规范

在多IDE协同开发环境中，文档管理尤为重要，以下是一些关键的文档规范建议：

### 1. 文档版本控制
- 所有文档变更必须通过Git进行版本控制
- 重要文档更新需提交PR并经团队成员审核
- 避免多人同时编辑同一文档造成冲突

### 2. 文档命名与组织
- 文档命名应具有明确的语义（如 `multi-ide-setup-guide.md`）
- 按功能或模块组织文档目录（如 `docs/setup/`, `docs/api/`, `docs/troubleshooting/`）
- 为重要文档添加版本号（如 `api-spec-v1.2.md`）

### 3. 文档内容标准化
- 为同类文档建立模板，确保格式统一
- 文档应包含作者、创建时间、最后更新时间和适用版本
- 关键配置和操作步骤应有明确的验证方法

### 4. 文档实时性维护
- 建立文档更新与代码变更的联动机制
- 在每次重大功能变更后同步更新相关文档
- 设立文档维护责任人，定期审查文档有效性

### 5. 文档共享与通知
- 重要文档更新应及时通知团队成员
- 建立文档索引页，方便快速查找
- 使用评论系统或协作工具讨论文档内容

## 解决方案

### 1. 标准化开发环境

#### 使用统一的环境配置
```bash
# 检查当前Python环境
python -c "import sys; print(sys.executable)"

# 检查当前Node版本
node --version && npm --version

# 使用统一的依赖管理
pip install -r requirements.txt
cd frontend && npm ci
```

#### 推荐使用容器化开发
```yaml
# docker-compose.yml 示例
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - ENV=development

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
```

### 2. 标准化开发流程

#### 开发前准备
```bash
# 1. 同步代码
git pull origin main

# 2. 检查依赖
pip install -r requirements.txt
cd frontend && npm ci && cd ..

# 3. 清理旧进程
# Windows: taskkill /f /im python.exe && taskkill /f /im node.exe
# Linux/Mac: pkill -f python && pkill -f node
```

#### 开发中注意事项
- 使用固定端口（后端8000，前端3000）
- 避免直接修改全局配置文件
- 使用Git分支隔离不同功能开发
- 定期提交代码，避免长时间未同步

#### 切换IDE前
```bash
# 1. 保存并提交代码
git add .
git commit -m "Work in progress"

# 2. 停止所有开发服务
# Windows: taskkill /f /im python.exe && taskkill /f /im node.exe
# Linux/Mac: pkill -f python && pkill -f node

# 3. 清理缓存
# 删除 .vite、__pycache__ 等缓存目录
rm -rf backend/__pycache__/
rm -rf frontend/node_modules/.vite
rm -rf frontend/dist
```

### 3. 项目状态验证脚本

创建一个脚本来验证项目状态：

```bash
# check-project-status.sh
#!/bin/bash
echo "Checking project status..."

# 检查端口占用
echo "Checking port 8000:"
netstat -an | grep :8000 | head -1
echo "Checking port 3000:"
netstat -an | grep :3000 | head -1

# 检查Git状态
echo "Git status:"
git status --porcelain

# 检查依赖一致性
echo "Dependency check..."
pip check 2>/dev/null || echo "Python dependencies OK or not installed"
cd frontend && npm ls --depth=0 2>/dev/null || echo "Node dependencies OK or not installed"
```

### 4. 防冲突最佳实践

#### A. 使用统一的配置管理
- 将环境配置保存在 `.env.example` 文件中
- 每个开发者复制为 `.env.local` 并个性化配置
- 避免将个人配置提交到版本控制系统

#### B. 建立标准化启动脚本
```bash
# backend-start.sh
#!/bin/bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# frontend-start.sh
#!/bin/bash
cd frontend
npm run dev
```

#### C. 使用独立的开发环境
- 为每个IDE/账号创建独立的开发分支
- 使用特性分支开发，避免在主分支上直接开发
- 定期合并主分支更新到特性分支

## 协同开发最佳实践

### 1. 分工明确
- 按功能模块划分开发任务，避免多人同时开发同一模块
- 建立开发日历，提前协调可能冲突的开发任务
- 定期同步开发进度，及时发现潜在冲突

### 2. 沟通机制
- 建立专门的开发沟通渠道（如微信群、Slack频道）
- 开发前通报开发计划，开发后同步开发结果
- 遇到问题及时寻求帮助，避免重复解决相同问题

### 3. 代码审查
- 所有代码变更都需要经过至少一人审查
- 建立代码审查清单，确保代码质量
- 审查不仅关注功能实现，还要关注对其他模块的影响

## 问题排查清单

当遇到项目打不开、路由错误等问题时，按以下步骤排查：

1. **检查端口占用**：
   - 后端服务是否占用了8000端口
   - 前端服务是否占用了3000端口

2. **检查服务状态**：
   - 是否有残留的Python/Node进程
   - 数据库连接是否正常

3. **检查代码同步**：
   - Git状态是否干净
   - 是否有未提交的修改

4. **检查依赖**：
   - Python包是否安装完整
   - Node模块是否安装完整

5. **检查配置**：
   - 环境变量是否正确
   - 数据库连接配置是否正确

## 建议措施

### 1. 建立开发规范文档
- 明确环境配置要求
- 规定标准开发流程
- 建立问题处理流程

### 2. 使用容器化开发环境
- 统一所有开发者的环境
- 避免环境差异导致的问题
- 简化环境配置流程

### 3. 建立自动化工具
- 创建一键启动/停止脚本
- 建立项目状态检查工具
- 实现自动清理残留进程功能

### 4. 加强团队沟通
- 建立共享的开发问题记录
- 定期同步开发环境配置
- 及时分享解决方案