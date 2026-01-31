# 体育彩票扫盘系统 - 启动指南

> **AI协同开发必读** | 版本: 1.0.0 | 更新时间: 2026-01-25

## 🚀 项目入口概览

### 后端入口
- **主文件**: `backend/main.py`
- **启动端口**: 8000
- **API文档**: http://localhost:8000/docs
- **启动命令**: 
  ```bash
  python backend/main.py
  # 或使用脚本
  start_backend.bat
  ```

### 前端入口
- **开发服务器**: 端口3000
- **API代理**: 自动转发到后端8000端口
- **启动命令**:
  ```bash
  cd frontend && npm run dev
  # 或使用脚本
  start-frontend.bat
  ```

## 📋 快速启动流程

### 一键启动（推荐）
```bash
# Windows
start-dev.ps1

# 或使用npm脚本
npm run dev
```

### 手动启动
1. **启动后端** (端口8000)
   ```bash
   cd backend
   python main.py
   ```

2. **启动前端** (端口3000)
   ```bash
   cd frontend
   npm run dev
   ```

3. **验证服务**
   - 后端健康检查: http://localhost:8000/health/live
   - API文档: http://localhost:8000/docs
   - 前端首页: http://localhost:3000

## 🔧 环境配置

### 必需环境变量
- **后端**: `backend/.env` (DATABASE_URL, SECRET_KEY, DEBUG, PORT=8000)
- **前端**: `frontend/.env` (VITE_API_BASE_URL=http://localhost:8000)

### 端口规范
- 前端开发服务器: **3000**
- 前端API接收端口: **8000**
- 后端服务端口: **8000**

## 🤖 AI开发协同

### 文件修改前必检
```bash
# 检查文件锁状态
python .codebuddy/locks/check_lock.py check 文件名 AI标识

# 创建文件锁
python .codebuddy/locks/check_lock.py create 文件名 AI标识
```

### 代码注释规范
```python
# AI_WORKING: [AI标识] @[时间戳] - 具体修改说明
# [修改的代码]
# AI_DONE: [AI标识] @[时间戳]
```

### 多AI协作协议
- **coder1**: 主要代码编写AI
- **coder2**: 辅助代码编写AI  
- **tester1**: 测试AI
- **reviewer1**: 代码审查AI
- **analyzer1**: 分析AI

## 📊 服务状态检查

### 健康检查命令
```bash
# 检查所有服务状态
python scripts/project_health_check.py

# 检查AI协同状态
python scripts/check_ai_compliance.py

# 扫描项目配置
python scripts/config_scanner.py
```

### 端口检查
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 或使用清理脚本
force_kill_port_8000.bat
```

## 🆘 故障排除

### 常见问题
1. **端口占用**: 运行 `force_kill_port_8000.bat`
2. **API 404**: 检查后端路由注册和前端代理配置
3. **文件锁冲突**: 检查 `.codebuddy/locks/` 目录
4. **编码错误**: 确保所有.py和.js文件使用UTF-8编码

### 紧急恢复
```bash
# 重启所有服务
restart_all.bat

# 或手动重启
kill_port_8000.bat
start_backend.bat
start-frontend.bat
```

---
**记住**: 本指南是所有AI和开发者协同工作的基础，请严格遵守！