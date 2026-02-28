# 北单赔率详情秒开与多源自动抓取实施清单（可直接开发）

文档版本: v1.0  
创建日期: 2026-02-28  
适用范围: `500w`、`盈球`、`100球` 的北单赛程与其它赔率抓取链路  
目标页面: `/admin/match-data/schedule/bd`、`/admin/data-source/config`

---

## 1. 目标与成功标准

### 1.1 业务目标

1. 打开“其它赔率详情”时，优先展示缓存，避免等待远程抓取。
2. 抓取体系从“手动触发”升级为“自动发现 + 自动入队 + 自动补抓”。
3. `100球` 期号自动跟随 `500w(bjdc)` 最新期号，无需人工填写期号。
4. 数据源列表自动出现“100球-北单-<期号>”新实例记录（新ID）。

### 1.2 技术目标（SLO）

1. 详情接口首屏响应: `< 300ms`（仅读缓存）。
2. 详情打开后 20 秒内三标签完整率（eu/asia/goals）: `> 90%`。
3. `/other-odds` 接口超时率: `< 1%`。
4. 抓取任务重复执行率: `< 0.5%`。

### 1.3 非目标（本期不做）

1. 不重构全站爬虫框架。
2. 不修改现有比赛核心模型主键体系。
3. 不在本期引入新中间件（例如 Kafka）；优先复用现有 Redis/Celery/线程任务能力。

---

## 2. 当前实现锚点（现有代码）

1. 详情接口与抓取逻辑耦合: `backend/api/v1/admin/lottery_schedule.py`。
2. 赛程模型与缓存载体: `backend/models/match.py`（`source_attributes`）。
3. 通用异步任务表: `backend/models/async_task.py`。
4. 任务状态管理参考实现: `backend/api/v1/draw_prediction.py`（`AsyncTask` 写入与查询逻辑）。
5. 任务基础设施: `backend/tasks/simple_celery.py`、`backend/services/task_scheduler_service.py`。
6. 前端详情页: `frontend/src/views/admin/sp/ScheduleManagement.vue`。
7. 数据源管理页: `frontend/src/views/admin/crawler/DataSourceManagement.vue`。

---

## 3. 目标架构（读写解耦）

### 3.1 核心原则

1. `GET /other-odds` 只读缓存，绝不触发远程慢抓。
2. 所有抓取动作通过任务系统执行，接口只入队。
3. 抓取按“缺什么抓什么”，不全量重抓。
4. 去重与锁在 Worker 侧执行，避免并发重复抓取。

### 3.2 架构分层

1. API 层:
   只读缓存、触发任务、查任务状态。
2. 调度层:
   定时发现最新期号、定时补抓临近比赛、导入后预热。
3. Worker 层:
   执行抓取、写缓存、更新状态、重试退避。
4. 存储层:
   `matches.source_attributes`（兼容） + 抓取状态表（调度依据）。

---

## 4. 数据库与模型改造清单

## 4.1 新增表: `bd_other_odds_fetch_state`

用途: 一场比赛一行，记录三标签抓取状态与调度元数据。

字段建议:

1. `id` BIGINT PK
2. `match_id` BIGINT UNIQUE NOT NULL
3. `data_source` VARCHAR(32) NOT NULL DEFAULT `yingqiu_bd`
4. `fixture_id` VARCHAR(64) NULL
5. `resolved_mid` VARCHAR(64) NULL
6. `eu_status` VARCHAR(16) NOT NULL DEFAULT `missing`
7. `asia_status` VARCHAR(16) NOT NULL DEFAULT `missing`
8. `goals_status` VARCHAR(16) NOT NULL DEFAULT `missing`
9. `eu_rows` JSON NULL
10. `asia_rows` JSON NULL
11. `goals_rows` JSON NULL
12. `last_attempt_at` DATETIME NULL
13. `last_success_at` DATETIME NULL
14. `next_retry_at` DATETIME NULL
15. `retry_count` INT NOT NULL DEFAULT 0
16. `consecutive_failures` INT NOT NULL DEFAULT 0
17. `last_error_code` VARCHAR(64) NULL
18. `last_error_message` VARCHAR(500) NULL
19. `priority` INT NOT NULL DEFAULT 100
20. `lock_token` VARCHAR(64) NULL
21. `lock_expires_at` DATETIME NULL
22. `created_at` DATETIME NOT NULL
23. `updated_at` DATETIME NOT NULL

状态枚举建议:

1. `missing`
2. `fetching`
3. `ready`
4. `stale`
5. `failed`

索引建议:

1. `idx_bd_fetch_state_retry_priority (next_retry_at, priority)`
2. `idx_bd_fetch_state_goals_retry (goals_status, next_retry_at)`
3. `idx_bd_fetch_state_updated_at (updated_at)`

### 4.2 新增表: `source_issue_tracking`

用途: 跟踪各数据源最新期号与发现状态，支持 100球 跟随 500w 期号。

字段建议:

1. `id` BIGINT PK
2. `source_type` VARCHAR(32) NOT NULL (`500w_bjdc`/`100qiu`/`yingqiu_bd`)
3. `latest_issue_no` VARCHAR(32) NULL
4. `last_processed_issue_no` VARCHAR(32) NULL
5. `last_discovered_at` DATETIME NULL
6. `last_processed_at` DATETIME NULL
7. `status` VARCHAR(16) NOT NULL DEFAULT `idle`
8. `last_error` VARCHAR(500) NULL
9. `created_at` DATETIME NOT NULL
10. `updated_at` DATETIME NOT NULL

唯一约束:

1. `uq_source_issue_tracking_source_type (source_type)`

### 4.3 数据源实例唯一约束（100球）

目标: 每个期号只生成一条 100球 实例源记录。

约束建议:

1. 在数据源表增加唯一约束 `uq_data_sources_type_issue_no (source_type, issue_no)`。

### 4.4 任务复用策略

1. 首期复用 `async_tasks`。
2. `task_type` 约定:
   `bd_other_odds_prefetch`、`issue_discovery`、`source_fetch_500w`、`source_fetch_yingqiu`、`source_fetch_100qiu`。

---

## 5. API 契约清单（开发级）

### 5.1 `GET /api/v1/admin/lottery-schedules/{match_id}/other-odds`

语义:

1. 只读缓存，不触发远程抓取。

响应新增字段:

1. `completeness`
2. `is_warming`
3. `last_success_at`
4. `last_attempt_at`
5. `next_retry_at`
6. `stale_seconds`
7. `tabs_meta`（可选，逐 tab 状态）

`completeness` 示例:

```json
{
  "eu": {"status": "ready", "count": 48, "updated_at": "2026-02-28 12:10:00"},
  "asia": {"status": "ready", "count": 23, "updated_at": "2026-02-28 12:09:52"},
  "goals": {"status": "fetching", "count": 0, "updated_at": null},
  "percent": 67
}
```

### 5.2 `POST /api/v1/admin/lottery-schedules/{match_id}/other-odds/refresh`

语义:

1. 触发任务入队（urgent），立即返回。

请求参数:

1. `force`: bool（默认 false）
2. `tabs`: array（可选，例 `["goals"]`）

响应:

1. `task_id`
2. `status`
3. `queued_at`

### 5.3 `GET /api/v1/admin/lottery-schedules/other-odds/tasks/{task_id}`

语义:

1. 查询任务状态，供前端轮询。

响应:

1. `task_id`
2. `status` (`pending/running/success/failed/retrying`)
3. `progress` (0-100)
4. `phase`
5. `result`
6. `error`

### 5.4 列表接口增强

接口: `GET /api/v1/admin/lottery-schedules`

每个 item 增加:

1. `other_odds_ready` (bool)
2. `other_odds_completeness_percent` (int)
3. `other_odds_last_success_at` (datetime)
4. `other_odds_is_warming` (bool)

---

## 6. 任务系统与调度清单

### 6.1 队列与优先级

队列建议:

1. `odds_prefetch_high`
2. `odds_prefetch_normal`
3. `issue_discovery`
4. `source_sync`

优先级规则:

1. 详情触发 urgent > 列表首屏预热 > 导入后全量预热 > 定时补抓。

### 6.2 去重键与锁

去重键:

1. `dedupe_key = "{match_id}:{tab}:{issue_no_or_date}"`。

锁策略:

1. 抢占 `match_id + tab` 锁。
2. `lock_expires_at` 超时自动释放。

### 6.3 重试与退避

错误分型:

1. `timeout`
2. `sign_error`
3. `empty_payload`
4. `rate_limited`
5. `upstream_5xx`

退避建议:

1. `timeout`: 30s, 60s, 120s
2. `sign_error`: 60s, 180s, 300s
3. `empty_payload`: 20s, 40s, 90s
4. `rate_limited`: 120s, 300s
5. 上限后置 `failed` 并记录 `next_retry_at`（由定时任务兜底再拉起）

### 6.4 触发矩阵

1. 导入 `yingqiu-bd` 成功后:
   入队当日全部比赛预热。
2. 打开列表页:
   首屏前 N 场入队（建议 N=8 或 12）。
3. 打开详情页:
   若 `completeness.percent < 100`，只入队不阻塞。
4. 定时补抓:
   `T-6h/T-2h/T-30m` 三档刷新。

---

## 7. 多源自动抓取清单（500w/盈球/100球）

### 7.1 统一自动抓取策略

1. `500w`:
   定时抓今天/明天/近期开赛。
2. `盈球`:
   定时抓今天/明天 + 详情赔率补抓。
3. `100球`:
   基于期号驱动抓取，不再手工填期号。

### 7.2 500w 期号发现器（权威源）

规则:

1. 期号来源唯一权威: `https://trade.500.com/bjdc/`。
2. 每 1-2 分钟解析最新 `issue_no`。
3. 若 `latest_issue_no > last_processed_issue_no`，触发新一期流程。

### 7.3 100球自动跟期号

1. 发现新期号后自动为 `100球` 入队。
2. 自动创建数据源实例（新ID）:
   命名建议 `100球-北单-<issue_no>`。
3. 同期幂等:
   若 `(source_type, issue_no)` 已存在则跳过创建，仅触发补抓。

### 7.4 跨期补抓

1. 若发现跳期（例如从 26026 到 26029）:
   自动补抓 26027、26028（可配置上限）。
2. 补抓优先级低于当前最新期号。

### 7.5 爬虫改造与反爬风险控制（必须落地）

目标:

1. 降低触发目标站点风控概率。
2. 在不增加高风险对抗手段前提下提高成功率与稳定性。

改造原则:

1. 以“少请求、稳节奏、可退避”为首要策略。
2. 以“增量抓取优先、全量抓取兜底”为执行顺序。
3. 以“接口直连快路径、浏览器兜底慢路径”为链路分层。

实施项:

1. 全局限速器:
   按域名单独设置并发与QPS上限，禁止无上限并发。
2. 请求节奏抖动:
   每次请求增加小抖动，避免固定周期命中风控模式。
3. 会话稳定:
   固定 User-Agent/Accept-Language/Referer 策略，避免高频随机画像切换。
4. 幂等去重:
   同一 `match_id + tab`、同一 `source + issue_no` 在同窗口只执行一次。
5. 分型重试:
   `429/403/signError/timeout/empty` 分别退避，不允许密集立即重试。
6. 熔断降级:
   连续失败达到阈值后进入冷却窗口，仅保留低频探测请求。
7. 浏览器兜底池化:
   Playwright 不按请求临时启动，采用常驻 browser/context 池，降低冷启动与指纹抖动。
8. 只抓缺项:
   已有 `eu+asia` 仅缺 `goals` 时只抓 `goals`，减少无效请求。
9. 负载分层:
   详情 urgent 任务优先，补抓和回填低优先级。
10. 合规边界:
   不实现高风险绕过动作（例如激进指纹伪造、验证码对抗等）。

建议初始参数:

1. `500w`:
   并发 2，QPS 0.5，失败退避 30/60/120 秒。
2. `盈球`:
   并发 2，QPS 0.33，失败退避 60/180/300 秒。
3. `100球`:
   并发 1，QPS 0.2，失败退避 60/180/300 秒。
4. Playwright 兜底:
   并发 1，单任务超时 20 秒，连续失败 5 次熔断 10 分钟。

---

## 8. 数据融合与覆盖规则

### 8.1 来源优先级（建议）

1. 赛程主体字段:
   `盈球` > `500w` > `100球`。
2. 北单特定赔率补充:
   `100球` 可作为补充源，但不覆盖已确认高质量字段。

### 8.2 覆盖原则

1. 同字段覆盖需满足“时间更近 + 质量等级不低”。
2. 原始 payload 必须保存，支持回溯与审计。
3. 禁止“最后写入全量覆盖”。

---

## 9. 前端改造清单（页面行为）

### 9.1 赛程详情弹窗

文件:

1. `frontend/src/views/admin/sp/ScheduleManagement.vue`

改造点:

1. 打开弹窗后立即展示缓存。
2. 若不完整，显示“后台补抓中”并轮询任务状态。
3. 手动“强制刷新”仅触发任务，不等待长请求。
4. 空标签页显示状态文案而非误导“暂无数据”。

### 9.2 数据源配置页

文件:

1. `frontend/src/views/admin/crawler/DataSourceManagement.vue`

改造点:

1. 显示 500w 最新期号发现状态。
2. 显示 100球 自动实例化结果（新ID、期号、状态）。
3. 保留手动入口但标记“应急”。

---

## 10. 后端文件级实施清单（可直接分工）

### 10.1 PR-1（接口与状态基础）

后端:

1. `backend/api/v1/admin/lottery_schedule.py`
   新增 `refresh` 入队接口、任务状态查询接口、详情只读缓存语义。
2. `backend/models/`  
   新增 `bd_other_odds_fetch_state.py`、`source_issue_tracking.py`。
3. `alembic/versions/`
   新增迁移脚本（新表、索引、唯一约束）。
4. `backend/schemas/`
   增加接口响应模型（completeness/task status）。

前端:

1. `frontend/src/views/admin/sp/ScheduleManagement.vue`
   适配新接口字段与状态展示。
2. `frontend/src/api/modules/`（按现有组织）
   增加 refresh/task-status API 方法。

验收:

1. 详情接口不再触发远程抓取。
2. 强制刷新返回 `task_id`。

### 10.2 PR-2（队列化与调度）

后端:

1. `backend/tasks/`  
   新增 odds prefetch worker 任务定义。
2. `backend/services/`
   新增 `odds_prefetch_service.py`（缺项抓取、写状态、重试策略）。
3. `backend/tasks/simple_celery.py`
   注册新任务队列。
4. `backend/services/task_scheduler_service.py`
   接入定时补抓策略（T-6h/T-2h/T-30m）。

运维:

1. 新增 worker 启停脚本（Windows 环境）。
2. 明确 `uvicorn` 与 worker 分离运行。

验收:

1. 任务可稳定消费，去重生效。
2. 不出现 Web 进程内长时抓取。

### 10.3 PR-3（500w 期号发现 + 100球自动化）

后端:

1. 新增 `issue_discovery_service.py`
   定时解析 `500w(bjdc)` 最新期号。
2. 新增 `source_auto_instance_service.py`
   自动生成 100球 期号实例源（新ID）。
3. 调度任务:
   `issue_discovery`、`source_sync_100qiu`。

前端:

1. `DataSourceManagement.vue`
   显示“发现状态、实例状态、失败原因”。

验收:

1. 新期号无需人工填写即可自动抓取。
2. 数据源列表自动新增对应 100球 实例行。

---

## 11. 配置项清单（环境变量）

建议新增:

1. `BD_OTHER_ODDS_CACHE_ONLY_READ=1`
2. `BD_OTHER_ODDS_PREFETCH_ENABLED=1`
3. `BD_OTHER_ODDS_PREFETCH_WORKER_CONCURRENCY=4`
4. `BD_OTHER_ODDS_PREFETCH_TIMEOUT_SECONDS=20`
5. `BD_OTHER_ODDS_PREFETCH_MAX_RETRY=5`
6. `ISSUE_DISCOVERY_ENABLED=1`
7. `ISSUE_DISCOVERY_INTERVAL_SECONDS=120`
8. `AUTO_CREATE_100QIU_SOURCE_INSTANCE=1`
9. `AUTO_BACKFILL_MISSING_ISSUES_MAX=3`
10. `CRAWLER_GLOBAL_RATE_LIMIT_ENABLED=1`
11. `CRAWLER_DOMAIN_500W_MAX_CONCURRENCY=2`
12. `CRAWLER_DOMAIN_500W_QPS=0.5`
13. `CRAWLER_DOMAIN_YINGQIU_MAX_CONCURRENCY=2`
14. `CRAWLER_DOMAIN_YINGQIU_QPS=0.33`
15. `CRAWLER_DOMAIN_100QIU_MAX_CONCURRENCY=1`
16. `CRAWLER_DOMAIN_100QIU_QPS=0.2`
17. `CRAWLER_REQUEST_JITTER_MS_MIN=150`
18. `CRAWLER_REQUEST_JITTER_MS_MAX=600`
19. `CRAWLER_CIRCUIT_BREAKER_FAIL_THRESHOLD=5`
20. `CRAWLER_CIRCUIT_BREAKER_COOLDOWN_SECONDS=600`
21. `CRAWLER_PLAYWRIGHT_POOL_ENABLED=1`
22. `CRAWLER_PLAYWRIGHT_POOL_SIZE=1`
23. `CRAWLER_PLAYWRIGHT_TASK_TIMEOUT_SECONDS=20`

---

## 12. 观测与告警清单

### 12.1 指标

1. `odds_prefetch_tab_success_rate{tab=eu|asia|goals}`
2. `odds_prefetch_duration_ms_p95`
3. `odds_prefetch_queue_backlog`
4. `odds_detail_cache_hit_ratio`
5. `issue_discovery_lag_seconds`
6. `source_instance_create_fail_total`
7. `crawler_http_429_total{domain}`
8. `crawler_http_403_total{domain}`
9. `crawler_sign_error_total{domain}`
10. `crawler_circuit_breaker_open_total{domain}`
11. `crawler_request_rate{domain}`
12. `crawler_playwright_fallback_ratio`
13. `crawler_dedupe_hit_total`

### 12.2 日志字段标准

1. `trace_id`
2. `match_id`
3. `fixture_id`
4. `issue_no`
5. `task_id`
6. `tab`
7. `status`
8. `error_code`
9. `duration_ms`

### 12.3 告警阈值

1. goals 成功率连续 15 分钟 < 70%。
2. 任务堆积 > 500 持续 10 分钟。
3. 期号发现延迟 > 10 分钟。
4. 任一域名 429 在 10 分钟内 > 50。
5. 熔断状态持续 > 20 分钟未恢复。
6. Playwright 兜底占比 > 30% 持续 30 分钟。

---

## 13. 测试与验收清单

### 13.1 单元测试

1. completeness 计算逻辑。
2. 去重键与锁超时逻辑。
3. 重试退避策略分支。
4. 期号解析与比较逻辑（500w 页面结构变动兜底）。
5. 限速器、抖动器、熔断器状态机逻辑。
6. 去重键冲突场景（并发提交下只执行一次）。

### 13.2 集成测试

1. `refresh` 入队后任务状态流转。
2. 缓存读接口首屏响应耗时。
3. 缺 goals 场景自动补抓成功。
4. 100球 新期号自动建实例源与自动抓取。
5. 429/403/signError 注入场景下退避与熔断生效。
6. Playwright 池化后兜底成功率与时延验证。

### 13.3 E2E 测试

1. 进入北单赛程页 -> 点详情 -> 首屏立即见数据 -> 后台补齐标签。
2. 数据源管理页显示最新期号与100球新实例行。
3. 人工不触发任何按钮情况下，跨新期号自动完成发现->建实例->抓取->入库。
4. 模拟上游限流时系统自动降频且不会打爆目标站点。

---

## 14. 灰度与回滚清单

### 14.1 灰度步骤

1. Step-0:
   仅加指标，不改行为，观察 1-2 天基线。
2. Step-1:
   开启 `CACHE_ONLY_READ`，保留旧逻辑开关兜底。
3. Step-2:
   开启预抓队列与详情 urgent 入队。
4. Step-3:
   开启 500w 期号发现与 100球自动实例化。
5. Step-4:
   隐藏手动主入口，仅保留应急操作。

### 14.2 回滚策略

1. 关闭 `BD_OTHER_ODDS_CACHE_ONLY_READ` 回退到旧行为。
2. 关闭 `ISSUE_DISCOVERY_ENABLED` 停止自动发现。
3. 关闭 `AUTO_CREATE_100QIU_SOURCE_INSTANCE` 停止自动建新ID。
4. 保留接口兼容字段，前端无需紧急回滚。

---

## 15. 任务分配模板（建议）

1. 后端A:
   接口改造、状态表、任务写回。
2. 后端B:
   Worker 队列、调度、期号发现器。
3. 前端A:
   详情弹窗状态流与轮询。
4. 前端B:
   数据源页自动实例化展示。
5. QA:
   场景矩阵回归 + 压测。

---

## 16. 上线前检查（Go/No-Go）

1. 所有迁移脚本已在测试库验证可回滚。
2. Worker 与 Web 独立进程运行稳定 24 小时。
3. 详情接口 P95 < 300ms。
4. 缺标签补抓成功率达标。
5. 100球 自动新期号流程至少连续通过 3 个期号。

---

## 17. 待确认项（进入开发前必须拍板）

1. 100球 实例源是否保留历史实例（建议保留）。
2. 跨期补抓上限是否固定为 3（可配）。
3. 若 500w 期号页临时不可达，是否允许用盈球期号兜底（建议不兜底，避免口径漂移）。
4. `goals` 长期缺失是否展示“基线占位”行（建议展示，减少前端空白感）。

---

## 18. 本文档对应交付物

1. 数据库迁移脚本（2-3 个）。
2. API 契约更新文档（含示例响应）。
3. Worker 运行脚本与部署说明。
4. E2E 测试计划与验收报告模板。

---

## 19. 开发执行勾选清单（可直接开工）

### 19.1 PR-1 勾选项（接口与状态基础）

- [ ] 新建迁移: `bd_other_odds_fetch_state` 表与索引。
- [ ] 新建迁移: `source_issue_tracking` 表与索引。
- [ ] 新建迁移: 数据源 `(source_type, issue_no)` 唯一约束。
- [ ] 新增模型: `backend/models/bd_other_odds_fetch_state.py`。
- [ ] 新增模型: `backend/models/source_issue_tracking.py`。
- [ ] 更新模型导出: `backend/models/__init__.py`。
- [ ] 新增 schema: completeness/task-status 响应模型。
- [ ] 改造 `GET /other-odds` 为只读缓存语义。
- [ ] 新增 `POST /other-odds/refresh`（入队返回 task_id）。
- [ ] 新增 `GET /other-odds/tasks/{task_id}`。
- [ ] 列表接口附带 `other_odds_ready` 等轻量状态。
- [ ] 前端详情页适配新字段，替换同步强刷逻辑。
- [ ] 单元测试补齐（completeness、接口契约、兼容字段）。
- [ ] 联调通过（前后端本地）。

### 19.2 PR-2 勾选项（队列化与预抓调度）

- [ ] 新增 service: `backend/services/odds_prefetch_service.py`。
- [ ] 新增 tasks: `backend/tasks/odds_prefetch_tasks.py`。
- [ ] 注册队列与任务: `backend/tasks/simple_celery.py`。
- [ ] 去重锁实现（match_id + tab）。
- [ ] 缺项抓取实现（仅抓 missing tab）。
- [ ] 重试退避策略按错误类型生效。
- [ ] 按域名限速器接入（500w/盈球/100球）。
- [ ] 请求抖动与固定请求画像策略接入。
- [ ] 熔断器接入并支持自动恢复。
- [ ] Playwright 常驻池化接入（非临时启动）。
- [ ] 导入后全量预抓触发接入。
- [ ] 列表首屏 N 场预热触发接入。
- [ ] 详情 urgent 入队触发接入。
- [ ] 定时窗口补抓接入（T-6h/T-2h/T-30m）。
- [ ] 新增 worker 启停脚本（Windows）。
- [ ] 压测与稳定性验证（队列堆积、并发、超时）。

### 19.3 PR-3 勾选项（500w期号发现 + 100球自动化）

- [ ] 新增 service: `backend/services/issue_discovery_service.py`。
- [ ] 新增 task: `issue_discovery` 定时任务。
- [ ] 解析 `https://trade.500.com/bjdc/` 最新期号。
- [ ] `latest_issue_no` 与 `last_processed_issue_no` 比对逻辑。
- [ ] 新期号自动触发 `500w/盈球/100球` 入队抓取。
- [ ] 100球 自动实例源创建（新ID）逻辑。
- [ ] 同期幂等（存在则不重复创建）。
- [ ] 跨期补抓策略与上限控制。
- [ ] 新期号流程与抓取流程联动压测（连续 3 个期号）。
- [ ] 数据源管理页展示自动实例与状态。
- [ ] E2E 验证 3 个连续期号自动流程。

### 19.4 发布前总勾选

- [ ] 关键配置项已加默认值并写入部署文档。
- [ ] 指标上报与告警规则已上线。
- [ ] 回滚开关已验证可生效。
- [ ] 手工回归与自动化回归通过。
- [ ] 生产发布窗口与值班人明确。

---

## 20. 最小改造按文件任务单（函数级，可直接开发）

适用范围：本章节对应“最小改造清单”，目标是先打通 headers/ip-pool 在当前北单+100球链路中的实际生效，不做全量重构。

### 20.1 P0-A 任务触发链路打通（先让绑定 headers 真能被用到）

- [ ] 文件：`frontend/src/api/crawlerTask.js`
- [ ] 函数：`triggerTask(id)`
- [ ] 改动：路由从 `/api/admin/crawler/tasks/${id}/trigger` 调整为 `/api/admin/tasks/${id}/trigger`。
- [ ] 验收：前端“立即执行”触发后，后端进入 `TaskSchedulerService.trigger_task`。

- [ ] 文件：`frontend/src/views/admin/crawler/TaskConsole.vue`
- [ ] 函数：调用 `triggerTask` 的事件处理逻辑（约第1000行附近）。
- [ ] 改动：适配新返回结构（success/message/data），失败提示不回退旧接口。

- [ ] 文件：`frontend/src/views/admin/crawler/TaskScheduler.vue`
- [ ] 函数：`triggerTask(scope.row.id)` 对应处理逻辑。
- [ ] 改动：同步适配新返回结构与状态刷新。

- [ ] 文件：`backend/api/v1/admin/task_management.py`
- [ ] 函数：`trigger_crawler_task(task_id, db)`
- [ ] 改动：保持此接口作为“真实执行入口”，确认调用 `TaskSchedulerService(db).trigger_task(...)` 后返回统一结构。
- [ ] 验收：触发后 `crawler_logs` 有执行记录，非仅 status 变化。

### 20.2 P0-B 抽取最小“请求上下文”服务（headers + proxy + timeout）

- [ ] 文件：`backend/services/crawler_request_context_service.py`（新建）
- [ ] 函数：`build_request_context(db, *, source_id: int, task_id: Optional[int], domain: Optional[str]) -> dict`
- [ ] 输出：`headers`, `used_header_ids`, `proxy_url`, `timeout`, `retry`。
- [ ] 规则：
- [ ] headers：复用 data_source/task 绑定优先级规则。
- [ ] proxy：从 `ip_pools` 中选 active 且最近可用的1个（最小实现可随机）。
- [ ] 兜底：无可用代理返回 `proxy_url=None`。

- [ ] 文件：`backend/services/task_scheduler_service.py`
- [ ] 函数：`_get_bound_headers`、`_record_header_usage`
- [ ] 改动：抽公共逻辑到新service后，这里改为调用公共service，避免双份实现。
- [ ] 验收：header usage/success 统计口径不变。

### 20.3 P0-C 北单赔率抓取链路接入上下文（lottery_schedule）

- [ ] 文件：`backend/api/v1/admin/lottery_schedule.py`
- [ ] 函数：`_fetch_yingqiu_sportdata_json`
- [ ] 改动：
- [ ] 在当前固定headers基础上 merge 绑定headers（绑定值优先）。
- [ ] 支持 `proxy` 参数注入 aiohttp 请求。
- [ ] 失败策略：代理失败后直连再试1次（受开关控制）。

- [ ] 函数：`_fetch_yingqiu_json_direct`
- [ ] 改动：同上（headers merge + proxy + failover）。

- [ ] 函数：`_resolve_yingqiu_league_match_id_direct`
- [ ] 改动：至少接入 headers merge。

- [ ] 函数：`_fetch_and_cache_other_odds_for_match`
- [ ] 改动：
- [ ] 透传 `source_id/task_id` 或最小上下文标识到抓取函数。
- [ ] 记录本次抓取 `used_header_ids/proxy_used/fallback_reason` 到日志字段。

- [ ] 验收：
- [ ] 打开详情触发补抓时日志可见 header/proxy 使用信息。
- [ ] eu/asia/goals 成功率不下降，失败时可自动回退直连。

### 20.4 P0-D 100球“获取”链路接入上下文（data_source_100qiu）

- [ ] 文件：`backend/api/v1/data_source_100qiu.py`
- [ ] 函数：`fetch_100qiu_data(source_id, compare_update, db)`
- [ ] 改动：
- [ ] 将 `_NO_PROXY_SESSION.get(...)` 改为“上下文驱动请求”。
- [ ] 支持绑定headers注入。
- [ ] 支持代理请求与“代理失败后直连1次”。

- [ ] 函数：连接测试接口（test相关函数）
- [ ] 改动：与 fetch 使用同一请求上下文构建逻辑，避免“测试可用/抓取不可用”不一致。

- [ ] 配置改动：
- [ ] 保留 `NO_PROXY` 行为，但改成开关控制，不再强制全局关闭代理。

- [ ] 验收：
- [ ] 管理页点击“获取”后，header usage 计数上涨。
- [ ] 开启代理可走代理；关闭开关后恢复直连。

### 20.5 P0-E 开关与配置（灰度上线最小集）

- [ ] 文件：`backend/config.py`（或现有配置集中定义文件）
- [ ] 新增：
- [ ] `CRAWLER_USE_BOUND_HEADERS`（default: true）
- [ ] `CRAWLER_USE_IP_POOL`（default: false）
- [ ] `CRAWLER_PROXY_FAILOVER_DIRECT`（default: true）

- [ ] 文件：`backend/.env.example`（若存在）
- [ ] 增补上述3个开关示例值与说明。

- [ ] 验收：
- [ ] 开关关闭时行为与当前版本一致。
- [ ] 分阶段开启不影响现有接口契约。

### 20.6 P0-F 监控与回归（最小闭环）

- [ ] 文件：`backend/api/v1/admin/lottery_schedule.py`
- [ ] 改动：在关键抓取失败/回退分支补日志字段：`match_id`, `source_id`, `used_header_ids`, `proxy_used`, `retry_count`, `fallback_reason`。

- [ ] 文件：`backend/api/v1/data_source_100qiu.py`
- [ ] 改动：在 fetch/test 结果日志中补同类字段。

- [ ] 回归用例（手工）：
- [ ] 北单详情：首次打开、补抓、强制刷新3条路径。
- [ ] 100球：连接测试、点击获取、失败重试3条路径。
- [ ] headers绑定生效验证：`usage_count` 变化。
- [ ] ip-pool生效验证：开启/关闭开关对比。

### 20.7 本轮明确不做（防止范围失控）

- [ ] 不做全链路队列系统重构。
- [ ] 不做复杂代理评分与自动淘汰。
- [ ] 不做Playwright池化重构（保持现有兜底策略）。

### 20.8 文档任务（本次迭代必须完成）

- [ ] 文件：`docs/BEIDAN_OTHER_ODDS_AND_MULTI_SOURCE_AUTO_FETCH_IMPLEMENTATION_CHECKLIST.md`
- [ ] 要求：同步每个P0子项状态（未开始/进行中/已完成），每次合并PR后更新。

- [ ] 文件：`docs/CRAWLER_HEADERS_IPPOOL_ROLLOUT.md`（新建）
- [ ] 要求：记录灰度开关顺序、回滚步骤、观测指标与判定标准。

- [ ] 文件：`docs/CRAWLER_REQUEST_CONTEXT_DESIGN.md`（新建）
- [ ] 要求：记录headers/proxy优先级、failover规则、已知限制。

- [ ] 文件：`docs/CHANGELOG.md`（若存在）
- [ ] 要求：增加“爬虫headers/ip-pool接入”变更条目与上线日期。

---

## 21. 池容量自动达标规划（IP池 + Headers池）

### 21.1 目标与原则

1. 目标：确保爬虫任务在任何时段都满足“可用IP数”和“可用Headers数”最低要求，避免因池容量不足导致抓取超时、403/429上升、详情补抓变慢。
2. 原则：先保稳定，再提并发；先自动补齐，再自动优化；先灰度告警，再自动执行。
3. 范围：覆盖 `500w`、`yingqiu`、`100qiu` 三个来源及公共应急池。

### 21.2 容量基线（初始建议）

| 目标域名/来源 | 建议并发 | 最小活跃IP | 备用IP | 最小可用Headers |
|---|---:|---:|---:|---:|
| 500w | 2 | 8 | 4 | 24 |
| yingqiu | 2 | 12 | 6 | 36 |
| 100qiu | 1 | 6 | 3 | 18 |
| 公共应急池 | - | 8 | 0 | 20 |

容量约束规则：

1. 候选池总量 >= 活跃池目标的 3 倍。
2. 每域名 Headers 数 >= 活跃IP数 * 3。
3. 每域名至少 5 类 User-Agent 家族，避免头部特征单一。

### 21.3 自动达标机制（Reconciler）

调节器（reconciler）任务：每 1 分钟运行一次。

执行流程：

1. 读取当前池状态：`active_ip_count`、`standby_ip_count`、`active_header_count`、错误率、最近成功率。
2. 与容量基线比对，计算缺口。
3. 自动下发补齐任务：
   1. `ip_pool.replenish`（补IP）
   2. `headers_pool.replenish`（补Headers）
   3. `headers_binding.reconcile`（重绑定）
4. 若超配，执行降配：降级到备用池或进入退休队列。

### 21.4 IP池生命周期与策略

状态机：`new -> testing -> active -> cooling -> banned/retired`

策略：

1. 健康检查频率：活跃池每 3 分钟，备用池每 15 分钟。
2. 晋升条件：连续成功 >= 3，延迟低于阈值，近15分钟失败率低于阈值。
3. 降级条件：超时/403/429 连续触发达到阈值。
4. 冷却策略：进入 `cooling` 后暂停使用，冷却期结束再回测。
5. 禁用策略：多次冷却后仍失败，进入 `banned`；人工或定时复检后再决定是否恢复。

### 21.5 Headers池生命周期与策略

状态机：`new -> testing -> active -> cooling -> retired`

策略：

1. 自动生成：按域名模板批量生成 headers 组（UA/Accept-Language/Referer/Origin）。
2. 质量评分：按成功率、403/429率、超时率综合评分。
3. 自动绑定：每数据源保持“主headers + 备headers”最小绑定数。
4. 自动切换：主headers失败达到阈值时切换到备headers。
5. 自动回收：长期低分 headers 进入 `retired`，不再参与调度。

### 21.6 请求调度防封策略（与池联动）

1. 每域名限制并发与QPS（沿用当前建议：500w=2，yingqiu=2，100qiu=1）。
2. 请求抖动窗口：150ms ~ 600ms。
3. 同一 `IP + Header` 组合设置最小复用间隔，避免短时重复命中风控。
4. 分类型退避：`timeout`、`429`、`403`、`sign_error` 分开退避。
5. 熔断降频：域名失败率超过阈值时自动降频，优先保障详情urgent任务。

### 21.7 自动巡检与达标判定

巡检任务：每 5 分钟运行一次，输出健康快照。

达标判定：

1. 连续15分钟低于最小活跃池，触发告警。
2. 连续10分钟 403/429 超阈值，触发降频与告警。
3. 每小时生成池健康报告：可用率、替换率、平均寿命、成功率。
4. 目标对齐：详情打开后20秒内补齐率 > 90%。

### 21.8 配置项建议（新增）

1. `IP_POOL_TARGET_500W_ACTIVE=8`
2. `IP_POOL_TARGET_YINGQIU_ACTIVE=12`
3. `IP_POOL_TARGET_100QIU_ACTIVE=6`
4. `IP_POOL_TARGET_EMERGENCY_ACTIVE=8`
5. `IP_POOL_STANDBY_RATIO=0.5`
6. `HEADERS_POOL_MIN_PER_IP=3`
7. `POOL_RECONCILE_INTERVAL_SECONDS=60`
8. `POOL_HEALTH_CHECK_ACTIVE_SECONDS=180`
9. `POOL_HEALTH_CHECK_STANDBY_SECONDS=900`
10. `POOL_FAILOVER_TO_DIRECT=true`

### 21.9 灰度步骤（建议）

1. 灰度阶段1：只巡检+告警，不自动补齐。
2. 灰度阶段2：开启自动补IP，关闭自动切换Headers。
3. 灰度阶段3：开启自动补Headers与自动重绑定。
4. 灰度阶段4：开启熔断降频与全自动达标闭环。

### 21.10 文档同步任务

1. 将本章节容量基线同步到运行手册（运维值班手册）。
2. 将配置项同步到 `.env.example` 与部署文档。
3. 每次调整阈值后在本章节更新“版本号 + 日期 + 调整原因”。

---

## 22. 第21章执行任务清单（按迭代拆分，可直接排期）

说明：本章节是第21章“池容量自动达标规划”的实施拆解，按最小闭环优先，逐步开启自动化动作。

### 22.1 迭代S1：观测与容量基线落库（只观测，不自动动作）

目标：先看清楚当前池健康与缺口，不触发自动补齐，避免误操作。

- [x] 文件：`backend/config.py`
- [x] 任务：新增第21章配置项（目标活跃IP、headers最小比、巡检周期）。
- [x] 验收：服务启动后可读取配置，日志打印生效值。

- [x] 文件：`backend/models/ip_pool.py`
- [x] 任务：补齐池状态字段映射（active/standby/cooling/banned）与索引需求评估。
- [x] 验收：可按状态快速统计数量。

- [x] 文件：`backend/models/headers.py`
- [x] 任务：确认可用字段支持质量评分（usage_count/success_count/last_used）。
- [x] 验收：可计算每域名header成功率。

- [x] 文件：`backend/api/v1/ip_pool_adapter.py`
- [x] 任务：增加“容量视图”响应字段（active_count/standby_count/target_gap）。
- [x] 验收：IP池页面可显示“当前 vs 目标”。

- [x] 文件：`backend/api/v1/admin/headers_management.py`
- [x] 任务：增加“域名维度统计”接口字段（active_headers、low_quality_headers）。
- [x] 验收：Headers页面可显示每域名可用头数量。

- [x] 文件：`docs/`
- [x] 任务：新增巡检报表模板（每5分钟快照、每小时汇总）。
- [x] 验收：有固定报表字段与阈值。

### 22.2 迭代S2：Reconciler框架上线（可告警，不补齐）

目标：实现自动对比目标与现状，先告警不执行。

- [x] 文件：`backend/services/pool_reconciler_service.py`（新建）
- [x] 任务：实现 `reconcile(dry_run=True)`，输出每域名缺口计划。
- [x] 输出：`ip_gap`、`header_gap`、`risk_level`、`recommended_actions`。
- [x] 验收：dry_run日志可稳定输出，未对库数据做修改。

- [x] 文件：`backend/tasks/simple_celery.py`
- [x] 任务：注册 `pool.reconcile` 定时任务（默认dry_run）。
- [x] 验收：任务按周期执行，队列可见。

- [x] 文件：`backend/tasks/`（新建 `pool_reconcile_tasks.py`）
- [x] 任务：封装Celery任务入口，支持 `dry_run` 开关。
- [x] 验收：手工触发和定时触发结果一致。

- [x] 文件：`docs/CRAWLER_HEADERS_IPPOOL_ROLLOUT.md`（新建）
- [x] 任务：记录S2阶段只告警策略与回滚方式。
- [x] 验收：值班人员可按文档执行。

### 22.3 迭代S3：IP池自动补齐闭环

目标：当活跃IP低于阈值时，自动补IP并晋升到活跃池。

- [x] 文件：`backend/services/pool_reconciler_service.py`
- [x] 任务：实现 `ip_pool.replenish` 动作编排（从来源抓取 -> 入库 -> 测试 -> 晋升）。
- [x] 验收：缺口出现时，IP数量可自动回升到目标区间。

- [x] 文件：`backend/tasks/ip_pool_refresh.py`
- [x] 任务：支持按“目标缺口”动态抓取页数/数量，不再固定参数。
- [x] 验收：补齐速度与缺口大小匹配。

- [x] 文件：`backend/api/v1/ip_pool_adapter.py`
- [x] 任务：补充批量健康检查与状态迁移接口（active/standby/cooling）。
- [x] 验收：可通过接口看到IP状态机流转。

- [x] 文件：`backend/services/task_scheduler_service.py`
- [x] 任务：新增“无可用IP时回退直连”策略开关判定。
- [x] 验收：代理池异常不会导致任务整体阻塞。

### 22.4 迭代S4：Headers池自动补齐与自动绑定

目标：保证每域名 headers 数量与质量达标，并自动绑定到数据源/任务。

- [x] 文件：`backend/services/headers_pool_service.py`（新建）
- [x] 任务：实现 headers 质量评分、低分回收、缺口补齐（模板生成或导入）。
- [x] 验收：每域名 `active_headers >= active_ip * 3`。

- [x] 文件：`backend/api/v1/admin/headers_management.py`
- [x] 任务：新增“批量自动绑定”接口（按域名、优先级）。
- [x] 验收：可自动为数据源补齐主/备headers绑定。

- [x] 文件：`backend/models/data_source_headers.py`
- [x] 任务：校验唯一性与优先级策略，避免重复绑定。
- [x] 验收：同一 data_source + header 不重复。

- [x] 文件：`backend/services/task_scheduler_service.py`
- [x] 任务：绑定缺失时自动降级使用默认headers并记录告警。
- [x] 验收：任务不中断，日志可追踪。

### 22.5 迭代S5：调度联动与防封策略闭环

目标：池容量达标与请求调度联动，稳定控制403/429。

- [x] 文件：`backend/services/task_scheduler_service.py`
- [x] 任务：接入 `IP + Header` 组合复用间隔、失败分型退避、域名熔断。
- [x] 验收：429/403在高峰期可控，失败后自动降频。

- [x] 文件：`backend/api/v1/admin/lottery_schedule.py`
- [x] 任务：北单详情补抓链路记录 `proxy_used/header_ids/fallback_reason`。
- [x] 验收：可审计每次抓取走向。

- [x] 文件：`backend/api/v1/data_source_100qiu.py`
- [x] 任务：100球抓取链路接入同样日志与failover策略。
- [x] 验收：100球“获取”稳定性提升，失败可回退。

### 22.6 前端配套任务（可视化与运维可用性）

- [x] 文件：`frontend/src/views/admin/crawler/IpPoolManagement.vue`
- [x] 任务：新增“目标值/当前值/缺口”展示与状态色标。
- [x] 验收：可直接看到是否达标。

- [x] 文件：`frontend/src/views/admin/crawler/HeadersManagement.vue`
- [x] 任务：新增域名维度“可用headers/低质量headers/绑定覆盖率”看板。
- [x] 验收：能定位是哪类headers不足。

- [x] 文件：`frontend/src/views/admin/crawler/DataSourceManagement.vue`
- [x] 任务：新增数据源级“池健康摘要”（IP可用、headers可用、降级状态）。
- [x] 验收：业务侧能判断是否需要手动干预。

### 22.7 统一验收清单（S1-S5完成后）

- [ ] 连续24小时：所有域名活跃IP不低于目标值。
- [ ] 连续24小时：所有域名可用headers不低于目标值。
- [ ] 详情补抓20秒补齐率 > 90%。
- [ ] 429/403告警次数较改造前下降（目标下降30%以上）。
- [ ] 出现上游波动时，系统能自动降频并自动恢复。

### 22.8 排期建议（最小可落地）

1. 第1周：S1 + S2（只观测、可告警）。
2. 第2周：S3（IP自动补齐）。
3. 第3周：S4（Headers自动补齐与绑定）。
4. 第4周：S5（调度联动与防封闭环）+ 全量回归。

### 22.9 文档更新责任

- [x] 每个迭代结束后，更新本文件对应勾选项。
- [ ] 每个阈值调整后，更新第21章“容量基线”和第22章“验收结果”。
- [x] 每次生产变更后，在 `docs/CHANGELOG.md` 追加记录。

### 22.10 每周PR清单（PR-1/2/3）+ 验收用例

#### Week-1 / PR-1：容量观测与Reconciler告警闭环（不自动补齐）

范围：S1 + S2

改动清单：

1. `backend/config.py`
   - 增加池目标与巡检配置项（仅生效于观测与告警）。
2. `backend/services/pool_reconciler_service.py`（新建）
   - 支持 `reconcile(dry_run=True)`。
3. `backend/tasks/pool_reconcile_tasks.py`（新建）
   - 定时触发 dry-run 调节任务。
4. `backend/tasks/simple_celery.py`
   - 注册 `pool.reconcile` 任务。
5. `backend/api/v1/ip_pool_adapter.py`
   - 返回容量视图字段（当前值、目标值、缺口）。
6. `backend/api/v1/admin/headers_management.py`
   - 返回域名维度 headers 可用统计字段。

PR-1 验收用例：

1. 手动触发 `pool.reconcile`，确认仅输出建议动作，不写库。
2. 定时任务每分钟执行一次，队列与日志可见。
3. IP池页面可显示 `active/standby/target_gap`。
4. Headers页面可显示域名级可用数量与低质量数量。
5. 关闭开关后，系统行为与改造前一致。

#### Week-2 / PR-2：IP自动补齐与失败回退直连

范围：S3

改动清单：

1. `backend/services/pool_reconciler_service.py`
   - 从 dry-run 升级为可执行 `ip_pool.replenish`。
2. `backend/tasks/ip_pool_refresh.py`
   - 根据缺口动态补抓数量。
3. `backend/api/v1/ip_pool_adapter.py`
   - 批量健康检查与状态迁移接口完善。
4. `backend/services/task_scheduler_service.py`
   - 无可用代理时支持自动回退直连（开关控制）。

PR-2 验收用例：

1. 人为下线部分IP后，系统可在阈值内自动补齐。
2. IP状态可按 `testing -> active -> cooling` 流转。
3. 模拟代理池不可用，任务可自动直连完成，不阻塞。
4. 连续24小时内活跃IP不低于基线目标。

#### Week-3 / PR-3：Headers自动补齐/自动绑定 + 调度联动收口

范围：S4 + S5（最小收口）

改动清单：

1. `backend/services/headers_pool_service.py`（新建）
   - 实现 headers 评分、补齐、回收。
2. `backend/api/v1/admin/headers_management.py`
   - 增加按域名批量自动绑定接口。
3. `backend/models/data_source_headers.py`
   - 校验去重与优先级一致性。
4. `backend/services/task_scheduler_service.py`
   - 接入 `IP+Header` 组合复用间隔、分型退避、域名降频。
5. `backend/api/v1/admin/lottery_schedule.py`
   - 记录北单补抓链路的 `proxy_used/header_ids/fallback_reason`。
6. `backend/api/v1/data_source_100qiu.py`
   - 记录100球抓取链路同类观测字段并启用failover。
7. `frontend/src/views/admin/crawler/IpPoolManagement.vue`
   - 展示目标值/当前值/缺口。
8. `frontend/src/views/admin/crawler/HeadersManagement.vue`
   - 展示域名维度可用率与绑定覆盖率。
9. `frontend/src/views/admin/crawler/DataSourceManagement.vue`
   - 展示数据源级池健康摘要。

PR-3 验收用例：

1. 每域名 `active_headers >= active_ip * 3` 持续达标。
2. 详情补抓20秒补齐率 > 90%。
3. 429/403 告警频次较基线下降（目标 >= 30%）。
4. 上游波动场景下自动降频，恢复后自动回升。
5. 北单与100球链路日志可审计每次请求的代理与headers使用情况。

#### 里程碑交付判定（PR-1/2/3完成后）

1. 周报中连续3周输出容量达标率与告警趋势。
2. 自动补齐触发次数与人工介入次数明显下降。
3. 形成稳定发布节奏：先 dry-run，再自动化，再收口优化。
