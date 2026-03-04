# 实体映射 DB 自动补全（PR-1）逐文件到函数级实施清单

## 1. 目标范围（PR-1）

- 将 `/api/v1/entity-mapping/mappings/{entity_type}` 从“静态配置读取”升级为“DB 优先读取，静态配置兜底”。
- 新增“球队/联赛映射自动补全定时任务”，从 `teams/leagues/matches` 聚合别名并回填映射表。
- 新增同步状态与手动触发接口，支持页面观测任务健康。
- 保持前端现有页面接口契约基本不变（返回结构仍为 `id -> mapping` 的对象）。

不包含（留给 PR-2/PR-3）：
- 官方信息自动发现抓取增强（仅保留现有能力）。
- 映射冲突人工审核工作流页面。
- 高级模糊匹配模型（Levenshtein/Embedding）。

## 2. 数据表设计（PR-1）

### 2.1 `entity_mapping_records`

用途：存球队/联赛标准映射（页面主数据来源）。

核心字段：
- `id` bigint/int PK
- `entity_type` varchar(16) 索引，值：`team` / `league`
- `entity_ref_id` varchar(64) 索引，内部实体 ID（Team.id / League.id）
- `canonical_key` varchar(128) 索引，标准键（如 `team_16`）
- `display_name` varchar(255)
- `zh_names` JSON
- `en_names` JSON
- `jp_names` JSON
- `source_aliases` JSON（`{source: [alias...]}`）
- `official_info` JSON（网站/社媒等）
- `confidence_score` float
- `auto_generated` bool
- `last_seen_at` datetime
- `created_at` datetime
- `updated_at` datetime

约束：
- 唯一键：`(entity_type, entity_ref_id)`

### 2.2 `entity_mapping_sync_runs`

用途：记录每次自动任务执行情况。

核心字段：
- `id` bigint/int PK
- `trigger_type` varchar(32)（`scheduler` / `manual` / `startup`）
- `status` varchar(20)（`running` / `success` / `failed`）
- `scanned_teams` int
- `scanned_leagues` int
- `upserted_teams` int
- `upserted_leagues` int
- `failed_count` int
- `error_message` text
- `summary` JSON
- `started_at` datetime
- `finished_at` datetime

## 3. 逐文件到函数级任务（PR-1）

### 3.1 后端模型层

文件：`backend/models/entity_mapping_record.py`（新增）
- 新增类：`EntityMappingRecord`
- 新增类：`EntityMappingSyncRun`

文件：`backend/models/__init__.py`
- 导出：`EntityMappingRecord`
- 导出：`EntityMappingSyncRun`

### 3.2 后端服务层

文件：`backend/services/entity_mapping_sync_service.py`（新增）
- 新增类：`EntityMappingSyncService`
- 函数：`start()`
  - 注册 APScheduler 周期任务
- 函数：`shutdown()`
  - 停止调度器
- 函数：`trigger_run_now()`
  - 手动触发一次同步（线程异步执行）
- 函数：`get_status_snapshot(db)`
  - 返回运行状态、最近一次 run、下次执行时间
- 函数：`_run_safely(trigger_type)`
  - 锁保护，避免并发重复跑
- 函数：`_run_once(trigger_type)`
  - 执行主流程：扫描球队/联赛 -> 聚合别名 -> upsert -> 写 run 结果
- 函数：`_sync_teams(db)`
  - 遍历 `Team`，构建映射记录
- 函数：`_sync_leagues(db)`
  - 遍历 `League`，构建映射记录
- 函数：`_collect_team_aliases(db, team_id)`
  - 从 `Match.source_attributes` + `Match.data_source` 聚合别名
- 函数：`_collect_league_aliases(db, league_id)`
  - 同上，聚合联赛别名
- 函数：`_clean_candidate_name(raw)`
  - 清洗比分/方括号序号等噪音
- 函数：`_upsert_mapping_record(...)`
  - 映射记录入库更新

### 3.3 后端 API 层

文件：`backend/api/v1/admin/entity_mapping.py`
- 改造函数：`get_entity_mappings(entity_type)`
  - 先读 `entity_mapping_records`，按旧契约返回 `id -> data`
  - DB 无数据时回退静态配置
- 改造函数：`update_entity_mapping(entity_type, entity_id, updates)`
  - 优先更新 DB 记录
  - DB 不存在时回退旧逻辑（静态配置）
- 新增接口函数：`get_sync_status()`
  - `GET /entity-mapping/sync/status`
- 新增接口函数：`trigger_sync_now()`
  - `POST /entity-mapping/sync/trigger`

### 3.4 应用启动层

文件：`backend/main.py`
- 在 `lifespan` 启动阶段新增：
  - 启动 `entity_mapping_sync_service.start()`
- 在 `lifespan` 关闭阶段新增：
  - `entity_mapping_sync_service.shutdown()`

### 3.5 配置层

文件：`backend/config.py`
- 新增配置：
  - `AUTO_ENTITY_MAPPING_SYNC_ENABLED`（默认 `true`）
  - `AUTO_ENTITY_MAPPING_SYNC_INTERVAL_MINUTES`（默认 `180`）
  - `AUTO_ENTITY_MAPPING_SYNC_RUN_ON_STARTUP`（默认 `true`）

### 3.6 前端（PR-1 最小改造）

文件：`frontend/src/api/entityMapping.js`
- 新增 API：
  - `getEntityMappingSyncStatus()` -> `/api/v1/entity-mapping/sync/status`
  - `triggerEntityMappingSync()` -> `/api/v1/entity-mapping/sync/trigger`

文件：`frontend/src/views/admin/system/EntityMappings.vue`
- 新增轻量状态区：
  - 展示最近同步时间、运行状态
  - 提供“立即同步”按钮

说明：
- 表格主体组件 `MappingTable.vue` 在 PR-1 不重构，仅复用现有读取接口。

## 4. 接口契约（PR-1）

### 4.1 `GET /api/v1/entity-mapping/mappings/{entity_type}`

响应保持：
- `status: success`
- `data: { "<id>": { zh, en, jp, source_aliases, official_info... } }`

新增保证：
- DB 有数据时返回 DB 映射。
- DB 无数据时返回静态配置（兼容）。

### 4.2 `GET /api/v1/entity-mapping/sync/status`

字段建议：
- `auto_enabled`
- `is_running`
- `last_started_at`
- `last_finished_at`
- `last_run`（run 明细）
- `next_sync_at`

### 4.3 `POST /api/v1/entity-mapping/sync/trigger`

字段建议：
- `started: true/false`
- `message`

## 5. 验收用例（PR-1）

### 5.1 功能验收

- 用例 F1：首次启动服务后，`entity_mapping_records` 自动产生球队与联赛映射。
- 用例 F2：`/entity-mapping/mappings/team` 返回 DB 数据结构正确。
- 用例 F3：`/entity-mapping/mappings/league` 返回 DB 数据结构正确。
- 用例 F4：手动触发 `/entity-mapping/sync/trigger` 可成功发起任务。
- 用例 F5：`/entity-mapping/sync/status` 能看到最近一次运行记录。

### 5.2 回归验收

- 用例 R1：`/admin/system/entity-mappings` 页面可正常打开，表格不报 4xx/5xx。
- 用例 R2：编辑映射保存后，刷新可见更新结果。
- 用例 R3：官方信息页面不受本次改造影响。

### 5.3 失败场景

- 用例 E1：任务执行异常时写入 `entity_mapping_sync_runs.status=failed`。
- 用例 E2：任务运行中重复触发，返回“already running”而不是并发执行。

## 6. 灰度步骤（PR-1）

1. 部署后仅启用“写 run 记录 + 手动触发”，观察 1 天。  
2. 打开定时调度（180 分钟一次），观察 2 天。  
3. 前端切换展示同步状态与手动同步入口。  
4. 稳定后默认开启开机首轮同步。

## 7. PR-1 交付物清单

- 新增：
  - `backend/models/entity_mapping_record.py`
  - `backend/services/entity_mapping_sync_service.py`
- 修改：
  - `backend/models/__init__.py`
  - `backend/api/v1/admin/entity_mapping.py`
  - `backend/main.py`
  - `backend/config.py`
  - `frontend/src/api/entityMapping.js`
  - `frontend/src/views/admin/system/EntityMappings.vue`

## 8. 备注

- 该 PR 先实现“数据库自动补全 + 定时任务 + 读接口切换”。
- “冲突审核、高级规则引擎、官方抓取增强”进入后续 PR。

---

## 9. 执行前阶段化总方案（优化版）

> 目的：在正式继续开发前，先把 **PR-2 ~ PR-4** 的阶段任务、门禁、回滚写清楚，避免边做边改方向。

### 9.1 当前状态基线（截至本次 PR-1 收尾）

- `PR-1` 已完成并提交：`d01b654`
- 已具备：
  - DB 映射主链路（`entity_mapping_records`）
  - 自动同步定时任务（`entity_mapping_sync_service`）
  - 同步状态/手动触发 API
  - `/admin/system/entity-mappings` 页面最小联调可用
- 当前风险：
  - 映射质量仍受脏别名影响（比分串、噪声词、重复别名）
  - 官方信息自动补全链路未闭环（仅有现有 discover/verify 能力）
  - 人工审核流程未形成（冲突无“待审/已审”状态）

### 9.2 分阶段总览

| 阶段 | 对应 PR | 目标 | 主要产物 | 进入条件 | 退出门槛 |
|---|---|---|---|---|---|
| Stage-0 | 准备阶段 | 冻结范围与基线 | 字段/接口冻结清单、回归脚本清单 | PR-1 已上线本地 | 评审通过 |
| Stage-1 | PR-2 | 映射质量治理 | 别名清洗规则、冲突标记、分页检索接口 | Stage-0 完成 | 误匹配率下降且回归通过 |
| Stage-2 | PR-3 | 官方信息自动补全闭环 | 自动补全任务链路、任务状态、失败重试 | Stage-1 完成 | 自动补全成功率达标 |
| Stage-3 | PR-4 | 页面增强与运营可视化 | 审核视图、任务看板、状态标签统一 | Stage-2 完成 | 页面全链路联调通过 |
| Stage-4 | 灰度上线 | 灰度与回滚验证 | 开关策略、巡检报表、回滚手册 | Stage-3 完成 | 48h 稳定运行 |

### 9.3 执行前门禁（必须先满足）

1. 数据库可回滚：备份 `sport_lottery.db`（或生产同等备份策略）。
2. 开关可控：`AUTO_ENTITY_MAPPING_SYNC_*` 可动态控制任务启停。
3. 监控可见：至少能看到 `sync run` 最近状态与失败信息。
4. 兼容不破：保留静态配置兜底与旧接口返回结构。
5. 回归脚本可重复：固定“登录 -> 页面 -> 触发同步 -> 状态检查”路径。

---

## 10. Stage-0（准备阶段）任务清单

### 10.1 文档与契约冻结

文件：`docs/ENTITY_MAPPING_DB_AUTO_SYNC_PR1_TASKLIST.md`
- 新增“字段冻结表”（哪些字段可加不可删）
- 新增“接口兼容矩阵”（旧字段/新字段/兼容期）
- 新增“异常码规范”（400/404/409/422/500）

文件：`docs/ENTITY_MAPPING_DB_AUTO_SYNC_PR2_PR4_EXECUTION_PLAN.md`
- 分阶段里程碑、风险、验收与回滚模板（已新增）

### 10.2 回归基线固化

文件：`tests/`（按现有结构补回归清单，不强制当阶段写代码）
- 定义最小回归：
  - API：`mappings/*`、`sync/status`、`sync/trigger`
  - 页面：`/admin/system/entity-mappings`、`/admin/data-source/official-info`

### 10.3 Stage-0 Batch-1 落地产出（已完成）

文件：`docs/ENTITY_MAPPING_STAGE0_CONTRACT_FREEZE.md`
- 已落地：字段冻结表、接口兼容矩阵、错误码规范、回滚约束。

文件：`docs/ENTITY_MAPPING_STAGE0_REGRESSION_BASELINE.md`
- 已落地：API/页面回归基线清单、命令模板、执行记录模板。
- 已记录：2026-03-04 Batch-1 的首轮 API/页面结果。

---

## 11. Stage-1（PR-2：映射质量治理）逐文件到函数级任务

### 11.1 数据模型增强（质量/审核字段）

文件：`backend/models/entity_mapping_record.py`
- 新增字段（建议）：
  - `alias_count`（聚合别名数量）
  - `conflict_count`（冲突候选数）
  - `review_status`（`auto_accepted`/`pending_review`/`reviewed`）
  - `quality_score`（0~1）

### 11.2 同步服务规则增强

文件：`backend/services/entity_mapping_sync_service.py`
- 新增函数：
  - `_is_noise_alias(raw)`：过滤比分串/纯数字/异常长度
  - `_normalize_alias(raw)`：统一空白、符号、大小写
  - `_dedupe_aliases(items)`：别名去重（归一化后去重）
  - `_compute_quality_score(...)`：质量评分
  - `_detect_conflicts(...)`：同别名映射多实体冲突识别
- 改造函数：
  - `_collect_team_aliases` / `_collect_league_aliases`
  - `_upsert_mapping_record`（写入新增质量字段）

### 11.3 API 查询能力增强（不破旧）

文件：`backend/api/v1/admin/entity_mapping.py`
- 改造 `get_entity_mappings(entity_type)` 支持可选参数：
  - `page`、`size`、`search`、`review_status`
  - 保持默认不传时返回旧结构（兼容）
- 新增接口（建议）：
  - `GET /entity-mapping/conflicts/{entity_type}`
  - `POST /entity-mapping/review/{entity_type}/{entity_id}`

### 11.4 前端页面能力增强

文件：`frontend/src/views/admin/system/components/MappingTable.vue`
- 增加筛选项：关键字、审核状态、仅冲突
- 增加展示列：质量评分、冲突数、审核状态
- 保持“编辑保存”原行为不变

文件：`frontend/src/api/entityMapping.js`
- 新增 conflict/review API 调用封装

### 11.5 Stage-1 验收

- A1：噪音别名明显下降（抽样 100 条，脏别名命中率下降）。
- A2：冲突记录可查询，且可人工审核标记。
- A3：旧页面在“不传新参数”下行为不变。

---

## 12. Stage-2（PR-3：官方信息自动补全闭环）逐文件到函数级任务

### 12.1 自动补全任务链路

文件：`backend/services/official_info_service.py`
- 新增函数（建议）：
  - `auto_enrich_official_info(entity_type, entity_id, seed_aliases)`
  - `batch_auto_enrich(entity_type, limit, only_missing)`

文件：`backend/services/entity_mapping_sync_service.py`
- 在同步完成后按开关触发“缺失官方信息实体”补全任务

### 12.2 任务运行记录

文件：`backend/models/entity_mapping_record.py`（或新表）
- 记录字段（建议）：
  - `official_last_attempt_at`
  - `official_last_success_at`
  - `official_enrich_status`
  - `official_enrich_error`

### 12.3 API 与页面

文件：`backend/api/v1/admin/entity_mapping.py`
- 新增接口（建议）：
  - `POST /entity-mapping/official-info/enrich/trigger`
  - `GET /entity-mapping/official-info/enrich/status`

文件：`frontend/src/views/admin/crawler/OfficialInfoManagement.vue`
- 增加“自动补全状态”与“仅看缺失”筛选

文件：`frontend/src/views/admin/crawler/components/EntityOfficialInfoTable.vue`
- 增加来源标识（auto/manual）与最近补全时间

### 12.4 Stage-2 验收

- B1：缺失官方信息实体可被自动识别并回填。
- B2：失败可重试，状态可见。
- B3：不覆盖人工已确认字段（manual 优先）。

---

## 13. Stage-3（PR-4：页面联调与运营可视化）逐文件到函数级任务

### 13.1 Stage-3 目标与边界

- 目标：
  - 把“映射同步 + 冲突审核 + 官方信息补全”做成可观测闭环。
  - 页面入口统一：`EntityMappings`（操作入口）+ `DataCenter`（健康概览）+ `SystemMonitor`（任务告警）。
- 边界：
  - 不改动 Stage-1/Stage-2 的核心数据规则（只做联调与可视化增强）。
  - 不新增复杂审核工作流状态机（仅补齐批量操作与可见性）。
  - 保持现有接口兼容，新增接口优先“可选使用”。

### 13.2 后端接口层（PR-4 增补）

文件：`backend/api/v1/admin/entity_mapping.py`

- 新增函数：`get_entity_mapping_ops_overview()`
  - 路由建议：`GET /entity-mapping/ops/overview`
  - 输出字段建议：
    - `sync_success_rate_7d`
    - `last_failed_at`
    - `last_failed_message`
    - `pending_conflicts`
    - `official_enrich_running`
    - `official_enrich_pending`
    - `last_sync_finished_at`
- 新增函数：`_build_ops_overview_payload(db: Session) -> Dict[str, Any]`
  - 聚合来源：
    - `entity_mapping_sync_runs`
    - `entity_mapping_records`
    - `official_info_service.get_enrich_status_snapshot("all")`
- 改造函数：`get_entity_mapping_conflicts(...)`
  - 补充 `summary` 字段（总冲突数、待审核数）供页面直接展示。
- 改造函数：`get_entity_mapping_sync_status()`
  - 补充 `last_error_message` / `last_error_at`，避免前端二次推导。

### 13.3 前端 API 封装层

文件：`frontend/src/api/entityMapping.js`

- 新增函数：`getEntityMappingOpsOverview()`
  - 对应：`/api/v1/entity-mapping/ops/overview`
- 改造函数：`getEntityMappingConflicts(entityType, params)`
  - 保留旧返回结构读取；增加 `summary` 兼容读取。
- 复用现有函数：
  - `getEntityMappingSyncStatus()`
  - `triggerEntityMappingSync()`
  - `triggerOfficialInfoEnrich(params)`
  - `getOfficialInfoEnrichStatus(params)`

### 13.4 系统页（核心操作入口）

文件：`frontend/src/views/admin/system/EntityMappings.vue`

- 新增状态字段：
  - `opsOverview`
  - `opsOverviewLoading`
  - `enrichTriggerLoading`
- 新增计算属性：
  - `syncSuccessRateText`
  - `lastFailureText`
  - `pendingConflictsText`
- 改造函数：`mounted()`
  - 由串行改为并行：`Promise.all([loadSyncStatus(), loadOpsOverview()])`
- 新增函数：`loadOpsOverview()`
  - 加载运营卡片数据，失败时给默认兜底值。
- 改造函数：`handleTriggerSync()`
  - 触发后刷新 `loadSyncStatus + loadOpsOverview`。
- 新增函数：`handleTriggerEnrich()`
  - 调用 `triggerOfficialInfoEnrich({ entity_type: 'all', only_missing: true })`。
- 新增函数：`handleRefreshOps()`
  - 手动刷新状态与概览。

### 13.5 映射表组件（批量审核与批量建议）

文件：`frontend/src/views/admin/system/components/MappingTable.vue`

- 新增状态字段：
  - `selectedRows`
  - `batchActionLoading`
  - `tableErrorText`
- 新增函数：`handleSelectionChange(rows)`
  - 维护勾选集合。
- 新增函数：`handleBatchReviewReviewed()`
  - 对选中行批量调用 `reviewEntityMapping(..., { review_status: 'reviewed' })`。
- 新增函数：`handleBatchMergeSuggestion()`
  - 当前 PR-4 先做“建议生成+弹窗确认”能力（不直接写库合并）。
- 改造函数：`fetchData()`
  - 请求失败时设置 `tableErrorText`，并统一空态/错误态文案。
- 改造函数：`reviewCurrentRow()` 与 `saveCurrentRow()`
  - 与批量操作共享刷新逻辑，避免重复请求路径。

### 13.6 数据资产中心（健康联动）

文件：`frontend/src/views/admin/crawler/DataCenter.vue`

- 新增状态字段：
  - `entityMappingHealth`（健康卡数据）
  - `entityMappingHealthLoading`
- 新增函数：`loadEntityMappingHealth()`
  - 组合调用：
    - `getEntityMappingSyncStatus()`
    - `getEntityMappingConflicts('team', { page: 1, size: 1 })`
    - `getEntityMappingConflicts('league', { page: 1, size: 1 })`
- 新增函数：`buildEntityMappingHealthCard(syncStatus, teamConflict, leagueConflict)`
  - 统一映射健康度指标：
    - 冲突总数
    - 最近同步状态
    - 最近失败信息
- 改造函数：`initializePage()`
  - 追加 `loadEntityMappingHealth()` 并行加载。
- 改造函数：`handleRefresh()`
  - 纳入 `loadEntityMappingHealth()`。
- 改造函数：`loadStats()`
  - 可选将映射健康摘要并入顶部指标行（避免重复卡片时可按开关控制）。

### 13.7 系统监控页（任务告警联动）

文件：`frontend/src/views/admin/crawler/SystemMonitor.vue`

- 新增状态字段：
  - `mappingSyncStatus`
  - `mappingSyncAlerts`
  - `mappingSyncLoading`
- 新增函数：`loadMappingSyncStatus()`
  - 调用 `getEntityMappingSyncStatus()`，抽取运行态/失败态。
- 新增函数：`buildMappingSyncAlerts(statusPayload)`
  - 生成页面级告警条目（失败、长期未执行、待审冲突过高）。
- 改造函数：`refreshData()`
  - 纳入 `loadMappingSyncStatus()`。
- 改造定时刷新流程：
  - 在现有轮询内同步刷新映射状态模块。

### 13.8 文案与状态字典统一（防编码回退）

文件：`frontend/src/views/admin/crawler/constants/monitorText.js`
- 增加映射模块文案键：
  - `mappingHealthTitle`
  - `mappingPendingConflicts`
  - `mappingLastSync`
  - `mappingLastFailure`
  - `mappingTaskStatus`

文件：`frontend/src/views/admin/system/constants/entityMappingText.js`（新增）
- 承载 `EntityMappings.vue` 与 `MappingTable.vue` 公共文案：
  - 卡片标题
  - 批量操作按钮
  - 空态/错误态文案

### 13.9 Stage-3 分批执行顺序（建议）

- Batch-1：接口与 API 封装
  - `backend/api/v1/admin/entity_mapping.py`
  - `frontend/src/api/entityMapping.js`
- Batch-2：系统页与映射表
  - `EntityMappings.vue`
  - `MappingTable.vue`
- Batch-3：DataCenter 健康卡联动
  - `DataCenter.vue`
- Batch-4：SystemMonitor 任务告警联动
  - `SystemMonitor.vue`
- Batch-5：文案常量统一与编码回归
  - `monitorText.js`
  - `entityMappingText.js`

### 13.10 Stage-3 验收清单（页面联调）

- C1：三页联动数据一致，无重复/冲突入口。
  - 核查项：
    - `EntityMappings` 待审冲突数
    - `DataCenter` 健康卡冲突数
    - `SystemMonitor` 映射告警冲突数
    - 三者读数偏差 <= 1 个刷新周期
- C2：运营闭环可跑通。
  - 路径：
    - 页面看到冲突 -> 触发同步/补全 -> 状态更新 -> 冲突数变化可见
- C3：回归通过。
  - 无关键 4xx/5xx
  - 无关键 JS 报错（尤其 Element Plus 非法 prop 与图表尺寸异常）
  - 空态/错误态文案统一为可读中文

### 13.11 Stage-3 回滚策略（页面维度）

- 开关回滚优先级：
  1. 隐藏新增运营卡与批量按钮（保留原列表可用）
  2. `DataCenter/SystemMonitor` 退回旧指标卡，不影响主表
  3. 后端 `ops/overview` 接口失败时前端降级为“sync/status + conflicts”组合读取

---

## 14. Stage-4（灰度/发布）任务与门禁

### 14.1 灰度步骤

1. 第 1 天：仅开启同步增强规则，不开启官方信息自动补全。
2. 第 2~3 天：开启官方信息自动补全（低频、限量）。
3. 第 4 天：开启页面批量操作入口（管理员白名单）。
4. 第 5 天：全量开关打开，进入 48 小时巡检。

### 14.2 监控阈值建议

- `sync success rate >= 95%`
- `sync p95 duration < 120s`
- `official enrich success rate >= 85%`
- 页面接口 `4xx/5xx < 1%`

### 14.3 回滚策略

- 任一阶段异常可通过开关回退到 PR-1 基线：
  - 关闭自动补全，仅保留同步；
  - 接口返回继续 DB 优先 + 静态兜底；
  - 页面隐藏新增入口但不影响基础查询编辑。

---

## 15. 下一步执行顺序（建议）

1. 先完成 Stage-0（文档冻结 + 回归基线），确认后开始写代码。
2. 再做 Stage-1（PR-2，质量治理）并出“前后对照”。
3. 最后按 Stage-2/3 分批推进，保持每批可回滚、可验收。
