# 竞彩足球扫盘系统 - 运行指南

## 项目启动说明

### 后端服务启动

1. 打开命令行窗口，进入项目根目录：
```bash
cd c:\Users\11581\Downloads\sport-lottery-sweeper
```

2. 启动后端服务（使用端口8001）：
```bash
python -c "from src.backend.optimized_main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8001, log_level='info')"
```

### 前端服务启动

1. 打开另一个命令行窗口，进入前端目录：
```bash
cd c:\Users\11581\Downloads\sport-lottery-sweeper\frontend
```

2. 确保已安装依赖：
```bash
npm install
```

3. 启动前端开发服务器：
```bash
npm run dev
```

## 访问地址

- **后端 API**: http://127.0.0.1:8001
- **后端文档**: http://127.0.0.1:8001/docs
- **前端界面**: http://127.0.0.1:3000
- **前端竞彩页面**: http://127.0.0.1:3000/jczq

## 端口冲突处理

如果遇到端口被占用的问题，可以使用以下命令查找并终止占用端口的进程：

```bash
# 查看占用8000端口的进程
netstat -ano | findstr :8000

# 终止指定PID的进程（替换<PROCESS_ID>为实际的PID）
taskkill /f /pid <PROCESS_ID>
```

## 环境要求

- Python 3.8+
- Node.js 18+
- npm 或 pnpm

## 故障排除

1. **后端启动失败**: 检查端口是否被占用，确保Python环境已正确配置
2. **前端启动失败**: 确认Node.js版本，检查依赖是否正确安装
3. **API调用失败**: 确认后端服务正常运行，检查前端代理配置