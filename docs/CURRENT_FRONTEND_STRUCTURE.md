# Sport Lottery Sweeper - 前端目录结构

## 项目概述

Frontend 是竞彩足球扫盘系统的前端部分，使用 Vue.js 3 + Vite + TypeScript 构建，提供了用户界面和交互功能。

## 前端目录结构

```
frontend/
├── .env.development             # 开发环境配置
├── .env.production.txt          # 生产环境配置
├── Dockerfile.dev               # 开发环境 Docker 配置
├── OPTIMIZATION_README.md       # 前端优化说明文档
├── cypress.config.js            # Cypress 测试配置
├── eslint.config.js             # ESLint 代码规范配置
├── index.html                   # 主页面入口文件
├── index.scss                   # 全局样式文件
├── package.json                 # npm 项目配置文件
├── pnpm-lock.yaml               # pnpm 依赖锁定文件
├── postcss.config.js            # PostCSS 配置文件
├── prettier.config.js           # Prettier 代码格式化配置
├── tailwind.config.js           # Tailwind CSS 配置
├── vite.config.js               # Vite 构建配置
├── vitest.config.js             # Vitest 测试配置
├── public/                      # 公共静态资源目录
│   ├── favicon.ico              # 网站图标
│   ├── index.html               # 模板页面
│   ├── manifest.json            # 应用清单文件
│   └── robots.txt               # 搜索引擎爬虫协议
├── src/                         # 源代码目录
│   ├── App.vue                  # Vue 根组件
│   ├── main-app.js              # 主应用逻辑文件
│   ├── main.js                  # Vue 应用入口文件
│   ├── api/                     # API 接口封装目录
│   │   ├── admin.js             # 管理员 API
│   │   ├── auth.js              # 认证 API
│   │   ├── index.js             # API 入口
│   │   ├── intelligence.js      # 情报 API
│   │   ├── matches.js           # 比赛 API
│   │   ├── predictions.js      # 预测 API
│   │   └── user.js              # 用户 API
│   ├── assets/                  # 静态资源目录
│   │   ├── css/                 # 样式文件
│   │   ├── images/              # 图片资源
│   │   └── logo.svg             # Logo 图标
│   ├── components/              # Vue 组件目录
│   │   ├── AdminPanel.vue       # 管理面板组件
│   │   ├── ChatInterface.vue    # 聊天界面组件
│   │   ├── DataTable.vue        # 数据表格组件
│   │   ├── FilterPanel.vue      # 过滤面板组件
│   │   ├── Footer.vue           # 页脚组件
│   │   ├── Header.vue           # 页头组件
│   │   ├── MatchCard.vue        # 比赛卡片组件
│   │   ├── MatchList.vue        # 比赛列表组件
│   │   ├── NotificationPanel.vue # 通知面板组件
│   │   └── SearchBar.vue        # 搜索栏组件
│   ├── composables/             # Vue 组合式 API 函数
│   │   ├── useAuth.js           # 认证组合函数
│   │   ├── useDarkMode.js       # 深色模式组合函数
│   │   ├── useLocalStorage.js   # 本地存储组合函数
│   │   ├── useNotifications.js  # 通知组合函数
│   │   ├── useOnlineStatus.js   # 在线状态组合函数
│   │   ├── usePagination.js     # 分页组合函数
│   │   ├── useTheme.js          # 主题组合函数
│   │   ├── useWebSocket.js      # WebSocket 组合函数
│   │   └── useWindowSize.js     # 窗口尺寸组合函数
│   ├── directives/              # Vue 自定义指令
│   │   ├── focus.js             # 聚焦指令
│   │   ├── highlight.js         # 高亮指令
│   │   ├── longpress.js         # 长按指令
│   │   ├── permissions.js       # 权限指令
│   │   └── tooltip.js           # 提示框指令
│   ├── i18n/                    # 国际化配置目录
│   │   ├── en.json              # 英文翻译
│   │   ├── index.js             # 国际化入口
│   │   └── zh.json              # 中文翻译
│   ├── i18n.js                  # 国际化配置文件
│   ├── router/                  # 路由配置目录
│   │   ├── index.js             # 路由入口文件
│   │   ├── routes.js            # 路由定义文件
│   │   ├── guards.js            # 路由守卫文件
│   │   └── middleware.js        # 路由中间件
│   ├── stores/                  # Pinia 状态管理目录
│   │   └── admin.js             # 管理员状态管理
│   ├── styles/                  # 样式文件目录
│   │   ├── base.css             # 基础样式
│   │   ├── components.css       # 组件样式
│   │   ├── layout.css           # 布局样式
│   │   ├── utilities.css        # 工具样式
│   │   ├── dark-theme.css       # 深色主题样式
│   │   ├── light-theme.css      # 浅色主题样式
│   │   ├── animations.css       # 动画样式
│   │   ├── responsive.css       # 响应式样式
│   │   ├── typography.css       # 字体样式
│   │   └── variables.css        # CSS 变量定义
│   ├── tests/                   # 测试文件目录
│   │   ├── unit/                # 单元测试
│   │   ├── integration/         # 集成测试
│   │   └── e2e/                 # 端到端测试
│   ├── utils/                   # 工具函数目录
│   │   ├── auth.js              # 认证工具
│   │   ├── date.js              # 日期工具
│   │   ├── http.js              # HTTP 请求工具
│   │   ├── storage.js           # 存储工具
│   │   ├── validation.js        # 验证工具
│   │   ├── helpers.js           # 辅助函数
│   │   ├── constants.js         # 常量定义
│   │   ├── formatters.js        # 格式化工具
│   │   ├── validators.js        # 验证器
│   │   ├── crypto.js            # 加密工具
│   │   ├── filters.js           # 过滤器
│   │   ├── permissions.js       # 权限工具
│   │   ├── themes.js            # 主题工具
│   │   └── logger.js            # 日志工具
│   ├── views/                   # 视图组件目录
│   │   ├── AdminDashboard.vue   # 管理仪表盘视图
│   │   ├── Home.vue             # 首页视图
│   │   ├── Login.vue            # 登录视图
│   │   ├── Matches.vue          # 比赛视图
│   │   ├── NotFound.vue         # 404 视图
│   │   ├── Profile.vue          # 个人资料视图
│   │   ├── Register.vue         # 注册视图
│   │   ├── Settings.vue         # 设置视图
│   │   └── About.vue            # 关于页面视图
│   └── admin/                   # 管理后台模块目录
│       ├── AdminLayout.vue      # 管理布局组件
│       ├── AdminLogin.vue       # 管理登录组件
│       ├── components/          # 管理后台组件
│       │   ├── UserManagement.vue # 用户管理组件
│       │   ├── DataReview.vue   # 数据审核组件
│       │   ├── DataSourceConfig.vue # 数据源配置组件
│       │   ├── SystemMonitor.vue # 系统监控组件
│       │   ├── MatchManagement.vue # 比赛管理组件
│       │   ├── PredictionAnalysis.vue # 预测分析组件
│       │   ├── ApiManagement.vue # API 管理组件
│       │   ├── LogViewer.vue    # 日志查看器
│       │   ├── BackupRestore.vue # 备份恢复组件
│       │   └── PerformanceMetrics.vue # 性能指标组件
│       ├── pages/               # 管理后台页面
│       │   ├── Dashboard.vue    # 仪表盘页面
│       │   ├── Users.vue        # 用户管理页面
│       │   ├── Data.vue         # 数据管理页面
│       │   └── Settings.vue     # 设置页面
│       └── index.js             # 管理后台入口文件
├── utils/                       # 工具函数目录
│   ├── auth.js                  # 认证工具
│   └── request.js               # 请求工具
└── node_modules/                # npm 依赖包目录（已忽略）
```

## 主要功能模块

### 1. API 层 (src/api/)
封装与后端服务的通信逻辑，包括用户认证、比赛数据、预测分析等接口。

### 2. 组件层 (src/components/)
可复用的 UI 组件，如表单、按钮、对话框、数据表格等。

### 3. 状态管理 (src/stores/)
使用 Pinia 进行状态管理，统一管理应用状态。

### 4. 路由 (src/router/)
定义应用路由结构，实现页面导航。

### 5. 视图 (src/views/)
页面级组件，实现具体业务逻辑。

### 6. 工具函数 (src/utils/)
提供通用的工具函数，如日期处理、HTTP 请求、验证等。

### 7. 管理后台 (src/admin/)
专门的管理后台模块，提供数据审核、用户管理等功能。

## 技术栈

- **Vue.js 3**: 前端框架
- **Vite**: 构建工具
- **TypeScript**: 类型安全（部分使用）
- **Tailwind CSS**: CSS 框架
- **Pinia**: 状态管理
- **Vue Router**: 路由管理
- **Element Plus**: UI 组件库（可能已使用）

## 构建和运行

### 开发环境
```bash
# 安装依赖
pnpm install

# 启动开发服务器
pnpm run dev
```

### 生产环境
```bash
# 构建生产版本
pnpm run build

# 预览生产构建
pnpm run preview
```

## 配置文件说明

- **vite.config.js**: Vite 构建配置
- **tailwind.config.js**: Tailwind CSS 配置
- **eslint.config.js**: ESLint 代码规范配置
- **.env.development**: 开发环境变量配置
- **.env.production.txt**: 生产环境变量配置