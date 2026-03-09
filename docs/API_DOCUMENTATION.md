# 竞彩足球API完整文档

## 📋 概述

本文档描述竞彩足球数据API的所有端点、参数和响应格式。API基于FastAPI构建，支持缓存、实时过滤和排序。

---

## 🔌 API基础信息

**基础URL**: `http://localhost:8000/api/jczq` (本地) 或 `https://api.example.com/api/jczq` (生产)

**认证**: 暂无（可选配置）

**响应格式**: JSON

**默认编码**: UTF-8

---

## 📊 API端点

### 1. 获取近期比赛赛程

**端点**: `GET /matches/recent`

**描述**: 获取未来N天内的比赛赛程数据

**请求参数**:

| 参数 | 类型 | 必需 | 默认值 | 范围 | 说明 |
|------|------|------|--------|------|------|
| `days` | integer | 否 | 3 | 1-7 | 未来N天内的比赛 |
| `league` | string | 否 | 无 | - | 联赛过滤（如：英超、西甲等） |
| `sort_by` | string | 否 | date | date/popularity/odds | 排序方式 |

**请求示例**:

```bash
# 获取近3天比赛
curl "http://localhost:8000/api/jczq/matches/recent?days=3"

# 获取英超比赛，按热度排序
curl "http://localhost:8000/api/jczq/matches/recent?league=英超&sort_by=popularity"

# 获取近7天比赛，按赔率排序
curl "http://localhost:8000/api/jczq/matches/recent?days=7&sort_by=odds"
```

**响应示例**:

```json
{
  "status": "success",
  "count": 15,
  "days": 3,
  "league_filter": null,
  "sort_by": "date",
  "matches": [
    {
      "id": "mock_001",
      "match_id": "mock_001",
      "home_team": "曼城",
      "away_team": "利物浦",
      "league": "英超",
      "match_date": "2026-01-16 20:30",
      "match_time": "2026-01-16 20:30",
      "odds_home_win": 2.15,
      "odds_draw": 3.20,
      "odds_away_win": 3.65,
      "status": "scheduled",
      "popularity": 85
    },
    ...
  ]
}
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 响应状态：success / error |
| count | integer | 返回的比赛数量 |
| matches | array | 比赛数据数组 |
| matches[].id | string | 比赛唯一ID |
| matches[].home_team | string | 主队名称 |
| matches[].away_team | string | 客队名称 |
| matches[].league | string | 所属联赛 |
| matches[].match_date | string | 比赛时间（格式：YYYY-MM-DD HH:MM） |
| matches[].odds_home_win | float | 主队胜赔率 |
| matches[].odds_draw | float | 平局赔率 |
| matches[].odds_away_win | float | 客队胜赔率 |
| matches[].status | string | 比赛状态：scheduled/live/finished |
| matches[].popularity | integer | 热度指数（1-100） |

---

### 2. 获取热门比赛

**端点**: `GET /matches/popular`

**描述**: 获取热门比赛TOP N

**请求参数**:

| 参数 | 类型 | 必需 | 默认值 | 范围 |
|------|------|------|--------|------|
| `limit` | integer | 否 | 10 | 1-50 |

**请求示例**:

```bash
# 获取热门比赛前10场
curl "http://localhost:8000/api/jczq/matches/popular"

# 获取热门比赛前5场
curl "http://localhost:8000/api/jczq/matches/popular?limit=5"
```

**响应示例**:

```json
{
  "status": "success",
  "count": 10,
  "limit": 10,
  "matches": [...]
}
```

---

### 3. 获取联赛列表

**端点**: `GET /leagues`

**描述**: 获取未来N天内的所有联赛及其比赛数量

**请求参数**:

| 参数 | 类型 | 必需 | 默认值 |
|------|------|------|--------|
| `days` | integer | 否 | 3 |

**请求示例**:

```bash
curl "http://localhost:8000/api/jczq/leagues?days=3"
```

**响应示例**:

```json
{
  "status": "success",
  "days": 3,
  "total_leagues": 8,
  "leagues": [
    {
      "name": "英超",
      "match_count": 3
    },
    {
      "name": "西甲",
      "match_count": 2
    },
    ...
  ]
}
```

---

### 4. 获取比赛详情

**端点**: `GET /match/{match_id}`

**描述**: 获取单场比赛的详细信息

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| match_id | string | 比赛ID |

**请求示例**:

```bash
curl "http://localhost:8000/api/jczq/match/mock_001"
```

**响应示例**:

```json
{
  "status": "success",
  "source": "cache",
  "match": {
    "id": "mock_001",
    "match_id": "mock_001",
    "home_team": "曼城",
    ...
  }
}
```

---

### 5. 获取统计信息

**端点**: `GET /stats`

**描述**: 获取比赛数据的统计信息

**请求参数**:

| 参数 | 类型 | 必需 | 默认值 |
|------|------|------|--------|
| `days` | integer | 否 | 3 |

**请求示例**:

```bash
curl "http://localhost:8000/api/jczq/stats?days=3"
```

**响应示例**:

```json
{
  "status": "success",
  "days": 3,
  "total_matches": 15,
  "avg_odds_home": 2.45,
  "avg_odds_draw": 3.10,
  "avg_odds_away": 3.55,
  "leagues": {
    "英超": {
      "count": 3,
      "avg_popularity": 85.5,
      "total_popularity": 256
    },
    ...
  }
}
```

---

### 6. 清空缓存

**端点**: `POST /cache/clear`

**描述**: 清空比赛缓存

**请求参数**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `pattern` | string | 否 | 清空模式（如：matches:* 仅清空比赛缓存） |

**请求示例**:

```bash
# 清空所有缓存
curl -X POST "http://localhost:8000/api/jczq/cache/clear"

# 清空特定模式的缓存
curl -X POST "http://localhost:8000/api/jczq/cache/clear?pattern=matches:*"
```

**响应示例**:

```json
{
  "status": "success",
  "message": "缓存已清空",
  "pattern": null
}
```

---

### 7. 获取缓存统计

**端点**: `GET /cache/stats`

**描述**: 获取缓存系统的统计信息

**请求示例**:

```bash
curl "http://localhost:8000/api/jczq/cache/stats"
```

**响应示例**:

```json
{
  "status": "success",
  "timestamp": "2026-01-16T12:00:00",
  "cache_stats": {
    "memory": {
      "total_keys": 5,
      "total_size_bytes": 45820,
      "keys": ["matches:recent|3", "matches:popular|10", ...]
    },
    "redis": {
      "available": true,
      "total_keys": 12,
      "memory_used": "2.5M",
      "memory_peak": "3.1M"
    }
  }
}
```

---

## 🔄 缓存策略

### 缓存TTL

| 数据类型 | TTL | 说明 |
|---------|-----|------|
| 比赛列表 | 3600秒 | 1小时过期 |
| 单场比赛 | 7200秒 | 2小时过期 |
| 其他数据 | 1800秒 | 30分钟过期 |

### 缓存方案

系统支持两层缓存：

1. **Redis缓存**（生产环境）
   - 分布式缓存
   - 支持多个实例共享
   - 自动过期管理

2. **内存缓存**（本地/回退）
   - 内置内存缓存
   - Redis不可用时自动回退
   - 进程级别缓存

---

## 🌐 前端集成示例

### HTML页面

```html
<!DOCTYPE html>
<html>
<head>
    <title>竞彩足球</title>
</head>
<body>
    <div id="matches"></div>

    <script>
        // 获取比赛数据
        async function loadMatches() {
            const response = await fetch('/api/jczq/matches/recent?days=3');
            const data = await response.json();
            
            const html = data.matches.map(match => `
                <div class="match">
                    <h3>${match.home_team} vs ${match.away_team}</h3>
                    <p>${match.league} | ${match.match_date}</p>
                    <p>赔率: ${match.odds_home_win} - ${match.odds_draw} - ${match.odds_away_win}</p>
                </div>
            `).join('');
            
            document.getElementById('matches').innerHTML = html;
        }
        
        loadMatches();
    </script>
</body>
</html>
```

### JavaScript/React

```javascript
import { useState, useEffect } from 'react';

function JCZQSchedule() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const response = await fetch('/api/jczq/matches/recent?days=3');
        const data = await response.json();
        setMatches(data.matches);
      } finally {
        setLoading(false);
      }
    };

    fetchMatches();
    // 每30分钟刷新一次
    const interval = setInterval(fetchMatches, 30 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>加载中...</div>;

  return (
    <div>
      {matches.map(match => (
        <div key={match.id} className="match-card">
          <h3>{match.home_team} vs {match.away_team}</h3>
          <p>{match.league}</p>
          <p>赔率: {match.odds_home_win} - {match.odds_draw} - {match.odds_away_win}</p>
        </div>
      ))}
    </div>
  );
}

export default JCZQSchedule;
```

---

## 🚀 部署指南

### Docker部署

```bash
# 构建镜像
docker build -t sport-lottery-backend -f Dockerfile.production .

# 使用Docker Compose
docker-compose -f docker-compose.production.yml up -d

# 检查健康状态
docker-compose -f docker-compose.production.yml exec backend \
    python deploy_helper.py --check
```

### 初始化步骤

```bash
# 1. 初始化缓存系统
python deploy_helper.py --init-cache

# 2. 预热缓存
python deploy_helper.py --warmup

# 3. 运行完整初始化
python deploy_helper.py

# 4. 执行健康检查
python deploy_helper.py --check
```

---

## 🧪 测试

### 运行测试套件

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行所有测试
pytest tests/test_complete_suite.py -v

# 运行特定测试
pytest tests/test_complete_suite.py::TestSportteryScraper -v

# 生成测试覆盖率报告
pytest tests/test_complete_suite.py --cov=app --cov-report=html
```

### 手动测试

```bash
# 测试API可用性
curl http://localhost:8000/api/jczq/matches/recent

# 测试缓存
curl http://localhost:8000/api/jczq/cache/stats

# 清空缓存
curl -X POST http://localhost:8000/api/jczq/cache/clear
```

---

## 📱 错误处理

### 常见错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源未找到 |
| 500 | 服务器内部错误 |

### 错误响应示例

```json
{
  "detail": "获取数据失败: 网络超时"
}
```

---

## 📝 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0.0 | 2026-01-16 | 初始版本：基础API、缓存、前端集成 |

---

## 📞 支持

如有问题，请：

1. 查看日志文件：`logs/app.log`
2. 运行健康检查：`python deploy_helper.py --check`
3. 清空缓存重试：`curl -X POST /api/jczq/cache/clear`
4. 检查网络连接和防火墙设置

---

**最后更新**: 2026-01-16
