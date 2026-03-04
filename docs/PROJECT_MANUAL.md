# 体育彩票扫盘系统项目说明书

**版本**: v1.0  
**作者**: Sport Lottery Sweeper Team  
**文档ID**: SLS-DOC-001  
**更新日期**: 2026-02-27

## 目录

1. [项目概述](#项目概述)
2. [技术架构](#技术架构)
3. [项目结构](#项目结构)
4. [功能模块](#功能模块)
5. [安装与部署](#安装与部署)
6. [开发规范](#开发规范)
7. [测试体系](#测试体系)
8. [运维指南](#运维指南)
9. [常见问题](#常见问题)

## 项目概述

### 项目简介

体育彩票扫盘系统（Sport Lottery Sweeper）是一个用于采集、分析和管理体育赛事数据的综合性平台。系统通过爬虫技术获取各大彩票网站的实时数据，提供智能化数据分析和筛选功能，辅助用户进行彩票分析和决策。

### 项目目标

- 实时采集各大彩票网站的赛事数据
- 提供数据分析和智能筛选功能
- 构建可视化管理后台
- 支持多策略自动筛选与消息通知
- 保障数据安全与系统稳定性

### 核心功能

- 数据源管理：支持多种数据源配置与管理
- 爬虫监控：实时监控爬虫运行状态
- 智能筛选：多维度赛事数据分析与筛选
- 用户管理：角色权限控制与用户管理
- 消息通知：支持钉钉等即时通讯工具通知

## 技术架构

### 技术栈

#### 后端技术栈
- **Python 3.9+**: 主要编程语言
- **FastAPI**: Web框架，提供高性能API服务
- **SQLAlchemy**: ORM框架，管理数据库操作
- **SQLite/PostgreSQL**: 数据库存储
- **Pydantic**: 数据验证和设置管理
- **Requests**: HTTP请求处理
- **Celery**: 异步任务队列（可选）

#### 前端技术栈
- **Vue 3**: 前端框架
- **Element Plus**: UI组件库
- **Vite**: 构建工具
- **Axios**: HTTP客户端
- **Pinia**: 状态管理
- **Vue Router**: 路由管理

#### 部署技术栈
- **Docker**: 容器化部署
- **Docker Compose**: 多服务编排
- **Nginx**: 反向代理和负载均衡
- **PM2**: Node.js进程管理（可选）
- **GitHub Actions**: CI/CD自动化部署

### 架构设计

系统采用前后端分离架构，后端提供RESTful API接口，前端通过HTTP请求与后端交互。整体架构分为以下几个层次：

1. **表示层**: Vue前端应用，提供用户界面
2. **服务层**: FastAPI后端服务，处理业务逻辑
3. **数据访问层**: SQLAlchemy ORM，处理数据库操作
4. **数据存储层**: SQLite/PostgreSQL数据库
5. **消息通知层**: 支持钉钉等即时通讯工具

## 项目结构

```
sport-lottery-sweeper/
├── backend/                 # 后端代码
│   ├── api/                 # API路由定义
│   │   └── v1/             # API v1版本
│   │       ├── __init__.py
│   │       ├── admin/       # 管理后台API
│   │       ├── auth/        # 认证API
│   │       ├── crawler/     # 爬虫相关API
│   │       └── lottery/     # 彩票相关API
│   ├── models/              # 数据模型定义
│   │   ├── __init__.py
│   │   ├── base.py         # 基础模型
│   │   ├── matches.py      # 比赛数据模型
│   │   └── user.py         # 用户模型
│   ├── schemas/             # Pydantic模型定义
│   ├── services/            # 业务逻辑服务
│   ├── utils/               # 工具函数
│   ├── scrapers/            # 爬虫实现
│   ├── database.py          # 数据库连接配置
│   ├── main.py              # 主应用入口
│   └── config.py           # 配置文件
├── frontend/                # 前端代码
│   ├── src/                 # 源代码
│   │   ├── components/      # 通用组件
│   │   ├── views/          # 页面视图
│   │   ├── api/            # API请求封装
│   │   ├── store/          # Pinia状态管理
│   │   ├── router/         # 路由配置
│   │   ├── assets/         # 静态资源
│   │   ├── styles/         # 样式文件
│   │   └── main.js         # 应用入口
│   ├── public/             # 静态资源
│   ├── package.json        # 前端依赖
│   └── vite.config.js      # Vite构建配置
├── docs/                   # 文档目录
├── scripts/                # 脚本目录
├── docker/                 # Docker相关配置
├── .env.example           # 环境变量示例
├── docker-compose.yml     # Docker编排配置
├── requirements.txt       # Python依赖
└── README.md             # 项目说明
```

## 功能模块

### 1. 数据源管理模块

**功能描述**: 管理和配置数据采集源

**主要功能**:
- 添加/编辑/删除数据源
- 测试数据源连接
- 数据源状态监控
- 批量操作支持

**技术实现**:
- 前端: Vue组件实现数据源管理界面
- 后端: FastAPI提供CRUD接口
- 数据库: SQLite/PostgreSQL存储配置

### 2. 爬虫监控模块

**功能描述**: 监控爬虫运行状态和数据采集情况

**主要功能**:
- 实时监控爬虫状态
- 采集成功率统计
- 异常日志记录
- 性能指标展示

**技术实现**:
- 前端: ECharts图表展示监控数据
- 后端: 定时任务检查爬虫状态
- 日志: 详细记录爬虫运行情况

### 3. 比赛数据管理模块

**功能描述**: 管理采集到的体育比赛数据

**主要功能**:
- 比赛数据展示
- 数据筛选与搜索
- 数据统计分析
- 数据导出功能

**技术实现**:
- 前端: Element Plus表格组件
- 后端: 数据库查询与过滤
- API: RESTful接口设计

### 4. 用户管理模块

**功能描述**: 管理系统用户和权限

**主要功能**:
- 用户注册/登录
- 角色权限管理
- 用户信息维护
- 操作日志记录

**技术实现**:
- 前端: 登录注册页面
- 后端: JWT认证机制
- 数据库: 用户表设计

### 5. 智能筛选模块

**功能描述**: 多维度赛事数据分析与筛选

**主要功能**:
- 多策略筛选条件配置
- 自动化策略执行
- 筛选结果通知
- 筛选历史记录

**技术实现**:
- 算法: 数据分析算法
- 通知: 钉钉机器人集成
- 调度: 定时任务执行

## 安装与部署

### 环境要求

- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.9+
- **Node.js**: 16+
- **Docker**: 20.10+ (可选)
- **Git**: 2.25+

### 本地开发环境搭建

#### 1. 克隆项目

```bash
git clone https://github.com/ctyqq/sport-lottery-sweeper.git
cd sport-lottery-sweeper
```

#### 2. 配置后端环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
# 修改SECRET_KEY、数据库连接等配置
```

#### 3. 配置前端环境

```bash
cd frontend

# 安装依赖
npm install
# 或使用 pnpm
pnpm install

# 启动开发服务器
npm run dev
# 或
pnpm dev
```

#### 4. 启动后端服务

```bash
# 在项目根目录
cd backend
python -m main
```

### Docker部署

#### 1. 构建镜像

```bash
# 构建并启动服务
docker-compose up -d
```

#### 2. 部署生产环境

```bash
# 使用生产配置
docker-compose -f docker-compose.prod.yml up -d
```

### 自动化部署

系统支持GitHub Actions自动化部署，配置文件位于`.github/workflows/deploy.yml`。

## 开发规范

### 代码规范

#### Python代码规范

- 遵循PEP 8编码规范
- 使用Google风格的文档字符串
- 变量命名采用snake_case格式
- 类名采用PascalCase格式
- 常量使用UPPER_CASE格式

#### JavaScript代码规范

- 遵循ESLint标准
- 使用Vue 3 Composition API
- 组件命名采用PascalCase格式
- 方法命名采用camelCase格式
- 文件命名使用kebab-case格式

### Git规范

- 分支命名: `feature/功能名`, `bugfix/问题描述`, `hotfix/紧急修复`
- 提交信息: 使用约定式提交格式
  - `feat: 新功能`
  - `fix: 修复bug`
  - `docs: 文档更新`
  - `style: 代码格式调整`
  - `refactor: 重构`
  - `test: 测试相关`
  - `chore: 构建过程或辅助工具变动

### API设计规范

- 使用RESTful API设计原则
- 状态码遵循HTTP标准
- 返回数据结构统一
- 错误处理机制完善
- 接口文档完整

## 测试体系

### 单元测试

- 后端: 使用pytest框架
- 前端: 使用Vitest框架
- 覆盖率要求: ≥85%

### 集成测试

- 测试模块间协作
- 验证数据流转正确性
- 模拟真实使用场景

### 端到端测试

- 使用Playwright进行UI测试
- 覆盖核心用户流程
- 自动化回归测试

## 运维指南

### 日志管理

- 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
- 日志格式: JSON格式，便于分析
- 日志轮转: 按大小或时间切割

### 监控告警

- 系统健康检查: `/health`端点
- 性能监控: 响应时间、吞吐量
- 异常监控: 错误率、异常日志

### 备份恢复

- 数据库定期备份
- 配置文件版本控制
- 环境变量安全存储

## 常见问题

### 启动问题

**问题**: 后端启动失败，端口被占用
**解决方案**: 
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

**问题**: 前端页面404错误
**解决方案**: 检查Vite配置，确认路由模式为history模式

### 数据库问题

**问题**: 数据库连接失败
**解决方案**: 
1. 检查数据库服务是否启动
2. 验证连接字符串格式
3. 确认数据库文件权限

### 部署问题

**问题**: Docker部署失败
**解决方案**: 
1. 确认Docker服务已启动
2. 检查Dockerfile语法
3. 验证镜像构建上下文

---

**版权**: © 2026 体育彩票扫盘系统开发团队