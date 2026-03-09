# 清理后的前端目录结构说明

## 已删除的不必要文件和目录

### 文件
- `.env.txt` - 冗余的环境配置文件
- `.eslintignore.txt` - 非标准的ESLint忽略配置文件
- `1` - 无意义的文件名
- `index-optimized.html` - 与index.html重复的页面文件
- `demo.html` - 演示页面（非必需）
- `preview.html` - 预览页面（非必需）
- `simple-index.html` - 与index.html重复的页面文件
- `jczq_schedule.html` - 与Vue路由功能重复的页面文件
- `tsconfig.json` - 空的TypeScript配置文件

### 目录
- `frontend/node_modules/` - 依赖包目录（通过package.json安装）
- `frontend/src/store/` - 使用Vuex的状态管理目录（项目同时存在Vuex和Pinia，已统一为Pinia）
- `frontend/src/router-1/` - 废弃的路由配置目录

## 保留的必要文件和目录

### 项目配置文件
- `.env.development` - 开发环境配置
- `.env.production.txt` - 生产环境配置
- `Dockerfile.dev` - Docker开发环境配置
- `OPTIMIZATION_README.md` - 优化说明文档
- `package.json` - 项目依赖和脚本配置
- `vite.config.js` - Vite构建工具配置
- `index.html` - 项目主入口HTML文件

### 源代码目录结构
- `src/admin/` - 管理后台相关组件
- `src/api/` - API接口封装
- `src/components/` - 可复用UI组件
- `src/views/` - 页面视图组件
- `src/router/` - 路由配置
- `src/stores/` - Pinia状态管理（已统一为单一状态管理方案）
- `src/utils/` - 工具函数
- `src/assets/` - 静态资源
- `src/styles/` - 样式文件
- `src/composables/` - Vue组合式API函数
- `src/directives/` - Vue自定义指令
- `src/i18n/` - 国际化配置

### 已统一的状态管理方案
项目原有两个状态管理目录(store/和stores/)，现已统一为Pinia方案(stores/)，符合"在Vue项目中必须统一状态管理方案，禁止同时配置Vuex和Pinia"的规范。

## 项目改进
1. 清理了冗余文件，使项目结构更简洁
2. 统一了状态管理方案，使用现代Vue推荐的Pinia
3. 保留了所有必要的功能模块和配置文件