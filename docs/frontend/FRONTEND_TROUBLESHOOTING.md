# 🔧 前端页面无法显示 - 完整解决方案

## ❌ 问题
`http://localhost:5173/#/jczq-schedule` 页面无法显示

## ✅ 原因
前后端服务器都没有运行！

---

## 🚀 立即解决（推荐）

### 方式1: 一键启动（最简单）
**双击运行这个文件:**
```
start_all_services.bat
```

这会自动打开两个命令窗口：
- 窗口1: 后端服务器 (端口 8000)
- 窗口2: 前端服务器 (端口 5173)

### 方式2: 手动启动

**步骤1: 启动后端**
```bash
# 打开第一个命令窗口
cd c:\Users\11581\Downloads\sport-lottery-sweeper
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**步骤2: 启动前端**
```bash
# 打开第二个命令窗口
cd c:\Users\11581\Downloads\sport-lottery-sweeper\frontend
npm run dev
```

---

## ⏱️ 等待时间

启动后需要等待：
- **后端**: 10-30秒完全启动
- **前端**: 5-10秒完全启动

**建议总等待时间: 30秒**

---

## 🔍 验证服务器状态

### ✅ 检查后端
在浏览器访问：
```
http://localhost:8000/docs
```
应该看到 FastAPI 文档界面

### ✅ 检查前端
在浏览器访问：
```
http://localhost:5173
```
应该能打开页面（即使是空白也说明服务器在运行）

### ✅ 检查API数据
在浏览器访问：
```
http://localhost:8000/api/v1/jczq/matches?source=500
```
应该返回JSON数据，包含周一5场比赛

---

## 🎯 最终访问

当两个服务器都启动后，访问：
```
http://localhost:5173/#/jczq-schedule
```

你将看到：
- ⚽ 竞彩足球标题
- 📊 统计卡片
- 🏆 周一5场比赛列表
  - 周一001 | 意甲 | 克雷莫纳 vs 维罗纳 (01-20 01:30)
  - 周一002 | 意甲 | 拉齐奥 vs 科莫 (01-20 03:45)
  - 周一003 | 法乙 | 南锡 vs 甘冈 (01-20 03:45)
  - 周一004 | 西甲 | 埃尔切 vs 塞维利亚 (01-20 04:00)
  - 周一005 | 葡超 | 阿马多拉 vs 埃斯托里 (01-20 04:15)

---

## 🛠️ 常见问题

### Q1: 启动后页面还是空白？
**A:** 
1. 等待30秒
2. 按 `Ctrl + F5` 强制刷新浏览器
3. 按 `F12` 打开控制台查看错误

### Q2: 后端启动失败？
**A:** 
```bash
# 检查Python环境
python --version

# 安装依赖
pip install -r requirements.txt

# 重新启动
python -m uvicorn backend.main:app --port 8000 --reload
```

### Q3: 前端启动失败？
**A:** 
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 重新启动
npm run dev
```

### Q4: 端口被占用？
**A:** 
```bash
# 查看占用8000端口的进程
netstat -ano | findstr :8000

# 查看占用5173端口的进程
netstat -ano | findstr :5173

# 杀死进程（替换PID）
taskkill /F /PID <进程ID>
```

---

## 📊 完整启动流程图

```
开始
  ↓
双击 start_all_services.bat
  ↓
后端窗口打开 (端口 8000)
  ↓
前端窗口打开 (端口 5173)
  ↓
等待 30 秒
  ↓
访问 http://localhost:5173/#/jczq-schedule
  ↓
✅ 看到周一5场比赛！
```

---

## 💡 调试技巧

### 查看后端日志
在后端命令窗口中会显示：
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 查看前端日志
在前端命令窗口中会显示：
```
VITE v4.x.x ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 浏览器控制台
1. 按 `F12` 打开开发者工具
2. 切换到 **Console** 标签
3. 查看是否有红色错误信息
4. 切换到 **Network** 标签
5. 刷新页面，查看API请求是否成功

---

## 🎉 成功标志

当一切正常时，你会看到：

✅ 后端命令窗口显示 "Uvicorn running"
✅ 前端命令窗口显示 "Local: http://localhost:5173/"
✅ 浏览器能访问 http://localhost:8000/docs
✅ 浏览器能访问 http://localhost:5173
✅ API返回数据: http://localhost:8000/api/v1/jczq/matches?source=500
✅ 页面显示5场比赛: http://localhost:5173/#/jczq-schedule

---

## 🔄 现在开始

1. **双击运行**: `start_all_services.bat`
2. **等待30秒**: 让服务器完全启动
3. **打开浏览器**: 访问 `http://localhost:5173/#/jczq-schedule`
4. **查看数据**: 应该显示周一5场比赛

**就这么简单！** 🚀
