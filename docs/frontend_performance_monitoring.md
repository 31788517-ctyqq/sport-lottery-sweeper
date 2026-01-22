# 前端性能监测与优化启动

本文档介绍如何使用优化的前端启动脚本，并包含详细的时间监测功能。

## 启动脚本概述

我们提供了三种平台特定的前端性能监测启动脚本：

1. **JavaScript脚本** (`scripts/frontend_perf_launch.js`) - 跨平台Node.js脚本
2. **批处理脚本** (`scripts/launch_frontend_perf.bat`) - Windows CMD脚本
3. **PowerShell脚本** (`scripts/launch_frontend_perf.ps1`) - Windows PowerShell脚本

## 使用方法

### JavaScript脚本（跨平台）

```bash
# 使用Node.js运行
node scripts/frontend_perf_launch.js
```

### Windows批处理脚本

```cmd
# 在CMD中运行
scripts\launch_frontend_perf.bat
```

### PowerShell脚本

```powershell
# 在PowerShell中运行
.\scripts\launch_frontend_perf.ps1
```

## 性能监测功能

### 1. 环境检查
- 检测Node.js版本（要求>=18.0.0）
- 检测包管理器（pnpm > yarn > npm）
- 验证必要的依赖

### 2. 时间监测
- **启动时间**: 记录从前端启动命令发出到服务器准备就绪的时间
- **总运行时间**: 记录从脚本执行到服务器停止的总时间
- **开发服务器启动时间**: 记录Vite开发服务器启动所需时间

### 3. 优化特性
- 自动检测可用的包管理器
- 智能错误处理和提示
- 清晰的进度指示器
- 详细的性能统计

## 性能优化措施

### 1. Vite配置优化
- 预构建常用依赖
- 代码分割策略
- 压缩插件启用
- 智能缓存配置

### 2. 启动优化
- 延迟加载非关键资源
- 优化依赖解析
- 并行处理任务

### 3. 监测指标
- 模块加载时间
- 依赖解析时间
- 热更新时间
- 构建时间

## 故障排除

### 常见问题

1. **Node.js版本过低**
   ```
   ❌ 检测到 Node.js 版本 v16.x，建议使用 Node.js 18 或更高版本
   ```
   **解决方案**: 升级到Node.js 18或更高版本

2. **包管理器未找到**
   ```
   ✅ 包管理器: npm (pnpm/yarn 未安装，使用 npm)
   ```
   **解决方案**: 安装pnpm或yarn以获得更好的性能

3. **端口被占用**
   ```
   error: Port 3000 is already in use
   ```
   **解决方案**: 终止占用端口的进程或修改vite.config.js中的端口号

### 性能调优建议

1. 使用pnpm包管理器以获得最快的依赖安装速度
2. 确保有足够的内存和CPU资源
3. 使用SSD存储以加快文件读写
4. 定期清理node_modules和重新安装依赖

## 预期性能指标

- **首次启动时间**: 10-30秒（取决于机器性能和依赖缓存）
- **增量更新时间**: < 1秒
- **热更新时间**: < 500毫秒
- **构建时间**: 1-3分钟（完整构建）

## 集成后端服务

前端开发服务器配置了自动代理到后端API：

- `/api` → `http://localhost:8000/api`（可由`.env`文件配置）
- `/ws` → `ws://localhost:8000/ws`（WebSocket连接）

确保后端服务正在运行，以便前端能够正确获取数据。

## 自定义配置

您可以通过修改`frontend/.env`文件来自定义前端开发服务器的行为：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_PORT=3000
VITE_OPEN_BROWSER=true
```