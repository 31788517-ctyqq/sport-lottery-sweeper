# 实体映射 Stage-0 契约冻结清单

## 1. 目标

在 PR-2 开发前冻结“表结构演进规则、接口兼容边界、错误码规范”，保证后续迭代不破坏现有 `/admin/system/entity-mappings` 与 `/admin/data-source/official-info` 的联调链路。

## 2. 表结构冻结（数据库契约）

### 2.1 `entity_mapping_records`

| 字段 | 类型 | 当前用途 | Stage-0 规则 |
|---|---|---|---|
| `id` | int/bigint PK | 主键 | 冻结：不可改类型/语义 |
| `entity_type` | varchar(16) | team/league 维度 | 冻结：值域仅 `team`/`league` |
| `entity_ref_id` | varchar(64) | 业务实体 ID | 冻结：保留唯一约束组合 |
| `canonical_key` | varchar(128) | 标准键 | 可扩展：允许补充生成规则，不改字段语义 |
| `display_name` | varchar(255) | 展示主名称 | 可扩展：允许回填策略优化 |
| `zh_names` | JSON | 中文名集合 | 冻结：列表语义不变 |
| `en_names` | JSON | 英文名集合 | 冻结：列表语义不变 |
| `jp_names` | JSON | 日文名集合 | 冻结：列表语义不变 |
| `source_aliases` | JSON | 源别名映射 | 冻结：`{source:[aliases]}` 结构不变 |
| `official_info` | JSON | 官方信息字段容器 | 可扩展：仅新增 key，不删旧 key |
| `confidence_score` | float | 置信度 | 可扩展：计算策略可变，字段语义不变 |
| `auto_generated` | bool | 是否自动生成 | 冻结 |
| `last_seen_at` | datetime | 最近见到时间 | 冻结 |
| `created_at` | datetime | 创建时间 | 冻结 |
| `updated_at` | datetime | 更新时间 | 冻结 |

约束冻结：
- 唯一键 `uq_entity_mapping_records_type_ref(entity_type, entity_ref_id)` 不可移除。
- 索引 `idx_entity_mapping_records_type_display` 不可移除。

### 2.2 `entity_mapping_sync_runs`

| 字段 | 类型 | 当前用途 | Stage-0 规则 |
|---|---|---|---|
| `id` | int/bigint PK | 主键 | 冻结 |
| `trigger_type` | varchar(32) | 触发来源 | 冻结：`scheduler/manual/startup` 可扩展枚举 |
| `status` | varchar(20) | 运行状态 | 冻结：`running/success/failed` |
| `scanned_teams` | int | 扫描球队数 | 冻结 |
| `scanned_leagues` | int | 扫描联赛数 | 冻结 |
| `upserted_teams` | int | 更新球队数 | 冻结 |
| `upserted_leagues` | int | 更新联赛数 | 冻结 |
| `failed_count` | int | 失败条数 | 冻结 |
| `error_message` | text | 失败原因 | 冻结 |
| `summary` | JSON | 汇总结构 | 可扩展：新增 key，不删已发布 key |
| `started_at` | datetime | 启动时间 | 冻结 |
| `finished_at` | datetime | 完成时间 | 冻结 |

## 3. 接口兼容矩阵（API 契约冻结）

### 3.1 必须保持兼容（PR-2 期间不下线）

| 接口 | 方法 | 当前返回关键结构 | Stage-0 兼容要求 |
|---|---|---|---|
| `/api/v1/entity-mapping/mappings/{entity_type}` | GET | `{status,data,source?}`，`data` 为 `id -> mapping` | 默认调用不破坏；新增参数必须可选 |
| `/api/v1/entity-mapping/mappings/{entity_type}/{entity_id}` | PUT | `{status,message,source?}` | 更新行为保持；DB/静态兜底逻辑不移除 |
| `/api/v1/entity-mapping/sync/status` | GET | `{status,data}`，含 `is_running/last_run/...` | 字段可增不可删 |
| `/api/v1/entity-mapping/sync/trigger` | POST | `{status,data}`，含 `started/message` | 保持幂等语义（运行中重复触发不并发） |
| `/api/v1/entity-mapping/official-info/*` | GET/POST/PUT | 现有 discover/verify/update 契约 | 路由与入参兼容 |

### 3.2 计划新增（PR-2 允许新增，不影响旧调用）

| 接口 | 方法 | 说明 | 兼容策略 |
|---|---|---|---|
| `/api/v1/entity-mapping/conflicts/{entity_type}` | GET | 冲突清单 | 新接口独立，不影响旧接口 |
| `/api/v1/entity-mapping/review/{entity_type}/{entity_id}` | POST | 审核动作 | 新接口独立，不影响旧接口 |

## 4. 错误码规范（Stage-0 冻结）

| 场景 | HTTP 状态码 | 约束 |
|---|---|---|
| 参数非法/实体类型非法 | 400 | 返回可读 message |
| 资源不存在 | 404 | 返回可读 message |
| 并发冲突（建议） | 409 | 仅用于“运行中重复触发”等冲突场景 |
| 参数校验失败 | 422 | 保持 FastAPI 默认校验结构 |
| 服务内部错误 | 500 | 不泄露敏感堆栈，记录日志 |

返回体建议（错误场景）
- 最小字段：`status=error` + `message`
- 可选字段：`detail`/`code`（新增时不能破坏旧前端）

## 5. 配置开关冻结

| 配置项 | 默认值 | Stage-0 要求 |
|---|---|---|
| `AUTO_ENTITY_MAPPING_SYNC_ENABLED` | true | 可随时关闭任务链路 |
| `AUTO_ENTITY_MAPPING_SYNC_INTERVAL_MINUTES` | 180 | 可调但不低于 30（生产建议） |
| `AUTO_ENTITY_MAPPING_SYNC_RUN_ON_STARTUP` | true | 支持一键关闭启动即跑 |
| `AUTO_ENTITY_MAPPING_SYNC_MATCH_SCAN_LIMIT` | 5000 | 防止扫描放大 |

## 6. 回滚约束

- 任何阶段异常，允许回退到“PR-1 基线”：
  - 仅保留 `mappings/* + sync/* + official-info/*` 现有行为。
  - 关闭自动增强任务，不移除已有表与数据。
- 不允许在 PR-2 删除 PR-1 已上线字段/接口。

## 7. 审查清单（提交前）

- [ ] 是否删除了已发布字段？
- [ ] 是否改变了 `mappings/{entity_type}` 默认返回结构？
- [ ] 是否新增了不可控高频任务？
- [ ] 是否有开关可以在不发版情况下止血？
- [ ] 是否保留静态映射兜底？
