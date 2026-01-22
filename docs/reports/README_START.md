# 🚀 快速启动指南

## ❌ 当前问题
页面无法显示的原因：**前端依赖未安装**

前端需要先安装 npm 依赖才能启动。

---

## ✅ 完整解决方案

### 第一次运行（需要安装依赖）

**双击运行：**
```
INSTALL_AND_START.bat
```

这个脚本会：
1. ✅ 安装前端依赖（需要2-5分钟）
2. ✅ 启动后端服务器（8000端口）
3. ✅ 启动前端服务器（5173端口）

### 以后每次运行（依赖已安装）

**双击运行：**
```
SIMPLE_START.bat
```

---

## 📋 详细步骤

### 步骤1: 安装并启动（第一次）

1. **双击运行** `INSTALL_AND_START.bat`
2. **等待安装完成**（2-5分钟，会自动安装所有依赖）
3. **等待30秒**让服务器完全启动
4. **打开浏览器**访问：`http://localhost:5173/#/jczq-schedule`

### 步骤2: 验证是否成功

打开浏览器，依次访问：

| URL | 说明 | 预期结果 |
|-----|------|----------|
| `http://localhost:8000/docs` | 后端API文档 | ✅ 显示Swagger文档 |
| `http://localhost:8000/api/v1/jczq/matches?source=500` | API数据 | ✅ 返回5场比赛JSON |
| `http://localhost:5173` | 前端首页 | ✅ 页面加载 |
| `http://localhost:5173/#/jczq-schedule` | 赛程页面 | ✅ **显示周一5场比赛** |

---

## 🎯 你将看到的内容

成功后页面会显示：

```
⚽ 竞彩足球
近三天赛程数据 | 实时更新

📊 统计卡片
总场数: 5 | 联赛数: 5

🏆 比赛列表

[周一001] 意甲 🔥74
01-20 01:30
克雷莫纳 VS 维罗纳
主胜:2.32 平:2.32 客胜:2.32

[周一002] 意甲 🔥74
01-20 03:45
拉齐奥 VS 科莫
主胜:2.44 平:2.44 客胜:2.44

[周一003] 法乙 🔥70
01-20 03:45
南锡 VS 甘冈

[周一004] 西甲 🔥78
01-20 04:00
埃尔切 VS 塞维利亚

[周一005] 葡超 🔥60
01-20 04:15
阿马多拉 VS 埃斯托里
```

---

## 🔧 常见问题

### Q1: 安装过程中出错？
**A:** 确保已安装 Node.js
- 下载地址：https://nodejs.org/
- 推荐版本：LTS (长期支持版)
- 安装后重启命令窗口

### Q2: Python相关错误？
**A:** 确保已安装 Python 和依赖
```bash
python --version
pip install -r requirements.txt
```

### Q3: 端口被占用？
**A:** 查找并关闭占用端口的进程
```bash
# 查看8000端口
netstat -ano | findstr :8000

# 查看5173端口
netstat -ano | findstr :5173

# 关闭进程（替换PID）
taskkill /F /PID <进程ID>
```

### Q4: 前端页面空白？
**A:** 按以下顺序检查：
1. 确认两个服务器窗口都在运行
2. 等待30秒让服务器完全启动
3. 按 `Ctrl + F5` 强制刷新浏览器
4. 按 `F12` 查看浏览器控制台错误

---

## 📊 安装进度说明

运行 `INSTALL_AND_START.bat` 时会看到：

```
[1/3] Installing frontend dependencies...
npm install
⠋ Installing packages... (this may take 2-5 minutes)

[2/3] Starting backend server...
INFO: Uvicorn running on http://0.0.0.0:8000

[3/3] Starting frontend server...
VITE ready in 1234 ms
➜ Local: http://localhost:5173/
```

---

## ✅ 成功标志

当看到以下内容时表示成功：

- ✅ 前端窗口显示：`Local: http://localhost:5173/`
- ✅ 后端窗口显示：`Uvicorn running on http://0.0.0.0:8000`
- ✅ 浏览器能访问：`http://localhost:5173/#/jczq-schedule`
- ✅ 页面显示：周一5场比赛数据

---

## 🎉 现在开始

**立即运行：**

1. 双击 `INSTALL_AND_START.bat`
2. 等待5分钟（首次安装）
3. 等待30秒（服务器启动）
4. 访问 `http://localhost:5173/#/jczq-schedule`

**享受你的竞彩足球数据吧！** ⚽🎉
