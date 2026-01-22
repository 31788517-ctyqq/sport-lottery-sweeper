# ✅ 周一5场比赛显示 - 快速修复

## 🎯 问题原因
后端API路由被旧代码覆盖，导致无法从500彩票网数据文件读取周一5场比赛。

## 🚀 立即解决（只需3步）

### 步骤1: 停止后端
打开任务管理器（Ctrl+Shift+Esc），找到并结束所有 `python.exe` 进程。

或者运行：
```powershell
taskkill /F /IM python.exe
```

### 步骤2: 启动后端
打开命令窗口，运行：
```bash
cd c:\Users\11581\Downloads\sport-lottery-sweeper
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**等待15秒让后端完全启动**，你会看到：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 步骤3: 测试并刷新前端

在浏览器打开：
```
http://localhost:8000/api/v1/jczq/matches?source=500
```

应该看到：
```json
{
  "success": true,
  "total": 5,
  "message": "成功获取5场比赛数据",
  "data": [
    {
      "match_id": "周一001",
      "league": "意甲",
      "home_team": "克雷莫纳",
      "away_team": "维罗纳",
      ...
    }
  ]
}
```

然后访问：
```
http://localhost:3005/#/jczq-schedule
```

**按 Ctrl+F5 强制刷新浏览器**

---

## 📊 你将看到

页面显示周一5场比赛：

```
⚽ 竞彩足球

📊 统计: 总场数:5 | 联赛数:5

🏆 比赛列表

[周一001] 意甲
克雷莫纳 VS 维罗纳
01-20 01:30

[周一002] 意甲
拉齐奥 VS 科莫
01-20 03:45

[周一003] 法乙
南锡 VS 甘冈
01-20 03:45

[周一004] 西甲
埃尔切 VS 塞维利亚
01-20 04:00

[周一005] 葡超
阿马多拉 VS 埃斯托里
01-20 04:15
```

---

## ⚠️ 如果还是不行

### 检查1: 确认数据文件存在
```bash
dir c:\Users\11581\Downloads\sport-lottery-sweeper\debug\500_com_matches_*.json
```

应该看到文件 `500_com_matches_20260119_011647.json`

### 检查2: 测试数据逻辑
```bash
cd c:\Users\11581\Downloads\sport-lottery-sweeper
python test_api_integration.py
```

应该显示"周一比赛数: 5"

### 检查3: 查看后端日志
在后端运行窗口查看是否有报错信息

---

## 💡 关键要点

1. ✅ 数据文件完整，包含周一5场比赛
2. ✅ 后端代码已修复，路径正确
3. ⚠️ **必须完全重启后端**（不要用--reload模式）
4. ⚠️ **必须强制刷新浏览器**（Ctrl+F5）

---

## 🎉 现在开始

1. 停止所有python进程
2. 运行 `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`
3. 等待15秒
4. 测试API返回数据
5. 访问前端并按Ctrl+F5刷新

**你就能看到周一5场比赛了！** ⚽🎊
