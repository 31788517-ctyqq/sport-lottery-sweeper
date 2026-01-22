# Sport Lottery Sweeper 最新项目结构文档

## 项目概述

Sport Lottery Sweeper 是一个专业的体育彩票数据采集与分析系统，主要功能是自动化采集体育赛事数据并提供分析工具。项目采用前后端分离架构，后端使用 FastAPI 框架，前端使用 Vue.js 框架。

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
├── .vscode/                    # VSCode 编辑器配置
├── API_DOCUMENTATION.md        # API 文档
├── CLEANUP_SUGGESTIONS.md      # 项目清理建议文档
├── Dockerfile                  # 生产环境 Docker 构建文件
├── Dockerfile.dev              # 开发环境 Dockerfile
├── Dockerfile.production       # 生产环境 Dockerfile
├── LICENSE                     # 许可证文件
├── Makefile                    # Make 工具配置
├── PERFORMANCE_REPORT.md       # 性能报告
├── PROJECT_STRUCTURE.md        # 旧版项目结构文档
├── NEW_PROJECT_STRUCTURE.md    # 当前项目结构文档
├── README.md                   # 项目说明文件
├── RUNNING_GUIDE.md            # 运行指南
├── alembic/                    # Alembic 数据库迁移工具配置
├── alembic.ini                 # Alembic 配置文件
├── backend/                    # 后端 Python 服务目录
├── backend.env                 # 后端环境变量配置
├── config/                     # 配置文件目录
├── crawler.env                 # 爬虫环境变量配置
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
├── package-lock.json           # Node.js 锁定依赖版本文件
├── package.json                # Node.js 项目配置
├── poetry.lock                 # Poetry 依赖锁定文件
├── pyproject.toml              # Python 项目配置文件
├── requirements-dev-utf8.txt   # 开发环境依赖（UTF-8编码）
├── requirements-dev.txt        # 开发环境依赖
├── requirements-windows.txt    # Windows 环境依赖
├── requirements.txt            # Python 依赖文件
├── scripts/                    # 脚本目录
├── start_project.bat           # Windows 批处理启动脚本
├── start_project.ps1           # PowerShell 启动脚本
└── tests/                      # 测试文件目录
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
│   ├── __init__.py
│   ├── auth.py                 # 认证模块
│   ├── config.py               # 核心配置
│   ├── database.py             # 数据库配置
│   ├── dependencies.py         # 依赖项
│   ├── hashing.py              # 加密哈希
│   ├── jwt.py                  # JWT 认证
│   ├── middleware.py           # 中间件
│   ├── models.py               # 数据模型
│   ├── schemas.py              # 数据结构定义
│   ├── security.py             # 安全相关
│   └── validators.py           # 验证器
├── database.py                 # 数据库连接配置
├── debug_*.py                  # 调试相关脚本
├── dependencies.py             # 依赖注入定义
├── lembic/                     # 另一个数据库迁移配置（可能是重复的）
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
└── 其他 Python 脚本文件（爬虫、数据处理等）
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
- **debug_*.py**: 一系列调试脚本，用于测试不同的爬虫和数据获取方法

## 前端目录结构 (frontend/)

```
frontend/
├── .env.development            # 开发环境配置
├── .env.production.txt         # 生产环境配置
├── .env.txt                    # 环境配置模板
├── .eslintignore.txt           # ESLint 忽略配置
├── 1                           # 临时文件或配置
├── Dockerfile.dev              # 前端开发环境 Dockerfile
├── OPTIMIZATION_README.md      # 前端优化说明文档
├── cypress.config.js           # Cypress 测试配置
├── demo.html                   # 演示页面
├── eslint.config.js            # ESLint 配置
├── index-optimized.html        # 优化后的主页
├── index.html                  # 主页面模板
├── index.scss                  # SCSS 样式文件
├── jczq_schedule.html          # 竞彩足球赛程页面
├── package.json                # npm 项目配置
├── pnpm-lock.yaml              # pnpm 依赖锁定文件
├── postcss.config.js           # PostCSS 配置
├── prettier.config.js          # Prettier 代码格式化配置
├── preview.html                # 预览页面
├── public/                     # 公共静态资源
│   ├── favicon.ico
│   ├── index.html
│   └── manifest.json
├── src/                        # 源代码目录
│   ├── App.vue                 # Vue 主组件
│   ├── api/                    # API 接口封装
│   ├── assets/                 # 静态资源
│   ├── components/             # Vue 组件
│   ├── composables/            # Vue 组合式 API 函数
│   ├── directives/             # Vue 自定义指令
│   ├── i18n/                   # 国际化配置
│   ├── main-app.js             # Vue 应用入口（较大）
│   ├── main.js                 # Vue 应用入口（较小）
│   ├── router/                 # Vue 路由配置
│   ├── store/                  # 状态管理（Vuex 或 Pinia）
│   ├── styles/                 # 样式文件
│   ├── tests/                  # 前端测试文件
│   ├── utils/                  # 工具函数
│   └── views/                  # 页面视图组件
├── tailwind.config.js          # Tailwind CSS 配置
├── utils/                      # 工具函数目录
├── vite.config.js              # Vite 构建配置
└── vitest.config.js            # Vitest 测试配置
```

### 前端模块说明

- **api/**: 与后端 API 的交互逻辑
- **components/**: 可复用的 UI 组件
- **views/**: 页面级组件
- **router/**: 前端路由配置
- **store/**: 状态管理（全局数据流）
- **utils/**: 前端工具函数
- **assets/**: 图片、样式等静态资源
- **composables/**: Vue 3 组合式 API 函数

## 主要技术栈

### 后端技术栈
- **Python 3.11**: 主要开发语言
- **FastAPI**: 现代高性能 Web 框架
- **SQLAlchemy**: ORM 框架
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI 服务器

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

1. **数据采集自动化**: 通过多种爬虫技术自动采集体育赛事数据
2. **模块化架构**: 清晰的前后端分离架构
3. **多数据源支持**: 支持从不同来源获取数据
4. **调试友好**: 包含大量调试脚本，便于开发和问题排查
5. **多环境支持**: 完整的开发、测试、生产环境配置
6. **容器化部署**: 使用 Docker 简化部署流程