# ⚡ 爬虫模块快速启动指南

5分钟快速上手新爬虫模块！

---

## 📦 步骤1: 安装依赖 (1分钟)

```bash
cd c:/Users/11581/Downloads/sport-lottery-sweeper
pip install -r requirements-crawler.txt
```

**依赖列表**:
- ✅ aiohttp (异步HTTP)
- ✅ beautifulsoup4 (HTML解析)
- ✅ tenacity (重试机制)
- ✅ aiolimiter (速率限制)
- ✅ aiocache (缓存)

---

## 🧪 步骤2: 运行测试 (2分钟)

```bash
python scripts/test_new_crawler.py
```

**预期输出**:
```
🚀 爬虫模块测试套件

测试1: 爬虫引擎基础功能
✅ 状态码: 200

测试2: 竞彩网爬虫
✅ 获取到 20 场比赛

测试3: 爬虫协调器
✅ 获取到 20 场比赛

测试4: 性能测试
✅ 并发3次请求完成
💾 缓存加速比: 30.0x

✅ 所有测试通过！
```

---

## 💻 步骤3: 在代码中使用 (2分钟)

### 示例1: 获取比赛数据

创建文件 `test_scraper.py`:

```python
import asyncio
from backend.scrapers.coordinator import get_coordinator

async def main():
    # 获取全局协调器实例
    coordinator = await get_coordinator()
    
    # 获取未来3天的比赛
    matches = await coordinator.get_matches(days=3)
    
    # 打印结果
    print(f"\n获取到 {len(matches)} 场比赛:\n")
    for i, match in enumerate(matches[:5], 1):
        print(f"{i}. {match['home_team']} vs {match['away_team']}")
        print(f"   联赛: {match['league']}")
        print(f"   时间: {match['match_time']}")
        print(f"   赔率: {match['odds_home_win']} / {match['odds_draw']} / {match['odds_away_win']}\n")

# 运行
asyncio.run(main())
```

运行:
```bash
python test_scraper.py
```

### 示例2: 使用Celery任务

```python
from backend.tasks.crawler_tasks_v2 import crawl_all_leagues_concurrent

# 触发任务
result = crawl_all_leagues_concurrent.delay(days_ahead=3)

# 获取结果
print(result.get(timeout=300))
```

---

## 🎯 常用功能

### 获取比赛详情

```python
from backend.scrapers.coordinator import get_coordinator

async def get_detail():
    coordinator = await get_coordinator()
    
    # 获取比赛详情
    detail = await coordinator.get_match_detail('match_001')
    print(detail)

asyncio.run(get_detail())
```

### 获取赔率历史

```python
from backend.scrapers.coordinator import get_coordinator

async def get_odds():
    coordinator = await get_coordinator()
    
    # 获取赔率历史
    history = await coordinator.get_odds_history('match_001')
    print(f"赔率历史记录: {len(history)} 条")
    
    for record in history:
        print(f"时间: {record['time']}")
        print(f"赔率: {record['odds_home_win']} / {record['odds_draw']} / {record['odds_away_win']}")

asyncio.run(get_odds())
```

### 健康检查

```python
from backend.scrapers.coordinator import get_coordinator

async def health_check():
    coordinator = await get_coordinator()
    
    # 检查所有数据源
    health = await coordinator.health_check_all()
    
    for source, status in health.items():
        healthy = "✅" if status['healthy'] else "❌"
        print(f"{healthy} {source}: {status.get('response_time', 0):.3f}s")

asyncio.run(health_check())
```

---

## 🔧 配置

### 环境变量 (.env)

```bash
# 爬虫引擎配置
SCRAPER_MAX_CONNECTIONS=100
SCRAPER_TIMEOUT=15
SCRAPER_MAX_RETRIES=3
SCRAPER_RATE_LIMIT=10
SCRAPER_ENABLE_CACHE=true
SCRAPER_CACHE_TTL=300
```

### Celery配置

在 `backend/tasks/__init__.py` 中配置定时任务:

```python
celery_beat_schedule = {
    'crawl-leagues': {
        'task': 'app.tasks.crawler_tasks_v2.crawl_all_leagues_concurrent',
        'schedule': crontab(minute='*/30'),  # 每30分钟
        'args': (3,),
    },
}
```

---

## 🚀 启动服务

### 1. 启动FastAPI

```bash
uvicorn backend.main:app --reload
```

### 2. 启动Celery Worker

```bash
celery -A backend.tasks worker --loglevel=info
```

### 3. 启动Celery Beat

```bash
celery -A backend.tasks beat --loglevel=info
```

---

## 📊 查看统计

```python
from backend.scrapers.coordinator import get_coordinator

async def show_stats():
    coordinator = await get_coordinator()
    stats = coordinator.get_stats()
    
    print("引擎统计:")
    print(f"  总请求: {stats['engine_stats']['total_requests']}")
    print(f"  成功率: {stats['engine_stats'].get('success_rate', 0):.1f}%")
    print(f"  缓存命中率: {stats['engine_stats'].get('cache_hit_rate', 0):.1f}%")

asyncio.run(show_stats())
```

---

## 🐛 故障排查

### 问题1: 导入错误

```
ModuleNotFoundError: No module named 'aiolimiter'
```

**解决**: 
```bash
pip install -r requirements-crawler.txt
```

### 问题2: 所有数据都是模拟的

**原因**: 真实数据源未配置

**解决**:
1. 查看 `backend/scrapers/sources/sporttery.py`
2. 实现 `_fetch_from_api()` 或 `_fetch_from_html()` 方法
3. 或者保持使用模拟数据进行测试

### 问题3: Celery任务不执行

**检查**:
```bash
# 1. 确认worker运行
celery -A backend.tasks worker --loglevel=info

# 2. 确认beat运行
celery -A backend.tasks beat --loglevel=info

# 3. 查看任务状态
from backend.tasks.crawler_tasks_v2 import crawl_all_leagues_concurrent
result = crawl_all_leagues_concurrent.delay(3)
print(result.state)
```

---

## 📚 进一步学习

- 📄 [重构指南](./CRAWLER_REFACTOR_GUIDE.md) - 详细文档
- 📄 [架构图](./CRAWLER_ARCHITECTURE.md) - 系统架构
- 📄 [分析报告](./CRAWLER_MODULE_ANALYSIS.md) - 性能分析
- 📄 [总结文档](./CRAWLER_REFACTOR_SUMMARY.md) - 重构总结

---

## ✅ 检查清单

完成快速启动后，确认以下项目:

- [ ] 依赖已安装
- [ ] 测试脚本运行成功
- [ ] 能够获取比赛数据
- [ ] Celery任务可以执行
- [ ] 健康检查通过

**恭喜！你已经成功上手新爬虫模块！** 🎉

---

**需要帮助?** 查看详细文档或提交Issue。
