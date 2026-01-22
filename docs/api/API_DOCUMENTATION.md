# 竞彩足球扫盘系统 - API文档

## API设计原则

1. **统一接口风格（RESTful优先）**
   - GET 获取资源
   - POST 创建资源
   - PUT 更新完整资源
   - PATCH 部分更新资源
   - DELETE 删除资源

2. **统一命名规范**
   - 全部小写，使用连字符分隔
   - 复数形式表示资源集合
   - 避免动词，使用名词表达资源

3. **统一响应格式**
   - `code`: 状态码（200成功，4xx/5xx错误）
   - `message`: 人类可读的描述
   - `data`: 实际业务数据
   - `timestamp`: 响应时间戳

4. **统一参数设计**
   - 分页参数：`page` 和 `size`
   - 排序参数：`sort` 和 `order`
   - 日期格式：统一使用 `yyyy-MM-dd`
   - ID格式：统一使用UUID或自增ID

5. **统一版本控制**
   - 采用语义化版本控制
   - 路径版本：`/api/v1/users`

---

## API端点列表

### 1. 比赛管理 (/api/v1/matches)

#### GET /api/v1/matches
获取比赛列表

**参数:**
- `page` (integer, optional): 页码，默认为1
- `size` (integer, optional): 每页大小，默认为10，最大100
- `sort` (string, optional): 排序字段
- `order` (string, optional): 排序方向 asc/desc，默认desc
- `date_from` (string, optional): 起始日期 (YYYY-MM-DD)
- `date_to` (string, optional): 结束日期 (YYYY-MM-DD)
- `league` (string, optional): 联赛过滤
- `status` (string, optional): 比赛状态过滤

**响应:**
```json
{
  "code": 200,
  "message": "获取比赛列表成功",
  "data": {
    "data": [...],
    "total": 100,
    "page": 1,
    "size": 10,
    "pages": 10,
    "timestamp": "2026-01-16T20:26:55"
  },
  "timestamp": "2026-01-16T20:26:55"
}
```

#### GET /api/v1/matches/{match_id}
获取比赛详情

**参数:**
- `match_id` (string): 比赛ID

**响应:**
```json
{
  "code": 200,
  "message": "获取比赛详情成功",
  "data": {...},
  "timestamp": "2026-01-16T20:26:55"
}
```

#### POST /api/v1/matches
创建比赛

**请求体:**
```json
{
  "home_team": "主队名称",
  "away_team": "客队名称",
  "league": "联赛名称",
  "match_time": "2026-01-16T20:00:00"
}
```

**响应:**
```json
{
  "code": 201,
  "message": "比赛创建成功",
  "data": {...},
  "timestamp": "2026-01-16T20:26:55"
}
```

#### PUT /api/v1/matches/{match_id}
更新比赛完整信息

**参数:**
- `match_id` (string): 比赛ID

**请求体:**
```json
{
  "home_team": "主队名称",
  "away_team": "客队名称",
  "league": "联赛名称",
  "match_time": "2026-01-16T20:00:00"
}
```

**响应:**
```json
{
  "code": 200,
  "message": "比赛更新成功",
  "data": {...},
  "timestamp": "2026-01-16T20:26:55"
}
```

#### PATCH /api/v1/matches/{match_id}
部分更新比赛信息

**参数:**
- `match_id` (string): 比赛ID

**请求体:**
```json
{
  "home_team": "新主队名称"
}
```

**响应:**
```json
{
  "code": 200,
  "message": "比赛部分更新成功",
  "data": {...},
  "timestamp": "2026-01-16T20:26:55"
}
```

#### DELETE /api/v1/matches/{match_id}
删除比赛

**参数:**
- `match_id` (string): 比赛ID

**响应:**
```json
{
  "code": 200,
  "message": "比赛删除成功",
  "data": null,
  "timestamp": "2026-01-16T20:26:55"
}
```

#### GET /api/v1/matches/popular
获取热门比赛

**参数:**
- `limit` (integer, optional): 返回数量，默认10，最大50

**响应:**
```json
{
  "code": 200,
  "message": "获取热门比赛成功",
  "data": [...],
  "timestamp": "2026-01-16T20:26:55"
}
```

#### GET /api/v1/matches/trending
获取趋势比赛

**参数:**
- `limit` (integer, optional): 返回数量，默认10，最大50

**响应:**
```json
{
  "code": 200,
  "message": "获取趋势比赛成功",
  "data": [...],
  "timestamp": "2026-01-16T20:26:55"
}
```

---

### 2. 竞彩足球 (/api/v1/jczq)

#### GET /api/v1/jczq
获取竞彩足球比赛列表

**参数:**
- `page` (integer, optional): 页码，默认为1
- `size` (integer, optional): 每页大小，默认为10，最大50
- `date_from` (string, optional): 起始日期 (YYYY-MM-DD)
- `date_to` (string, optional): 结束日期 (YYYY-MM-DD)
- `league` (string, optional): 联赛过滤
- `sort` (string, optional): 排序字段
- `order` (string, optional): 排序方向 asc/desc，默认asc

**响应:**
```json
{
  "code": 200,
  "message": "获取竞彩足球比赛数据成功",
  "data": {
    "data": [...],
    "total": 100,
    "page": 1,
    "size": 10,
    "pages": 10
  },
  "timestamp": "2026-01-16T20:26:55"
}
```

#### GET /api/v1/jczq/{match_id}
获取竞彩足球比赛详情

**参数:**
- `match_id` (string): 比赛ID

**响应:**
```json
{
  "code": 200,
  "message": "获取比赛详情成功",
  "data": {...},
  "timestamp": "2026-01-16T20:26:55"
}
```

#### POST /api/v1/jczq/refresh
刷新竞彩足球数据

**响应:**
```json
{
  "code": 200,
  "message": "数据刷新成功",
  "data": {
    "refreshed_at": "2026-01-16T20:26:55"
  },
  "timestamp": "2026-01-16T20:26:55"
}
```

#### GET /api/v1/jczq/leagues
获取竞彩足球联赛列表

**参数:**
- `days` (integer, optional): 未来天数，默认3，范围1-7

**响应:**
```json
{
  "code": 200,
  "message": "获取联赛列表成功",
  "data": {...},
  "timestamp": "2026-01-16T20:26:55"
}
```

#### GET /api/v1/jczq/stats
获取竞彩足球数据统计

**参数:**
- `days` (integer, optional): 未来天数，默认3，范围1-7

**响应:**
```json
{
  "code": 200,
  "message": "获取数据统计成功",
  "data": {...},
  "timestamp": "2026-01-16T20:26:55"
}
```

---

### 3. 情报管理 (/api/v1/intelligence)

#### GET /api/v1/intelligence
获取情报列表

#### GET /api/v1/intelligence/{id}
获取情报详情

#### POST /api/v1/intelligence
创建情报

#### PUT /api/v1/intelligence/{id}
更新情报

#### PATCH /api/v1/intelligence/{id}
部分更新情报

#### DELETE /api/v1/intelligence/{id}
删除情报

---

### 4. 用户认证 (/api/v1/auth)

#### POST /api/v1/auth/login
用户登录

#### POST /api/v1/auth/logout
用户登出

#### POST /api/v1/auth/register
用户注册

#### GET /api/v1/auth/me
获取当前用户信息

---

### 5. 管理后台 (/api/v1/admin)

#### GET /api/v1/admin/users
获取用户列表

#### GET /api/v1/admin/users/{id}
获取用户详情

#### PUT /api/v1/admin/users/{id}
更新用户信息

#### DELETE /api/v1/admin/users/{id}
删除用户

#### GET /api/v1/admin/matches
获取比赛管理列表

#### PUT /api/v1/admin/matches/{id}
更新比赛信息

---

### 6. WebSocket端点

#### ws://localhost:8000/api/v1/ws/matches
实时比赛更新

---

## 错误码说明

- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 禁止访问
- `404`: 资源不存在
- `422`: 参数验证失败
- `500`: 服务器内部错误