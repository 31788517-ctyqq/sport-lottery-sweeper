# 500w 期号驱动 100qiu 全自动链路无代码实施清单（按当前项目结构）

更新时间：2026-03-03  
适用范围：`/admin/data-source/config`、`/api/v1/admin/sources`、`/api/v1/data-source-100qiu/*`、当前 Celery/任务体系

## 1. 目标与现状结论

### 1.1 目标（你要的四点）

1. 自动从 `https://trade.500.com/bjdc/` 识别最新期号。  
2. 仅当发现“新期号”时，自动触发 `https://m.100qiu.com/api/dcListBasic?dateTime=xxxxx` 抓取。  
3. 抓取成功后，自动在数据源管理卡片列表回填一条该期号记录。  
4. 全流程无需人工点击“创建100球数据源/获取”。

### 1.2 当前实现状态（基于现有代码）

1. 已有：`/api/v1/data-source-100qiu/{id}/test`、`/fetch` 支持按 500w 期号候选兜底。  
2. 已有：`/api/v1/admin/sources` 数据源 CRUD 可承载卡片展示。  
3. 未闭环：缺少“定时发现新期号 -> 比对 -> 自动抓取 -> 自动回填”的独立调度链路。  
4. 现状仍以页面手动触发为主（`DataSourceManagement.vue`）。

结论：目前是“半自动能力 + 人工触发”，不是“完全自动闭环”。

---

## 2. 表结构实施清单（无代码设计）

## 2.1 复用现有表（不改或小改）

1. `data_sources`：继续作为“数据源卡片主表”。  
2. `crawler_tasks`：承载周期任务定义。  
3. `crawler_task_logs`：承载执行日志与耗时、失败信息。  
4. `async_tasks`：承载异步任务状态查询（可选）。

## 2.2 新增表（建议最小新增 2 张）

### A. `source_issue_state`（每个 source_type 一行）

用途：记录“最新发现期号”和“已成功抓取期号”。

字段建议：

1. `id`  
2. `source_type`（`500w_bjdc` / `100qiu`）唯一  
3. `latest_discovered_issue`  
4. `last_success_issue`  
5. `last_discovered_at`  
6. `last_success_at`  
7. `last_error_message`  
8. `updated_at`

索引建议：

1. `uniq_source_type(source_type)`  
2. `idx_latest_discovered_issue(latest_discovered_issue)`

### B. `source_issue_fetch_runs`（每期每源一行）

用途：记录“某源某期”是否执行过、是否成功，做幂等与追溯。

字段建议：

1. `id`  
2. `source_type`（`100qiu`）  
3. `issue_no`  
4. `status`（`pending/running/success/failed/skipped`）  
5. `trigger_type`（`scheduler/manual/retry`）  
6. `request_url`  
7. `response_code`  
8. `records_count`  
9. `error_message`  
10. `started_at`  
11. `finished_at`  
12. `created_at`

索引建议：

1. `uniq_source_issue(source_type, issue_no)`（核心幂等）  
2. `idx_status_created(status, created_at)`

---

## 3. 任务流实施清单（调度与执行）

## 3.1 任务拆分

1. `issue_discovery_500w`：读取 500w 当前期号。  
2. `issue_compare_and_enqueue_100qiu`：与 `source_issue_state.last_success_issue` 比对。  
3. `fetch_100qiu_by_issue`：调用 100qiu 接口抓数、入库。  
4. `backfill_data_source_card`：在 `data_sources` 回填/更新该期号卡片。  
5. `issue_retry_compensation`：失败重试与补偿。

## 3.2 调度频率（按你“2-3天更新，不频繁抓”的要求）

1. 常态：每 3 小时执行一次 `issue_discovery_500w`。  
2. 开奖窗口（可配置）：每天 10:00-23:00，每 30 分钟执行一次。  
3. 失败重试：5 分钟、30 分钟、2 小时三级退避，最多 3 次。

## 3.3 幂等与去重规则

1. 同一 `source_type + issue_no` 只能有一条运行记录（数据库唯一约束）。  
2. 任务启动前先查运行表：`running/success` 则跳过。  
3. 回填卡片时使用 `source_id` 或 `issue_no` 唯一键更新，不重复造脏数据。

## 3.4 失败处理

1. 500w 解析失败：仅记录告警，不触发 100qiu。  
2. 100qiu 超时/非 JSON：写失败日志、进入重试队列。  
3. 连续失败超阈值：任务状态置 `degraded`，页面显式提示“自动链路异常”。

---

## 4. 接口契约实施清单

## 4.1 保留并统一的现有接口

1. `GET /api/v1/admin/sources`（数据源列表）  
2. `POST /api/v1/admin/sources`（创建数据源）  
3. `PUT /api/v1/admin/sources/{id}`（更新）  
4. `POST /api/v1/data-source-100qiu/{id}/fetch`（单次抓取）

说明：前端统一使用 `/api/v1/admin/*`，避免 `/api/admin/*` 与迁移中间层混用导致 404/405/422。

## 4.2 新增接口（建议）

1. `GET /api/v1/admin/source-sync/status`
   - 返回：500w 最新期号、100qiu 最后成功期号、链路状态、最近错误。  
2. `POST /api/v1/admin/source-sync/run-now`
   - 手动触发一次全链路（应急入口，不作为日常流程）。  
3. `GET /api/v1/admin/source-sync/runs`
   - 返回期号运行明细，用于页面“执行记录”抽屉。

## 4.3 接口字段标准化（关键）

统一返回结构：

1. `success`  
2. `message`  
3. `data`  
4. `error_code`（可空）  
5. `trace_id`（可空）

---

## 5. 页面字段实施清单（`/admin/data-source/config`）

## 5.1 数据源卡片新增字段

1. `source_type`（500w/100qiu）  
2. `latest_issue_no`（最新发现期号）  
3. `last_success_issue_no`（最后成功期号）  
4. `sync_status`（`idle/running/success/failed/degraded`）  
5. `last_sync_at`  
6. `next_sync_at`  
7. `records_count`（本期抓取条数）  
8. `last_error`（摘要）

## 5.2 页面交互调整

1. “创建100球数据源”按钮降级为管理员应急入口。  
2. “获取”按钮降级为“立即重试本期”（默认隐藏在更多操作）。  
3. 列表顶部新增“自动链路状态条”：显示 500w -> 100qiu 当前健康状态。  
4. 新增“期号运行记录”抽屉，展示最近 20 次执行。

---

## 6. 灰度实施步骤（可回滚）

## 6.1 Phase-0（观测，不自动执行）

1. 只跑 `issue_discovery_500w`，不触发 100qiu。  
2. 验证 500w 期号识别准确率与稳定性。  
3. 观测 3-7 天，确认无误再进入下一阶段。

## 6.2 Phase-1（自动抓取，不自动建卡）

1. 发现新期号后自动抓取 100qiu。  
2. 仅写运行表与日志，不写 `data_sources` 新卡片。  
3. 观测失败率、重试成功率。

## 6.3 Phase-2（自动抓取 + 自动回填卡片）

1. 开启 `backfill_data_source_card`。  
2. 页面可看到新期号记录与状态。  
3. 手动“创建/获取”仍保留应急。

## 6.4 Phase-3（默认全自动）

1. 隐藏主流程手动入口，仅保留管理员二级入口。  
2. 将运营 SOP 更新为“只监控，不手工触发”。  
3. 发布后 48 小时重点巡检。

## 6.5 回滚策略

1. 一键关闭自动触发开关，仅保留手动模式。  
2. 保留日志与运行记录，问题排查后可无损恢复。  
3. 回滚不删数据，只停自动任务。

---

## 7. 验收标准（上线门槛）

1. 新期号出现后 30 分钟内自动发起抓取（窗口期）。  
2. 自动链路成功率 >= 95%（按最近 30 次运行）。  
3. 失败重试后最终成功率 >= 98%。  
4. 数据源管理页可准确显示“最新期号/最后成功期号/同步状态”。  
5. 无需人工“创建100球数据源 + 点击获取”即可持续更新。

---

## 8. 执行清单（可直接分工）

1. 表设计评审：确认新增 2 张表字段与索引。  
2. 任务编排评审：确认 5 个任务的触发关系与退避。  
3. 接口评审：确认 3 个新增接口及返回结构。  
4. 页面评审：确认卡片字段与状态条展示。  
5. 灰度评审：确认 Phase-0 到 Phase-3 开关与回滚手册。  
6. 上线评审：确认监控项、告警阈值与值班响应。

---

## 9. 备注（与现有工程对齐）

1. 不推翻现有 `data_source_100qiu` 接口，作为执行器复用。  
2. 不推翻现有 `data_sources/crawler_tasks/crawler_task_logs`，仅增补状态与运行追踪。  
3. 先做“自动发现+自动抓取+自动回填”主链路，再做页面体验增强。

