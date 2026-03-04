# Kaggle 比赛数据接入实施清单（按当前仓库结构）

## 1. 目标与范围

本清单用于将 Kaggle 比赛数据接入当前项目，作为现有抓取数据源（500w/100qiu/yingqiu）的补充，用于：

1. 扩充历史比赛样本。
2. 提升球队/联赛实体映射覆盖率。
3. 为平局预测训练链路提供可追溯的增强特征来源。

本阶段按照可灰度发布拆分为 PR-1 ~ PR-4。本文件重点给出 PR-1 的可执行任务。

## 2. 目录落位（固定）

### 2.1 文件数据层

1. `data/external/kaggle/<dataset_slug>/<version>/raw/`：原始下载文件。
2. `data/external/kaggle/<dataset_slug>/<version>/curated/`：清洗后文件（建议 parquet/csv）。
3. `data/external/kaggle/<dataset_slug>/<version>/rejects/`：脏数据与拒绝样本。
4. `reports/kaggle/<dataset_slug>/<run_id>/`：运行报告与质量报告。

### 2.2 代码模块层

1. `backend/models/`：Kaggle 元数据、运行记录、staging 表模型。
2. `backend/services/kaggle_sync_service.py`：同步编排服务（PR-1 提供基础能力）。
3. `backend/api/v1/admin/kaggle_sync.py`：管理接口。
4. `backend/main.py`：路由注册、生命周期启停。
5. `docs/`：本实施文档与后续 PR 验收报告。

## 3. 数据库表清单

## 3.1 配置与状态表

1. `kaggle_dataset_registry`
2. `kaggle_sync_state`
3. `kaggle_sync_runs`
4. `kaggle_file_manifest`

### 3.2 staging 表

1. `kaggle_match_staging`
2. `kaggle_team_staging`
3. `kaggle_league_staging`

### 3.3 复用表（不新增）

1. `external_source_mappings`
2. `matches`
3. `teams`
4. `leagues`
5. `draw_features` / `draw_training_jobs`（后续 PR 用于训练链路）

## 4. 任务名清单（统一命名）

1. `kaggle_discover_versions`
2. `kaggle_download_dataset`
3. `kaggle_transform_curated`
4. `kaggle_stage_upsert`
5. `kaggle_merge_entities`
6. `kaggle_quality_check`
7. `kaggle_feature_backfill`
8. `kaggle_retry_failed_runs`

说明：PR-1 先实现 registry/state/runs 的基础记录能力与 run-now 入口；真实下载与清洗在 PR-2。

## 5. 接口清单（Admin）

统一前缀：`/api/v1/admin/kaggle-sync`

1. `GET /status`：读取聚合状态。
2. `GET /datasets`：读取数据集注册列表。
3. `POST /datasets`：新增数据集注册。
4. `PATCH /datasets/{id}`：更新数据集配置。
5. `GET /runs`：读取运行历史。
6. `POST /run-now`：手工触发一次同步（PR-1 可先写入一条 pending run）。

PR-2/3 增量接口：

1. `GET /runs/{run_id}`
2. `GET /runs/{run_id}/quality`
3. `GET /datasets/{id}/preview`
4. `POST /datasets/{id}/rebuild`

## 6. 页面字段清单（复用已有页面，不新开重页面）

### 6.1 `frontend/src/views/admin/crawler/DataSourceManagement.vue`

新增展示字段：

1. `dataset_slug`
2. `latest_version`
3. `last_sync_at`
4. `sync_status`
5. `rows_upserted`
6. `last_error`

### 6.2 `frontend/src/views/admin/crawler/DataCenter.vue`

新增资产概览字段：

1. `kaggle_team_count`
2. `kaggle_league_count`
3. `kaggle_match_count`
4. `mapping_coverage_rate`
5. `quality_score`

### 6.3 `frontend/src/views/admin/crawler/TaskExecutionMonitor.vue`

新增筛选与列：

1. `task_type` 支持 `kaggle_*`
2. `run_id`
3. `duration_ms`
4. `retry_count`
5. `error_message`

## 7. PR 拆分计划

### PR-1：数据底座与最小管理接口

1. 建表模型与模型注册。
2. 状态/运行基础服务。
3. `/kaggle-sync` 最小接口。
4. `main.py` 路由注册与生命周期挂钩。

### PR-2：下载与清洗任务链路

1. 接入 Kaggle 下载。
2. 清洗、staging upsert、manifest 写入。
3. 失败重试与错误分级。

### PR-3：页面联调与运行可视化

1. 数据源管理页展示 Kaggle 状态。
2. 数据中心接真实指标。
3. 任务中心接真实 run 历史。

### PR-4：实体合并与特征回填

1. `external_source_mappings` 自动映射策略。
2. `teams/leagues/matches` 合并策略。
3. 平局预测特征增强链路接入。

## 8. PR-1 按文件到函数级任务单（直接可开发）

### 8.1 模型层

1. `backend/models/kaggle_dataset_registry.py`
   - `class KaggleDatasetRegistry(Base)`
2. `backend/models/kaggle_sync_state.py`
   - `class KaggleSyncState(Base)`
3. `backend/models/kaggle_sync_runs.py`
   - `class KaggleSyncRun(Base)`
4. `backend/models/kaggle_file_manifest.py`
   - `class KaggleFileManifest(Base)`
5. `backend/models/kaggle_match_staging.py`
   - `class KaggleMatchStaging(Base)`
6. `backend/models/kaggle_team_staging.py`
   - `class KaggleTeamStaging(Base)`
7. `backend/models/kaggle_league_staging.py`
   - `class KaggleLeagueStaging(Base)`
8. `backend/models/__init__.py`
   - 导入并导出上述 7 个模型。

### 8.2 服务层

1. `backend/services/kaggle_sync_service.py`
   - `class KaggleSyncService`
   - `start()`
   - `shutdown()`
   - `get_status_snapshot(db)`
   - `list_datasets(db, page, size, enabled)`
   - `create_dataset(db, payload)`
   - `update_dataset(db, dataset_id, payload)`
   - `list_runs(db, page, size, dataset_slug, status)`
   - `trigger_run_now(db, payload)`

### 8.3 API 层

1. `backend/api/v1/admin/kaggle_sync.py`
   - `GET /status`
   - `GET /datasets`
   - `POST /datasets`
   - `PATCH /datasets/{dataset_id}`
   - `GET /runs`
   - `POST /run-now`

### 8.4 应用接入层

1. `backend/main.py`
   - 注册 `kaggle_sync` 路由到 `/api/v1/admin`
   - 在 lifespan 启动/关闭时调用 `kaggle_sync_service.start()/shutdown()`

## 9. PR-1 验收标准

1. 服务启动后无导入错误。
2. OpenAPI 可见 `kaggle-sync` 路由。
3. `GET /api/v1/admin/kaggle-sync/status` 返回 `200`。
4. 可通过 `POST /datasets` 写入一条 registry 配置。
5. 可通过 `POST /run-now` 生成一条 run 记录（pending/running 任一允许）。
6. 不影响已有 `source-sync`、`data-source`、`task-monitor` 路由。

## 10. 你需要提供的 Key 动作（最小）

1. 提供 Kaggle API Token（仅环境变量，不落库，不入仓）。
2. 提供首批数据集列表（`owner/dataset`）。
3. 提供授权边界（可入库 license）。
4. 提供覆盖策略（Kaggle 与现有数据冲突时优先级）。

