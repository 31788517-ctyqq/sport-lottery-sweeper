# AI_WORKING: coder1 @1769627946 - 创建端口冲突解决方案

# 端口冲突

## 症状描述
- 后端启动失败，错误信息：`[Errno 10048] 通常每个套接字地址(协议/网络地址/端口)只允许使用一次`
- 前端启动失败，端口已被占用
- 访问 `http://localhost:8000/docs` 无法打开
- 服务启动后立即退出

## 根本原因
多个服务尝试绑定到同一端口，或之前运行的进程未完全退出。

## 解决方案

### 1. 查找占用端口的进程
```bash
# 查找占用 8000 端口的进程（后端端口）
netstat -ano | findstr :8000

# 查找占用 5173 端口的进程（前端开发服务器）
netstat -ano | findstr :5173

# 查找占用 3000 端口的进程（前端备用端口）
netstat -ano | findstr :3000
```

### 2. 结束占用进程
```bash
# 根据 netstat 输出的 PID 结束进程
taskkill /F /PID <进程ID>

# 示例：结束 PID 为 12345 的进程
taskkill /F /PID 12345
```

### 3. 如果无法结束进程
```bash
# 使用 PowerShell 结束进程
powershell -Command "Stop-Process -Id <进程ID> -Force"

# 查找进程详情
tasklist | findstr <进程ID>

# 如果进程是 Python，结束所有 Python 进程
taskkill /F /IM python.exe
```

### 4. 更换端口（临时方案）
**后端更换端口**：
```bash
# 启动在 8001 端口
python -m uvicorn backend.main:app --port 8001 --reload
```

**前端更换端口**：
```bash
cd frontend
npm run dev -- --port 5174
```

### 5. 验证端口可用性
```bash
# 检查端口是否已释放
netstat -ano | findstr :8000

# 如果没有输出，表示端口可用
```

## 标准端口配置
| 服务 | 端口 | 说明 |
|------|------|------|
| 后端 API | 8000 | FastAPI 服务默认端口 |
| 前端开发服务器 | 5173 | Vite 默认端口 |
| 前端备用端口 | 3000 | 备用开发端口 |
| 数据库（SQLite）| - | 文件形式，无端口 |

## 预防措施
- 服务停止时使用 `Ctrl + C` 正确终止
- 编写启动脚本确保先检查端口占用
- 在 Docker 环境中使用固定端口映射
- 开发环境与生产环境使用不同端口

## 相关文档
- [端口配置规范](../PROJECT_STANDARDS.md#端口配置)
- [后端启动诊断](../../docs/backend/BACKEND_NOT_STARTING.md)
- [前端故障排查](../../docs/frontend/FRONTEND_TROUBLESHOOTING.md)

# AI_DONE: coder1 @1769627946