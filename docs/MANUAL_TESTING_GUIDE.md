# 竞彩赛程数据测试指南

## ✅ 已完成的工作

### 1. 修复数据加载函数
**文件**: `backend/api/v1/lottery.py`
- ✅ 生成正确的数字ID（从1开始递增）
- ✅ 分离 `match_date` 和 `match_time`
- ✅ 保留原始 `popularity` 值

### 2. 创建路由映射
**文件**: `backend/api/v1/admin_matches.py` (新建)
- ✅ 将 `/admin/matches` API 映射到 `/lottery/matches`
- ✅ 转换响应格式以匹配前端期望

### 3. 修复路由冲突
**文件**: `backend/api/v1/__init__.py`
- ✅ 解决 `/admin/matches` 路由冲突
- ✅ 正确注册所有路由

### 4. 准备测试数据
**文件**: `debug/500_com_matches_20260126_013748.json`
- ✅ 10条测试比赛数据已准备

## 🎯 下一步操作步骤

### 步骤1: 重启后端服务
```bash
cd c:\Users\11581\Downloads\sport-lottery-sweeper\backend
python main.py
```

### 步骤2: 在浏览器中测试API

#### 测试1: 直接访问lottery API
打开浏览器访问：
```
http://localhost:8000/api/v1/lottery/matches?source=500&page=1&size=10
```

**期望结果**: JSON格式的比赛数据，包含10条记录

#### 测试2: 访问admin API
打开浏览器访问：
```
http://localhost:8000/api/v1/admin/matches?source=500&page=1&size=10
```

**期望结果**: 格式化的JSON数据，包含 `code`, `message`, `data`, `pagination` 字段

### 步骤3: 启动前端服务
```bash
cd c:\Users\11581\Downloads\sport-lottery-sweeper
npm run dev
# 或
pnpm dev
```

### 步骤4: 在前端页面查看
1. 访问: http://localhost:3000
2. 登录系统
3. 导航到 **"竞彩赛程管理"** 或 **"比赛管理"** 页面
4. 应该能看到500彩票网的10条比赛数据

## 📊 测试数据内容

**数据源**: 500万彩票 (https://trade.500.com/jczq/)

包含以下10条比赛数据：

1. 周二01 - 日职联 - 大阪钢巴 vs 浦和红钻
2. 周二02 - 中超 - 北京国安 vs 上海申花
3. 周二03 - 中超 - 山东泰山 vs 广州恒大
4. 周二04 - 英超 - 曼联 vs 利物浦
5. 周三05 - 英超 - 切尔西 vs 阿森纳
6. 周三06 - 西甲 - 皇马 vs 巴萨
7. 周三07 - 中超 - 江苏苏宁 vs 河南建业
8. 周三08 - 中超 - 天津泰达 vs 重庆当代
9. 周四09 - 德甲 - 拜仁 vs 多特
10. 周四10 - 中超 - 武汉卓尔 vs 石家庄永昌

## 🔧 如果数据未显示

### 问题1: API返回500错误
**可能原因**: 后端代码有语法错误
**解决方法**:
1. 查看后端控制台日志
2. 检查 `backend/api/v1/lottery.py` 第22-84行
3. 检查 `backend/api/v1/admin_matches.py` 第10-65行

### 问题2: API返回200但无数据
**可能原因**: debug文件路径错误或文件不存在
**解决方法**:
1. 检查文件是否存在: `debug/500_com_matches_20260126_013748.json`
2. 检查文件内容是否为有效的JSON格式
3. 检查 `lottery.py` 中 debug_dir 路径计算是否正确

### 问题3: 前端显示错误
**可能原因**: 前端API调用失败
**解决方法**:
1. 打开浏览器开发者工具 (F12)
2. 查看 Network 标签中的API请求
3. 检查 Console 中的JavaScript错误
4. 确认前端访问的是 `/api/v1/admin/matches` 而不是 `/api/v1/lottery/matches`

### 问题4: 数据格式不匹配
**可能原因**: 前端期望的字段名与后端返回的不一致
**解决方法**:
1. 比较前端 `LotterySchedule.vue` 中使用的字段名
2. 检查后端 `admin_matches.py` 返回的数据结构
3. 确保字段名匹配: id, match_id, league, home_team, away_team, match_time, match_date, odds_*, status, score, popularity, source

## 📋 数据源信息

### 500万彩票数据源
- **名称**: 500万彩票
- **URL**: https://trade.500.com/jczq/
- **类型**: web
- **状态**: 启用
- **配置**:
  ```json
  {
    "source_type": "web_scraper",
    "data_type": "lottery_schedule",
    "parser_type": "html_parser",
    "update_frequency": "daily",
    "timeout": 30,
    "retry_count": 3,
    "url_pattern": "https://trade.500.com/jczq/"
  }
  ```

## 🔍 调试技巧

### 查看后端日志
后端启动后，观察控制台输出：
- 是否有路由注册成功的信息
- 是否有错误堆栈跟踪
- API请求时的日志输出

### 手动测试数据加载
```python
cd backend
python -c "
from api.v1.lottery import load_500_com_data
data = load_500_com_data()
print(f'Loaded {len(data)} matches')
if data:
    print(f'First match: {data[0]}')
"
```

### 清除缓存
如果怀疑是缓存问题：
```
http://localhost:8000/api/v1/lottery/refresh
```

## ✅ 成功标志

当一切正常工作时，你应该：

1. **API测试**: 浏览器访问 `/api/v1/admin/matches?source=500&page=1&size=10` 能看到JSON数据
2. **前端显示**: 竞彩赛程页面显示10条比赛数据
3. **数据正确**: 每条数据有正确的id, match_id, league, teams, odds等信息
4. **分页工作**: 分页组件显示正确的页码和总数

## 📝 总结

现在请执行以下操作：
1. ✅ 重启后端服务 (必须重启！)
2. ✅ 在浏览器中测试两个API端点
3. ✅ 启动前端服务
4. ✅ 在竞彩赛程页面查看数据

如果还有问题，请提供：
- 后端控制台的错误日志
- 浏览器中API请求的响应内容
- 浏览器Console中的JavaScript错误
