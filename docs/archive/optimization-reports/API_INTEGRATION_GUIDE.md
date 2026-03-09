# 🎯 API集成完成指南

## ✅ 已完成的工作

### 1. 后端API端点 (`backend/api.py`)

新增了 **竞彩足球API接口**：

```
GET /api/v1/jczq/matches
```

**参数**:
- `days` (int): 天数范围，默认3天
- `league` (string): 联赛筛选（可选）
- `sort_by` (string): 排序方式 - `date`/`popularity`/`odds`
- `source` (string): 数据来源 - `500`（500彩票网）或 `sporttery`（竞彩官网）

**返回数据**:
```json
{
  "success": true,
  "data": [
    {
      "id": "周一001",
      "match_id": "周一001",
      "league": "意甲",
      "home_team": "克雷莫纳",
      "away_team": "维罗纳",
      "match_time": "01-20 01:30",
      "match_date": "2026-01-20T01:30:00",
      "odds_home_win": 2.50,
      "odds_draw": 2.32,
      "odds_away_win": 3.20,
      "status": "scheduled",
      "score": "-:-",
      "popularity": 74,
      "source": "500彩票网"
    }
  ],
  "total": 5,
  "message": "成功获取5场比赛数据",
  "source": "500",
  "timestamp": "2026-01-19T00:30:00"
}
```

**特性**:
- ✅ 自动读取最新的爬取数据文件
- ✅ 智能筛选周一比赛
- ✅ 数据格式标准化
- ✅ 自动计算比赛热度
- ✅ 支持按联赛/时间/热度排序

---

### 2. 前端API调用 (`frontend/src/api/jczq.js`)

新增了以下方法：

```javascript
// 获取竞彩足球比赛数据
getJczqMatches(params)

// 获取周一比赛
getMondayMatches()

// 获取模拟数据（开发测试用）
getMockData()
```

---

### 3. 前端页面更新 (`frontend/src/views/JczqSchedule.vue`)

**改进**:
- ✅ 优先从500彩票网API获取真实数据
- ✅ 失败时自动降级到模拟数据
- ✅ 显示周一的5场比赛
- ✅ 完整的比赛信息展示（时间、球队、赔率、热度等）
- ✅ 联赛筛选、排序功能

---

## 🚀 如何运行

### 方式1: 完整启动（推荐）

#### 步骤1: 启动后端服务器

```bash
# 方式A: 使用批处理文件
start_backend_test.bat

# 方式B: 手动启动
cd c:/Users/11581/Downloads/sport-lottery-sweeper
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

后端将运行在: `http://localhost:8000`

API文档: `http://localhost:8000/docs`

#### 步骤2: 启动前端

```bash
cd frontend
npm install  # 首次运行需要
npm run dev
```

前端将运行在: `http://localhost:5173` (或其他端口)

#### 步骤3: 访问竞彩足球页面

浏览器打开: `http://localhost:5173/#/jczq-schedule`

你将看到从500彩票网爬取的周一5场比赛！

---

### 方式2: 测试API端点

#### 测试1: 使用浏览器
直接访问:
```
http://localhost:8000/api/v1/jczq/matches?source=500&days=1
```

#### 测试2: 使用curl
```bash
curl "http://localhost:8000/api/v1/jczq/matches?source=500&days=1"
```

#### 测试3: 使用Postman
- Method: GET
- URL: `http://localhost:8000/api/v1/jczq/matches`
- Params:
  - source: 500
  - days: 1

---

## 📊 数据流程图

```
┌──────────────────┐
│  500彩票网爬虫  │
│ (crawl_500_com.py)│
└────────┬─────────┘
         │ 爬取数据
         ↓
┌────────────────────────────┐
│   保存JSON文件              │
│ debug/500_com_matches_*.json│
└────────┬───────────────────┘
         │ 读取
         ↓
┌────────────────────┐
│   后端API          │
│ GET /jczq/matches  │
│  - 读取文件        │
│  - 数据转换        │
│  - 计算热度        │
│  - 筛选排序        │
└────────┬───────────┘
         │ HTTP响应
         ↓
┌────────────────────┐
│   前端API调用      │
│ getJczqMatches()   │
└────────┬───────────┘
         │ Vue组件
         ↓
┌────────────────────┐
│   JczqSchedule.vue │
│  - 显示比赛列表    │
│  - 筛选器          │
│  - 排序功能        │
│  - 统计信息        │
└────────────────────┘
```

---

## 🎨 前端显示效果

页面将显示以下内容：

### 统计卡片
- 总场数: 5
- 联赛数: 5
- 平均赔率

### 比赛列表（每场比赛显示）
- 🏆 联赛名称（如：意甲、西甲等）
- ⏰ 比赛时间（如：01-20 03:45）
- ⚽ 主队 vs 客队
- 💰 三项赔率（主胜/平局/客胜）
- 🔥 热度值（0-100）
- 📊 比赛编号（如：周一001）

### 筛选功能
- 按联赛筛选
- 按时间排序
- 按热度排序
- 刷新数据按钮

---

## 📝 周一5场比赛数据

根据爬取的数据，周一的5场比赛是：

| 编号 | 联赛 | 比赛 | 时间 |
|------|------|------|------|
| 周一001 | 意甲 | 克雷莫纳 vs 维罗纳 | 01-20 01:30 |
| 周一002 | 意甲 | 拉齐奥 vs 科莫 | 01-20 03:45 |
| 周一003 | 法乙 | 南锡 vs 甘冈 | 01-20 03:45 |
| 周一004 | 西甲 | 埃尔切 vs 塞维利亚 | 01-20 04:00 |
| 周一005 | 葡超 | 阿马多拉 vs 埃斯托里 | 01-20 04:15 |

---

## 🔧 技术特点

### 后端
- ✅ FastAPI异步框架
- ✅ 自动文件读取
- ✅ 数据格式转换
- ✅ 智能热度计算
- ✅ 灵活的筛选和排序
- ✅ 完整的错误处理

### 前端
- ✅ Vue 3 Composition API
- ✅ 响应式数据绑定
- ✅ 优雅的加载和错误状态
- ✅ 美观的UI设计
- ✅ 移动端适配
- ✅ 自动降级机制

---

## 🐛 故障排除

### 问题1: 后端启动失败

**解决方案**:
```bash
# 检查Python版本
python --version  # 需要 >= 3.8

# 安装依赖
pip install -r requirements.txt

# 检查端口占用
netstat -ano | findstr :8000
```

### 问题2: 前端无法获取数据

**检查项**:
1. 后端是否正常运行？访问 `http://localhost:8000/docs`
2. API端点是否返回数据？访问 `http://localhost:8000/api/v1/jczq/matches?source=500`
3. 浏览器控制台是否有CORS错误？
4. 网络请求是否被拦截？

**解决方案**:
```javascript
// 检查前端API配置
// frontend/.env.development
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 问题3: 数据文件不存在

**解决方案**:
```bash
# 重新运行爬虫
python crawl_500_com.py

# 检查文件是否生成
dir debug\500_com_matches_*.json
```

---

## 🎯 下一步优化建议

1. **定时任务**: 定时自动爬取最新数据
2. **数据库存储**: 将数据存入PostgreSQL/MySQL
3. **缓存机制**: 使用Redis缓存热点数据
4. **实时更新**: WebSocket推送比赛实时数据
5. **数据分析**: 添加历史数据分析和预测功能

---

## 📞 联系方式

如有问题，请查看：
- API文档: `http://localhost:8000/docs`
- 项目文档: `README.md`
- 测试报告: `FINAL_TEST_REPORT.md`

---

**🎉 恭喜！API集成已完成，现在可以在前端看到周一的5场比赛了！**
