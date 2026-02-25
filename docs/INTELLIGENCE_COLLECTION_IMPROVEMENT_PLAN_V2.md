# 情报采集系统改进方案 v2.1（实施版）

> 页面：`http://localhost:3000/admin/intelligence/collection`  
> 文档类型：实施版（已实现 / 待实现 / 阻塞项）  
> 更新日期：2026-02-20  
> 目标：先跑通、再提质、最后稳态上线

---

## 1. 方案结论（执行摘要）

- 当前方案整体可行，评估为 `中高可行（7.5/10）`。
- 基础能力已具备：参数配置、来源健康、候选调试、回放调试、质量字段展示、缓存机制已上线。
- 仍存在发布阻塞：任务状态误判、计划任务未真正调度、超时策略不匹配、日志可诊断性不足。
- 建议路线：`P0（先稳） -> P1（再准） -> P2（可运营）`。

---

## 2. 已实现（可直接复用）

## 2.1 后端已实现能力

- 统一采集接口基座：`/api/v1/admin/intelligence/collection/*`
- 时间窗配置：`GET/PUT /settings/time-window`
- 网络配置：`GET/PUT /settings/network`
- 来源规则配置：`GET/PUT /settings/source-rules`
- 质量阈值配置：`GET/PUT /settings/quality-thresholds`
- 别名字典配置：`GET/PUT /settings/alias-dictionary`
- 来源健康统计：`GET /sources/health`
- 候选调试：`POST /debug/match-candidates`
- 回放调试：`POST /debug/replay`
- 结果查询支持质量字段：`GET /matches/{match_id}/items`  
  返回 `quality_score / quality_status / quality_pass_reason / quality_block_reason / source_parser / article_url`。
- 任务轻量轮询：`GET /tasks/{task_id}?lightweight=true`
- 任务重试：`POST /tasks/{task_id}/retry`
- 子任务进度：`GET /tasks/{task_id}/subtasks`
- 任务日志查询：`GET /tasks/{task_id}/logs`
- 网络层支持：重试、退避、熔断、`trust_env` 开关、来源级超时。
- 专用解析器已覆盖重点来源：`500w / ttyingqiu / weibo / tencent / sina`（含部分二跳能力）。

## 2.2 前端已实现能力

- 采集页已支持：
  - 任务创建、重试、取消、状态跟踪
  - 赛程筛选与任务列表
  - 结果列表与详情查看区
  - 质量字段展示（质量分、采纳原因、过滤原因）
  - 候选调试弹窗、回放调试弹窗
  - 参数设置弹窗（network/source-rules/quality/alias）
  - 来源健康看板
  - 结果缓存与强制刷新机制
- 已接入回归脚本：
  - `scripts/run-intelligence-regression.bat`
  - `scripts/run-all-tests.bat` 中已串联情报模块 3 条 Playwright 用例。

---

## 3. 阻塞项（发布前必须修）

> 说明：以下项不解决，会持续导致“页面超时、成功误报、结果质量不稳定”。

| 编号 | 阻塞项 | 当前现象 | 影响 | 必修动作 |
|---|---|---|---|---|
| B1 | 任务最终状态误判 | 任务执行后直接置 `success` | 用户误判成功，告警失真 | 引入任务最终状态收敛：`success/partial/failed` |
| B2 | 计划任务未真正调度 | `scheduled` 仅记录 queued | 定时采集不可依赖 | 接入 worker 调度（Celery/RQ）并落地执行 |
| B3 | 超时策略冲突 | 前端默认 15s；采集请求常超时 | 频繁 timeout 误报 | 前端采集链路单独超时策略 + 轮询退避 |
| B4 | 默认源超时偏低 | 网络默认超时基线过小 | 外站抓取失败率高 | 提升默认超时并按来源配置 |
| B5 | 日志可诊断性不足 | 配置快照日志占比高 | 排障慢 | 增加失败摘要接口，弱化冗余 debug |
| B6 | 质量字段解析耦合 raw | 依赖 `content_raw` 正则抽取 | 易受文本格式波动影响 | 质量字段结构化入库，raw 仅保留快照 |
| B7 | 文档/API口径不一致 | 文档有旧路径 | 联调误用接口 | 全文统一为 `/api/v1/admin/intelligence/collection/*` |
| B8 | 存在重复实现文件 | 管理端与非管理端并存 | 后续易分叉 | 收敛单一主实现并标注弃用路径 |

---

## 4. 待实现（按优先级）

## 4.1 P0（先稳，1周）

### P0-1 任务状态机收敛
- 目标：任务状态真实反映执行结果。
- 动作：
  - 引入 `success_rate` 计算逻辑。
  - 统一终态为：`success / partial / failed / cancelled`。
  - 前端状态筛选与展示同步支持 `partial`。
- 验收：
  - 全失败任务不再显示 success。
  - 任务详情显示成功率百分比。

### P0-2 真正异步任务执行
- 目标：创建接口快速返回、执行可持续。
- 动作：
  - `POST /tasks` 改为入队返回 `accepted + task_id`。
  - Worker 执行采集主逻辑。
  - `scheduled` 按 offset 或 cron 被 worker 拉起执行。
- 验收：
  - 接口返回 < 2s。
  - 服务重启后队列任务可恢复/重试。

### P0-3 统一超时与重试策略
- 目标：降低超时误报，提高任务稳定性。
- 动作：
  - 前端全局 15s 保留，但采集链路接口独立配置（创建/重试/轮询/调试）。
  - 轮询改指数退避（例如 2.5s -> 4s -> 6s）。
  - 来源默认 timeout 上调，保留来源级覆盖。
- 验收：
  - 任务创建和重试超时报错率明显下降。
  - 轮询日志不再刷屏 timeout。

### P0-4 失败摘要与诊断提效
- 目标：3分钟内定位失败主因。
- 动作：
  - 新增 `GET /tasks/{task_id}/failure-summary`。
  - 输出维度：`top_reasons / source_failures / sample_logs`。
  - 任务详情弹窗接入失败摘要卡片。
- 验收：
  - 失败任务可直接看到 Top 原因与来源分布。

## 4.2 P1（再准，1-2周）

### P1-1 质量字段结构化存储
- 目标：摆脱 `content_raw` 反解析依赖。
- 动作：
  - `intel_collection_items` 新增结构化字段：  
    `quality_status, quality_score, quality_pass_reason, quality_block_reason, source_parser, article_url, match_hit_terms_json`。
  - 写入时直接落库，读接口优先读结构化字段。
- 验收：
  - 前端展示无需再正则解析 raw 也可工作。

### P1-2 解析器质量收敛
- 目标：提升“文章页命中率 + 比赛相关性”。
- 动作：
  - 专用解析器继续增强（重点来源）。
  - 固定样例回放集 + 每次改动自动对比报告。
  - 黑名单与降权策略参数化、可热更新。
- 验收：
  - 详情页占比、accepted率持续提升，回放不回退。

### P1-3 时间窗和别名匹配精修
- 目标：降低误命中。
- 动作：
  - 时间窗硬门槛与软门槛并存（严格模式可切换）。
  - 联赛/球队别名字典继续扩展（中英、简称、繁简）。
- 验收：
  - `quality_block_reason` 中“时间窗不符/关键词不符”可解释比例 > 95%。

## 4.3 P2（可运营，2周）

### P2-1 实时进度推送（建议先 SSE）
- 目标：减少轮询压力和等待焦虑。
- 动作：
  - 先上 SSE 通道，后续再评估 WebSocket。
  - 进度事件包含：阶段、完成数、失败数、当前 source/match。
- 验收：
  - 前端可实时看到阶段推进，手动刷新次数下降。

### P2-2 质量趋势看板
- 目标：支持运营按周调参。
- 动作：
  - 新增趋势接口（天维度 success/accepted/blocked/avg_quality）。
  - 前端 ECharts 可视化。
- 验收：
  - 可按来源与日期区间查看趋势变化。

### P2-3 推送收敛策略
- 目标：少而准地推送。
- 动作：
  - `push-preview` 支持 `top_n/min_score/include_blocked`。
  - 推送模板标准化（摘要/证据/风险/置信度）。
- 验收：
  - 每场推送条目可控，阅读成本显著下降。

---

## 5. 接口口径（实施版）

## 5.1 已有接口（继续沿用）

- `GET /api/v1/admin/intelligence/collection/sources`
- `GET /api/v1/admin/intelligence/collection/sources/health`
- `GET/PUT /api/v1/admin/intelligence/collection/settings/time-window`
- `GET/PUT /api/v1/admin/intelligence/collection/settings/network`
- `GET/PUT /api/v1/admin/intelligence/collection/settings/source-rules`
- `GET/PUT /api/v1/admin/intelligence/collection/settings/quality-thresholds`
- `GET/PUT /api/v1/admin/intelligence/collection/settings/alias-dictionary`
- `GET /api/v1/admin/intelligence/collection/matches`
- `POST /api/v1/admin/intelligence/collection/tasks`
- `GET /api/v1/admin/intelligence/collection/tasks`
- `GET /api/v1/admin/intelligence/collection/tasks/{task_id}`
- `GET /api/v1/admin/intelligence/collection/tasks/{task_id}/subtasks`
- `GET /api/v1/admin/intelligence/collection/tasks/{task_id}/logs`
- `POST /api/v1/admin/intelligence/collection/tasks/{task_id}/retry`
- `POST /api/v1/admin/intelligence/collection/tasks/{task_id}/cancel`
- `GET /api/v1/admin/intelligence/collection/matches/{match_id}/items`
- `POST /api/v1/admin/intelligence/collection/debug/match-candidates`
- `POST /api/v1/admin/intelligence/collection/debug/replay`

## 5.2 需新增/增强接口

- 新增：`GET /api/v1/admin/intelligence/collection/tasks/{task_id}/failure-summary`
- 增强：`POST /tasks`（accepted + queue_id + estimated_start）
- 增强：`GET /tasks/{task_id}`（阶段进度、success_rate、partial）
- 增强：`POST /tasks/{task_id}/retry`（可按 source/match 定向重试）
- 增强：`GET /matches/{match_id}/items`（结构化质量字段优先输出）

---

## 6. 数据表改造（实施版）

## 6.1 必做（P0/P1）

- `intel_collection_tasks`
  - 新增：`success_rate`, `queue_job_id`, `request_payload_json`, `config_snapshot_json`（可后移）
  - 状态枚举补充：`partial`
- `intel_collection_match_subtasks`
  - 新增：`candidate_count`, `parsed_count`, `matched_count`, `accepted_count`, `blocked_count`
- `intel_collection_items`
  - 新增：`quality_status`, `quality_score`, `quality_pass_reason`, `quality_block_reason`, `source_parser`, `article_url`, `match_hit_terms_json`

## 6.2 可选（P2）

- `intel_task_run_logs`（结构化日志表，替代大 JSON）
- `intel_quality_audit`（回放与阈值变更审计）

---

## 7. 验收门禁（Go/No-Go）

| 指标 | 门禁值 |
|---|---|
| 任务状态准确率 | 100%（无“全失败仍success”） |
| 创建/重试请求超时率 | <= 5% |
| 抓取成功率（HTTP） | >= 95% |
| 解析成功率（详情页） | >= 80% |
| 可用情报率（accepted） | >= 50% |
| 关键 E2E 用例通过率 | 100% |

---

## 8. 执行顺序（建议）

- 第1步（本周）：完成 `B1/B2/B3`，确保链路稳定可用。
- 第2步（下周）：完成 `B4/B5/B6`，提升诊断效率与数据稳定性。
- 第3步：持续做解析器质量收敛与回放门禁。

---

## 9. 备注（对齐要求）

- 本文档所有接口路径统一为：`/api/v1/admin/intelligence/collection/*`。
- 本文档是实施版，不再重复展开概念性方案，聚焦上线前能交付的事项。

