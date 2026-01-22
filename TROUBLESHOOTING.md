# 🔧 故障排查 - 页面无内容显示

## ❌ 问题：页面无内容显示

访问 `http://localhost:5173/#/jczq-schedule` 时页面空白或显示"暂无比赛数据"

---

## ✅ 已解决！原因分析

**根本原因**: 后端服务器未启动，前端无法获取数据

### 现在的状态
- ✅ **前端服务器**: 正在运行 (http://localhost:5173)
- ✅ **后端服务器**: 正在运行 (http://localhost:8000)

---

## 🎯 现在的操作步骤

### 1. 刷新浏览器页面
访问: `http://localhost:5173/#/jczq-schedule`

然后按 `Ctrl + F5` 或 `F5` 刷新页面

### 2. 验证数据显示
你应该看到周一5场比赛：
- 周一001 | 意甲 | 克雷莫纳 vs 维罗纳
- 周一002 | 意甲 | 拉齐奥 vs 科莫
- 周一003 | 法乙 | 南锡 vs 甘冈
- 周一004 | 西甲 | 埃尔切 vs 塞维利亚
- 周一005 | 葡超 | 阿马多拉 vs 埃斯托里

---

## 🔍 验证后端是否正常

### 方法1: 访问API文档
打开浏览器访问: `http://localhost:8000/docs`

应该看到 FastAPI 的 Swagger 文档界面

### 方法2: 直接测试API
访问: `http://localhost:8000/api/v1/jczq/matches?source=500`

应该返回JSON数据：
```json
{
  "success": true,
  "data": [...],
  "total": 5,
  "message": "成功获取5场比赛数据"
}
```

### 方法3: 检查健康状态
访问: `http://localhost:8000/health`

应该返回：
```json
{
  "status": "healthy",
  "timestamp": "..."
}
```

---

## 🐛 如果仍然无内容

### 检查1: 浏览器控制台
1. 按 `F12` 打开开发者工具
2. 切换到 **Console** 标签
3. 查看错误信息

**常见错误及解决方案**:

#### 错误1: `Failed to fetch` 或 `Network Error`
```
原因: 后端未响应
解决: 确认后端运行在 http://localhost:8000
```

#### 错误2: `CORS policy` 跨域错误
```
原因: 跨域配置问题
解决: 检查 backend/main.py 中的 CORS 配置
```

#### 错误3: `404 Not Found`
```
原因: API路径错误
解决: 确认访问 /api/v1/jczq/matches
```

### 检查2: 网络请求
1. 按 `F12` 打开开发者工具
2. 切换到 **Network** 标签
3. 刷新页面
4. 查找 `jczq/matches` 请求

**正常的请求**:
```
Request URL: http://localhost:8000/api/v1/jczq/matches?source=500&days=3&sort_by=date
Status: 200 OK
```

**如果状态码不是200**:
- `500 Internal Server Error` - 后端代码错误，查看后端日志
- `404 Not Found` - 路由配置错误
- `Failed` - 后端未启动或连接失败

### 检查3: 数据文件是否存在
```bash
# 检查数据文件
dir debug\500_com_matches_*.json
```

**如果文件不存在**，运行爬虫：
```bash
python crawl_500_com.py
```

---

## 🚀 完整重启流程

如果问题仍然存在，尝试完整重启：

### 步骤1: 停止所有服务
- 关闭所有终端窗口
- 或按 `Ctrl + C` 停止服务

### 步骤2: 检查数据文件
```bash
python crawl_500_com.py
```

### 步骤3: 启动后端
```bash
cd c:\Users\11581\Downloads\sport-lottery-sweeper
python -m uvicorn backend.main:app --port 8000 --reload
```

等待看到：
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete
```

### 步骤4: 启动前端
```bash
cd c:\Users\11581\Downloads\sport-lottery-sweeper\frontend
npm run dev
```

等待看到：
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

### 步骤5: 访问页面
```
http://localhost:5173/#/jczq-schedule
```

---

## 🎬 一键启动脚本

为了避免每次手动启动，使用这个脚本：

```bash
start_full_stack.bat
```

这个脚本会：
1. ✅ 检查数据文件（如无则运行爬虫）
2. ✅ 启动后端服务器
3. ✅ 启动前端服务器
4. ✅ 自动打开浏览器

---

## 📊 系统状态检查清单

使用这个清单确认系统正常：

- [ ] **后端运行**: 访问 `http://localhost:8000/docs` 可打开
- [ ] **API响应**: 访问 `http://localhost:8000/api/v1/jczq/matches?source=500` 返回数据
- [ ] **前端运行**: 访问 `http://localhost:5173/` 可打开
- [ ] **路由工作**: 访问 `http://localhost:5173/#/jczq-schedule` 显示页面
- [ ] **数据显示**: 页面显示5场周一比赛
- [ ] **交互正常**: 筛选、排序、刷新按钮可用

---

## 💡 常见问题解答

### Q1: 为什么需要同时启动前端和后端？
**A**: 
- **前端** (5173端口): 负责页面显示和用户交互
- **后端** (8000端口): 负责提供比赛数据API
- 两者缺一不可

### Q2: 数据从哪里来？
**A**: 
```
500彩票网 → 爬虫脚本 → JSON文件 → 后端API → 前端页面
```

### Q3: 如何更新数据？
**A**: 
运行爬虫脚本获取最新数据：
```bash
python crawl_500_com.py
```
然后刷新浏览器页面

### Q4: 页面显示"暂无比赛数据"怎么办？
**A**: 
检查以下几点：
1. 后端是否运行
2. 数据文件是否存在
3. API是否返回数据
4. 浏览器控制台是否有错误

### Q5: 端口被占用怎么办？
**A**: 
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# 结束进程
taskkill /PID <进程ID> /F
```

---

## 🎯 当前系统状态

### ✅ 正在运行的服务

1. **后端服务器**
   - 地址: http://localhost:8000
   - 状态: ✅ 运行中
   - API文档: http://localhost:8000/docs

2. **前端服务器**
   - 地址: http://localhost:5173
   - 状态: ✅ 运行中
   - 赛程页面: http://localhost:5173/#/jczq-schedule

### 📝 下一步操作

1. **刷新浏览器页面**: 按 `F5` 或 `Ctrl + F5`
2. **验证数据显示**: 应该看到5场周一比赛
3. **测试功能**: 尝试筛选、排序、刷新

---

## 🎉 解决方案总结

**问题**: 页面无内容显示
**原因**: 后端服务器未启动
**解决**: 已启动后端服务器

**现在两个服务器都在运行，请刷新浏览器页面查看数据！**

---

## 📞 仍有问题？

如果按照上述步骤操作后仍然无法显示数据：

1. 查看后端终端的日志输出
2. 查看浏览器控制台的错误信息
3. 检查数据文件: `debug/500_com_matches_*.json`
4. 运行诊断工具: `diagnose_frontend.bat`

参考文档：
- 📄 `FRONTEND_FIX.md` - 前端修复指南
- 📄 `API_INTEGRATION_GUIDE.md` - API集成文档
- 📄 `DEMO.md` - 完整演示指南
