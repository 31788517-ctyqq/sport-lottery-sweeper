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
