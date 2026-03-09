# 实体映射 Stage-0 回归基线清单（API + 页面）

## 1. 目标

形成“可重复执行、可对照记录”的最小回归基线，作为 PR-2/3/4 每批改动的回归门禁。

## 2. 执行前条件

- 后端运行：`http://127.0.0.1:8000`
- 前端运行：`http://localhost:3000`
- 可用管理员账号（本地默认）：`admin/admin123`

## 3. API 基线检查（必跑）

### 3.1 登录拿 token

```powershell
$body = @{ username='admin'; password='admin123' } | ConvertTo-Json
$login = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/api/v1/auth/login' -ContentType 'application/json' -Body $body
$token = if($login.access_token){$login.access_token}else{$login.data.access_token}
$headers = @{ Authorization = "Bearer $token" }
```

### 3.2 实体映射核心接口

```powershell
Invoke-RestMethod -Method Get  -Uri 'http://127.0.0.1:8000/api/v1/entity-mapping/mappings/team'   -Headers $headers
Invoke-RestMethod -Method Get  -Uri 'http://127.0.0.1:8000/api/v1/entity-mapping/mappings/league' -Headers $headers
Invoke-RestMethod -Method Get  -Uri 'http://127.0.0.1:8000/api/v1/entity-mapping/sync/status'     -Headers $headers
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/api/v1/entity-mapping/sync/trigger'    -Headers $headers
```

通过标准：
- 全部 HTTP `200`
- `sync/status` 返回 `data.last_run` 且 `status` 字段存在
- `mappings/team` 和 `mappings/league` 返回 `data` 对象

### 3.3 官方信息接口抽检

```powershell
Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8000/api/v1/entity-mapping/official-info/summary' -Headers $headers
```

通过标准：
- HTTP `200`
- `status=success`

## 4. 页面基线检查（手工路径）

### 4.1 `/admin/system/entity-mappings`

路径：登录 -> 系统管理 -> 实体映射管理

检查点：
- 页面可打开，无白屏/路由报错
- 球队映射表能加载数据
- 切换“联赛映射”后可加载数据
- 点击“立即同步”后无前端异常，接口返回成功
- 点击“刷新状态”后状态区刷新

### 4.2 `/admin/data-source/official-info`

路径：登录 -> 数据源管理 -> 官方信息管理

检查点：
- 页面可打开
- 球队/联赛标签可切换
- 列表可正常加载（不出现 4xx/5xx）

## 5. 回归记录模板（每批次复制一份）

| 批次 | 日期 | 代码范围 | API 通过率 | 页面通过率 | 主要失败点 | 处理结论 |
|---|---|---|---|---|---|---|
| Batch-1 | YYYY-MM-DD | Stage-0 | x/x | x/x | - | - |

## 6. Stage-0 Batch-1 实际执行结果（2026-03-04）

### 6.1 API 结果

- 登录：通过（200）
- `GET /mappings/team`：通过（200）
- `GET /mappings/league`：通过（200）
- `GET /sync/status`：通过（200）
- `POST /sync/trigger`：通过（200）
- `GET /official-info/summary`：通过（200）

### 6.2 页面结果

- `/admin/system/entity-mappings`：通过（可加载、可切换、可触发同步、可刷新状态）
  - Playwright 抽检行数：`4979`
- `/admin/data-source/official-info`：通过（可加载、可切换、无路由异常）
  - Playwright 抽检行数：`4979`

### 6.3 本轮接口状态快照

- `POST /api/v1/auth/login`：`200`
- `GET /api/v1/entity-mapping/mappings/team`：`200`
- `GET /api/v1/entity-mapping/mappings/league`：`200`
- `GET /api/v1/entity-mapping/sync/status`：`200`
- `POST /api/v1/entity-mapping/sync/trigger`：`200`
- `GET /api/v1/entity-mapping/official-info/summary`：`200`

## 7. 失败分级规则

- P0：页面白屏、核心接口 5xx、无法登录
- P1：核心操作不可达（同步按钮无效、列表为空且接口异常）
- P2：文案/样式问题、不影响主流程

## 8. 下一批执行门禁

进入 PR-2 前必须满足：
- API 基线全部通过
- `/admin/system/entity-mappings` 页面链路通过
- 本文档回归记录已更新
