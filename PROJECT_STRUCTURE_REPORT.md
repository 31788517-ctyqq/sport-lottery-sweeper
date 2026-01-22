# Sport Lottery Sweeper 项目结构报告

## 项目概述

Sport Lottery Sweeper 是一个体育彩票数据抓取和管理系统，包含前后端分离的架构，支持数据采集、处理、存储和展示功能。

## 项目根目录结构

```
├── .codebuddy/              # 代码助手规则配置
├── .github/                 # GitHub配置文件
├── .naming-optimization/    # 命名优化相关配置
├── .pytest_cache/           # pytest缓存目录
├── .vscode/                 # VSCode配置
├── alembic/                 # 数据库迁移工具配置
├── backend/                 # 后端代码主目录
├── config/                  # 项目配置文件
├── crawler/                 # 爬虫模块（空目录）
├── data/                    # 数据文件
├── debug/                   # 调试相关文件
├── docker/                  # Docker配置文件
├── docs/                    # 文档文件
├── frontend/                # 前端代码
├── infrastructure/          # 基础设施配置
├── instance/                # 实例相关文件（空目录）
├── logs/                    # 日志文件
├── migrations/              # 数据库迁移文件
├── monitoring/              # 监控配置
├── node_modules/            # Node.js依赖包
├── scripts/                 # 各类脚本文件
├── src/                     # 源代码（含测试代码）
├── storage/                 # 存储相关文件
├── temp/                    # 临时文件
├── tests/                   # 测试文件
├── __pycache__/             # Python缓存文件
├── .dockerignore            # Docker忽略文件
├── .env                     # 环境变量配置
├── .env.example             # 环境变量配置示例
├── .env.local               # 本地环境变量配置
├── .env.production          # 生产环境变量配置
├── .gitignore               # Git忽略文件配置
├── alembic.ini              # Alembic数据库迁移配置
├── ARCHIVING_COMPLETION_REPORT.md    # 归档完成报告
├── backend.env              # 后端环境配置
├── crawler.env              # 爬虫环境配置
├── docker-compose.dev.yml   # 开发环境Docker Compose配置
├── docker-compose.override.yml        # Docker Compose覆盖配置
├── docker-compose.prod.yml  # 生产环境Docker Compose配置
├── docker-compose.production.yml      # 生产环境Docker Compose配置
├── docker-compose.yml       # Docker Compose配置
├── Dockerfile               # Docker镜像构建文件
├── Dockerfile.crawler       # 爬虫环境Docker构建文件
├── Dockerfile.dev           # 开发环境Docker构建文件
├── Dockerfile.production    # 生产环境Docker构建文件
├── env.development          # 开发环境配置
├── env.example              # 环境配置示例
├── frontend.env             # 前端环境配置
├── LICENSE                  # 许可证文件
├── Makefile                 # Make构建脚本
├── package-lock.json        # Node.js依赖锁定文件
├── package.json             # Node.js项目配置
├── pnpm-lock.yaml           # pnpm依赖锁定文件
├── poetry.lock              # Poetry依赖锁定文件
├── pyproject.toml           # Python项目配置文件
├── README.md                # 项目说明文档
├── requirements-crawler.txt # 爬虫模块Python依赖
├── requirements-dev-utf8.txt # 开发环境Python依赖（UTF-8编码）
├── requirements-dev.txt     # 开发环境Python依赖
├── requirements-windows.txt # Windows环境Python依赖
├── requirements.txt         # 生产环境Python依赖
├── ROOT_DIRECTORY_ANALYSIS_AND_ARCHIVING_PLAN.md  # 根目录分析和归档规划
├── start-frontend-powershell.ps1     # PowerShell启动前端脚本
├── start_project.ps1        # PowerShell启动项目脚本
├── test_sp_api_connectivity.js        # API连接测试脚本
└── 平局.docx                # 项目相关文档
```

## 后端结构 (backend/)

```
├── admin/                   # 管理后台相关代码
│   ├── __init__.py
│   ├── admin_dashboard.py   # 管理面板
│   ├── user_management.py   # 用户管理
│   └── routes.py            # 管理后台路由
├── alembic/                 # Alembic数据库迁移配置
│   ├── env.py
│   └── script.py.mako
├── api/                     # API接口定义
│   ├── __init__.py
│   ├── deps.py              # 依赖注入
│   ├── v1/                  # API v1版本
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证接口
│   │   ├── intelligence.py  # 情报接口
│   │   ├── matches.py       # 比赛接口
│   │   ├── odds.py          # 赔率接口
│   │   ├── predictions.py   # 预测接口
│   │   ├── users.py         # 用户接口
│   │   └── admin_user_management.py # 管理用户接口
│   └── v2/                  # API v2版本（预留）
├── app/                     # 应用主模块
│   ├── __init__.py
│   ├── database.py          # 数据库连接配置
│   ├── main.py              # 应用主入口
│   └── middleware.py        # 中间件定义
├── architecture/            # 架构相关文件
│   └── README.md
├── auth/                    # 认证模块
│   ├── __init__.py
│   └── security.py          # 安全认证相关
├── core/                    # 核心配置
│   ├── __init__.py
│   ├── config.py            # 配置文件
│   ├── constants.py         # 常量定义
│   ├── exceptions.py        # 异常定义
│   ├── logging_config.py    # 日志配置
│   ├── security.py          # 安全配置
│   ├── settings.py          # 设置定义
│   └── utils.py             # 工具函数
├── crud/                    # 数据库操作
│   ├── __init__.py
│   ├── base.py              # 基础CRUD操作
│   ├── intelligence_crud.py # 情报CRUD操作
│   ├── match_crud.py        # 比赛CRUD操作
│   ├── odds_crud.py         # 赔率CRUD操作
│   ├── prediction_crud.py   # 预测CRUD操作
│   ├── user_crud.py         # 用户CRUD操作
│   └── admin_user_crud.py   # 管理用户CRUD操作
├── debug/                   # 调试相关文件
│   ├── __init__.py
│   ├── debug_api.py         # 调试API
│   ├── debug_db.py          # 数据库调试
│   ├── debug_match.py       # 比赛数据调试
│   ├── debug_scheduler.py   # 调度器调试
│   └── debug_utils.py       # 调试工具
├── lembic/                  # 另一个数据库迁移配置
│   ├── env.py
│   └── script.py.mako
├── logs/                    # 日志文件
│   └── app.log
├── models/                  # 数据模型定义
│   ├── __init__.py
│   ├── base.py              # 基础模型
│   ├── intelligence.py      # 情报模型
│   ├── league.py            # 联赛模型
│   ├── match.py             # 比赛模型
│   ├── odds.py              # 赔率模型
│   ├── prediction.py        # 预测模型
│   ├── team.py              # 球队模型
│   ├── user.py              # 用户模型
│   └── admin_user.py        # 管理用户模型
├── monitoring/              # 监控相关
│   └── health_check.py      # 健康检查
├── processors/              # 数据处理器
│   ├── __init__.py
│   └── data_processor.py    # 数据处理逻辑
├── schemas/                 # 数据模式定义
│   ├── __init__.py
│   ├── intelligence.py      # 情报数据模式
│   ├── league.py            # 联赛数据模式
│   ├── match.py             # 比赛数据模式
│   ├── odds.py              # 赔率数据模式
│   ├── prediction.py        # 预测数据模式
│   ├── team.py              # 球队数据模式
│   ├── user.py              # 用户数据模式
│   └── admin_user.py        # 管理用户数据模式
├── scrapers/                # 爬虫相关
│   ├── __init__.py
│   ├── base_scraper.py      # 基础爬虫
│   ├── bet365_scraper.py    # 365赔率爬虫
│   ├── five_hundred_scraper.py # 500彩票网爬虫
│   ├── match_scraper.py     # 比赛爬虫
│   ├── odds_scraper.py      # 赔率爬虫
│   ├── schedule_scraper.py  # 赛程爬虫
│   ├── sports_reference_scraper.py # 体育参考爬虫
│   ├── sporttery_scraper.py # 体彩爬虫
│   ├── today_match_scraper.py # 今日比赛爬虫
│   ├── zqszsc_scraper.py    # 中超爬虫
│   └── scraper_factory.py   # 爬虫工厂
├── scripts/                 # 后端脚本
│   ├── __init__.py
│   ├── create_admin.py      # 创建管理员脚本
│   ├── create_superuser.py  # 创建超级用户脚本
│   ├── db_backup.py         # 数据库备份脚本
│   ├── db_restore.py        # 数据库恢复脚本
│   ├── init_db.py           # 初始化数据库脚本
│   ├── run_server.py        # 运行服务器脚本
│   └── seed_data.py         # 种子数据脚本
└── services/                # 业务服务层
    ├── __init__.py
    ├── auth_service.py      # 认证服务
    ├── intelligence_service.py # 情报服务
    ├── match_service.py     # 比赛服务
    ├── odds_service.py      # 赔率服务
    ├── prediction_service.py # 预测服务
    ├── user_service.py      # 用户服务
    └── admin_user_service.py # 管理用户服务
```

## 前端结构 (frontend/)

```
├── public/                  # 静态资源
├── src/                     # 源代码
│   ├── assets/              # 资源文件
│   ├── components/          # 组件
│   ├── views/               # 页面视图
│   ├── router/              # 路由配置
│   ├── stores/              # 状态管理 (Pinia)
│   ├── api/                 # API接口
│   ├── utils/               # 工具函数
│   ├── styles/              # 样式文件
│   └── App.vue              # 应用主组件
│   └── main.js              # 应用入口
├── package.json             # 项目配置
├── vite.config.js           # Vite构建配置
└── index.html               # 主页面
```

## 测试结构 (tests/)

```
├── backend/                 # 后端测试
│   ├── unit/                # 单元测试
│   ├── integration/         # 集成测试
│   └── e2e/               # 端到端测试
├── unit/                    # 单元测试
│   ├── models/              # 模型单元测试
│   ├── api/                 # API单元测试
│   ├── services/            # 服务单元测试
│   └── schemas/             # 模式单元测试
├── integration/             # 集成测试
│   ├── database/            # 数据库集成测试
│   ├── api/                 # API集成测试
│   └── services/            # 服务集成测试
├── e2e/                    # 端到端测试
│   ├── api/                 # API端到端测试
│   └── scenarios/           # 业务场景测试
└── functional/             # 功能测试
    └── 各类功能测试脚本
```

## 文档结构 (docs/)

```
├── api/                     # API文档
├── crawler/                 # 爬虫文档
├── frontend/                # 前端文档
├── backend/                 # 后端文档
├── troubleshooting/         # 故障排除文档
└── reports/                 # 各类报告
```

## 脚本结构 (scripts/)

```
├── admin/                   # 管理相关脚本
├── batch/                   # 批处理脚本
├── crawler/                 # 爬虫相关脚本
├── db/                      # 数据库相关脚本
├── fixes/                   # 修复脚本
├── utils/                   # 通用工具脚本
├── dev/                     # 开发相关脚本
├── docker/                  # Docker相关脚本
└── health_check/            # 健康检查脚本
```

## 数据结构 (data/)

```
├── backups/                 # 数据库备份
└── samples/                 # 示例数据
```

## 配置文件说明

- `.env` - 主环境变量配置
- `requirements.txt` - Python生产依赖
- `requirements-dev.txt` - Python开发依赖
- `package.json` - Node.js项目配置
- `Dockerfile` - Docker镜像构建配置
- `docker-compose.yml` - Docker Compose编排配置
- `alembic.ini` - 数据库迁移配置
- `pyproject.toml` - Python项目配置

## 项目特点

1. **前后端分离架构** - 使用FastAPI作为后端API，Vue.js作为前端框架
2. **数据驱动** - 包含多个爬虫模块用于数据采集
3. **多层测试** - 涵盖单元测试、集成测试、端到端测试
4. **容器化部署** - 支持Docker和Docker Compose部署
5. **数据库迁移** - 使用Alembic进行数据库版本管理
6. **模块化设计** - 代码结构清晰，职责分离
7. **配置管理** - 支持多环境配置管理