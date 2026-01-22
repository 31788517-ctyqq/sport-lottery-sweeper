# Sport Lottery Sweeper 项目结构文档

## 项目概述

Sport Lottery Sweeper 是一个体育彩票数据采集与分析系统，包含后端数据处理服务和前端展示界面。该项目旨在提供体育赛事数据的自动化采集、审核和展示功能。

## 整体目录结构

```
sport-lottery-sweeper/
├── .coverage                    # 代码覆盖率报告
├── .dockerignore               # Docker 构建忽略文件
├── .env.example                # 环境变量示例文件
├── .env.local                  # 本地环境变量配置
├── .env.production             # 生产环境变量配置
├── .git/                       # Git 版本控制目录
├── .github/                    # GitHub 配置目录
├── .gitignore                  # Git 忽略文件配置
├── .gitignore.txt              # Git 忽略文件配置（文本版）
├── .vscode/                    # VSCode 编辑器配置
├── API_DOCUMENTATION.md        # API 文档
├── Dockerfile                  # Docker 构建文件
├── Dockerfile.dev              # 开发环境 Dockerfile
├── Dockerfile.production       # 生产环境 Dockerfile
├── LICENSE                     # 许可证文件
├── Makefile                    # Make 工具配置
├── PERFORMANCE_REPORT.md       # 性能报告
├── README.md                   # 项目说明文件
├── RUNNING_GUIDE.md            # 运行指南
├── alembic/                    # Alembic 数据库迁移工具配置
├── alembic.ini                 # Alembic 配置文件
├── app.log                     # 应用日志文件
├── backend/                    # 后端 Python 服务目录
├── backend.env                 # 后端环境变量配置
├── backups/                    # 备份文件目录
├── config/                     # 配置文件目录
├── crawler/                    # 爬虫模块目录
├── crawler.env                 # 爬虫环境变量配置
├── date/                       # 日期相关文件目录
├── docker/                     # Docker 相关配置目录
├── docker-compose.dev.yml      # 开发环境 Docker Compose 配置
├── docker-compose.override.yml # Docker Compose 覆盖配置
├── docker-compose.prod.yml     # 生产环境 Docker Compose 配置
├── docker-compose.production.yml # 生产环境 Docker Compose 配置
├── docker-compose.yml          # 主 Docker Compose 配置
├── docs/                       # 文档目录
├── env.development             # 开发环境变量
├── env.example                 # 环境变量示例
├── frontend/                   # 前端 Vue 项目目录
├── frontend.env                # 前端环境变量配置
├── htmlcov/                    # HTML 代码覆盖率报告
├── logs/                       # 日志目录
├── node_modules/               # Node.js 依赖包目录
├── null                        # 空文件
├── package-lock.json           # Node.js 锁定依赖版本文件
├── package.json                # Node.js 项目配置
├── page_content.html           # 页面内容文件
├── poetry.lock                 # Poetry 依赖锁定文件
├── pyproject.toml              # Python 项目配置文件
├── requirements-dev-utf8.txt   # 开发环境依赖（UTF-8编码）
├── requirements-dev.txt        # 开发环境依赖
├── requirements-windows.txt    # Windows 环境依赖
├── requirements.txt            # Python 依赖文件
├── scraper/                    # 数据抓取工具目录
├── scripts/                    # 脚本目录
├── start_project.bat           # Windows 批处理启动脚本
├── start_project.ps1           # PowerShell 启动脚本
├── tests/                      # 测试文件目录
├── tianyun/                    # 天云相关文件目录
├── venv/                       # Python 虚拟环境目录
├── venv_new/                   # 新的 Python 虚拟环境目录
└── wendang/                    # 文档目录
```

## 后端目录结构 (backend/)

```
backend/
├── __init__.py                 # 初始化文件
├── __pycache__/                # Python 缓存目录
├── admin/                      # 管理后台模块
│   ├── __init__.py
│   ├── api/                    # 管理后台 API
│   └── models/                 # 管理后台数据模型
├── alembic/                    # 数据库迁移配置
├── api/                        # API 接口定义
│   ├── __init__.py
│   └── v1/                     # API V1 版本
├── api.py                      # API 主入口
├── config.py                   # 配置文件
├── core/                       # 核心功能模块
├── database.py                 # 数据库连接配置
├── debug_*.py                  # 调试相关脚本
├── dependencies.py             # 依赖注入定义
├── main.py                     # 应用主入口
├── middleware.py               # 中间件定义
├── models/                     # 数据模型定义
├── schemas/                    # Pydantic 模型定义
├── scrapers/                   # 数据爬虫模块
├── services/                   # 业务服务层
├── static/                     # 静态文件目录
├── tasks/                      # 定时任务模块
├── tests/                      # 后端测试文件
├── utils/                      # 工具函数模块
├── *.db                        # SQLite 数据库文件
└── 其他 Python 脚本文件
```

### 后端模块说明

- **admin/**: 管理员后台相关功能
- **api/**: REST API 接口定义，按版本分目录管理
- **core/**: 应用核心功能模块，包括认证、权限等
- **models/**: SQLAlchemy 数据模型定义
- **schemas/**: Pydantic 数据传输对象定义
- **scrapers/**: 数据爬虫实现，负责从各渠道采集体育赛事数据
- **services/**: 业务逻辑服务层
- **utils/**: 通用工具函数

## 前端目录结构 (frontend/)

```
frontend/
├── .env.development            # 开发环境配置
├── .env.production.txt         # 生产环境配置
├── .env.txt                    # 环境配置模板
├── .eslintignore.txt           # ESLint 忽略配置
├── Dockerfile.dev              # 前端开发环境 Dockerfile
├── package.json                # npm 项目配置
├── pnpm-lock.yaml              # pnpm 依赖锁定文件
├── vite.config.js              # Vite 构建配置
├── src/                        # 源代码目录
│   ├── App.vue                 # Vue 主组件
│   ├── api/                    # API 接口封装
│   ├── assets/                 # 静态资源
│   ├── components/             # Vue 组件
│   ├── composables/            # Vue 组合式 API 函数
│   ├── directives/             # Vue 自定义指令
│   ├── i18n/                   # 国际化配置
│   ├── main.js                 # Vue 应用入口
│   ├── router/                 # Vue 路由配置
│   ├── store/                  # 状态管理（Vuex 或 Pinia）
│   ├── styles/                 # 样式文件
│   ├── utils/                  # 工具函数
│   └── views/                  # 页面视图组件
├── public/                     # 公共静态资源
├── index.html                  # 主页面模板
└── 其他配置文件
```

### 前端模块说明

- **api/**: 与后端 API 的交互逻辑
- **components/**: 可复用的 UI 组件
- **views/**: 页面级组件
- **router/**: 前端路由配置
- **store/**: 状态管理（全局数据流）
- **utils/**: 前端工具函数
- **assets/**: 图片、样式等静态资源

## 主要技术栈

### 后端技术栈
- **Python**: 主要开发语言
- **FastAPI**: Web 框架，提供高性能 API
- **SQLAlchemy**: ORM 框架
- **Alembic**: 数据库迁移工具
- **Pydantic**: 数据验证和序列化

### 前端技术栈
- **Vue.js 3**: 前端框架
- **Vite**: 构建工具
- **TypeScript**: 类型安全（部分使用）
- **Tailwind CSS**: CSS 框架
- **Pinia/Vuex**: 状态管理

## 部署配置

- **Docker**: 容器化部署
- **Docker Compose**: 多容器编排
- **多环境配置**: 支持开发、测试、生产环境

## 项目特点

1. **数据审核流程**: 所有数据必须经过后台审核才能发布
2. **模块化架构**: 清晰的前后端分离架构
3. **自动化爬虫**: 实现体育赛事数据自动采集
4. **多环境支持**: 支持不同环境的配置切换
5. **容器化部署**: 使用 Docker 简化部署流程