# 数据源管理页面重构任务单 V2（按文件到函数级）

文档版本: v2.0  
创建日期: 2026-03-01  
适用范围: `/admin/data-source/*` 模块  
目标: 在最大复用现有代码前提下，重构为“运行总览 / 任务中心 / 数据资产中心”三页架构

---

## 1. 重构目标与边界

### 1.1 新信息架构（IA）

1. 运行总览: `/admin/data-source/overview`
2. 任务中心: `/admin/data-source/tasks`
3. 数据资产中心: `/admin/data-source/assets`

### 1.2 旧路由兼容策略

1. `/admin/data-source/monitor` -> 重定向到 `/admin/data-source/overview`
2. `/admin/data-source/task-monitor` -> 重定向到 `/admin/data-source/tasks`
3. `/admin/data-source/task-console` -> 重定向到 `/admin/data-source/tasks`
4. `/admin/data-source/data-center` -> 重定向到 `/admin/data-source/assets`

### 1.3 本期不做

1. 不引入新中间件队列（Kafka 等）
2. 不重写全部可视化组件库
3. 不重做整站菜单体系，仅改数据源管理子域

---

## 2. 复用策略（必须执行）

### 2.1 直接复用组件

1. `frontend/src/views/admin/crawler/components/ExecutionList.vue`
2. `frontend/src/views/admin/crawler/components/LogViewer.vue`
3. `frontend/src/views/admin/crawler/components/RealtimeDashboard.vue`
4. `frontend/src/views/admin/crawler/components/StatisticsPanel.vue`
5. `frontend/src/components/common/ResourceGauge.vue`

### 2.2 页面复用拆分

1. `SystemMonitor.vue` 复用为“运行总览”主壳
2. `TaskConsole.vue + TaskExecutionMonitor.vue` 合并为“任务中心”双 Tab
3. `DataCenter.vue` 复用为“数据资产中心”壳，但删除随机/模拟逻辑

---

## 3. 分阶段执行计划

## 3.1 Phase P0（契约冻结与路由收敛）

| 编号 | 文件 | 函数/位置 | 改造动作 | 验收标准 |
|---|---|---|---|---|
| P0-01 | `frontend/src/router/modules/crawler-routes.js` | `children` 路由定义 | 新增 `overview/tasks/assets` 三路由；旧四路由改 `redirect` | 路由跳转后只存在三张主页面 |
| P0-02 | `frontend/src/layout/Index.vue` | 数据源管理菜单项 | 菜单改为“运行总览/任务中心/数据资产中心”；旧菜单入口下线 | 菜单无重复概念入口 |
| P0-03 | `frontend/src/components/Sidebar/MenuConfig.js` | `data-source` 配置节点 | 与 `Index.vue` 文案和路径对齐，避免双配置不一致 | 侧栏配置与实际路由一致 |
| P0-04 | `backend/main.py` | `APIMigrationMiddleware.dispatch` | 移除 `/api/v1/admin/data -> /api/admin/data` 反向重写 | 访问 `/api/v1/admin/data` 不再命中旧 mock 路径 |
| P0-05 | `backend/main.py` | `@app.get("/api/admin/data")`、`@app.get("/api/stats/data-center")` | 标记 deprecated，仅保留兼容提示，不承载主业务 | 前端主链路不调用这两个端点 |
| P0-06 | `frontend/src/api/crawlerMonitor.js` | 全部导出函数 | 路径统一为 `/api/v1/admin/crawler/monitor/*`；`acknowledgeAlert` 改 `PUT` | 无 404/405，路径与后端注册一致 |
| P0-07 | `frontend/src/api/taskMonitorApi.js` | 全部导出函数 | 路径统一为 `/api/v1/task-monitor/*`（显式加 `/api/v1`） | 任务监控接口路径一致 |
| P0-08 | `frontend/src/api/crawlerTask.js` | `listTasks/createTask/updateTask/...` | 路径统一为 `/api/v1/admin/crawler/tasks/*` 与 `/api/v1/admin/tasks/*` | 任务控制台所有请求 2xx/4xx 可预期 |
| P0-09 | `frontend/src/utils/request.js`、`frontend/src/api/index.js` | 响应拦截器 | 统一响应语义（建议统一返回 payload），禁止二次 `res.data` 套娃 | 三页面无 `res.data.data` 混用 |

## 3.2 Phase P1（运行总览页面重构）

| 编号 | 文件 | 函数/位置 | 改造动作 | 复用来源 | 验收标准 |
|---|---|---|---|---|---|
| P1-01 | `frontend/src/views/admin/crawler/SystemMonitor.vue` | `loadHealthStatus` | 仅保留“全局健康”加载，不再混入任务执行统计 | 原 `loadHealthStatus` | 卡片指标全来自后端真实接口 |
| P1-02 | 同上 | `loadAlerts`、`handleAcknowledge` | 保留告警列表与确认闭环；按新契约处理分页 | 原告警表格 | 告警确认成功后列表状态正确刷新 |
| P1-03 | 同上 | `loadSystemResources` | 仅展示资源指标（CPU/内存/磁盘/连接） | `ResourceGauge.vue` | 资源区无随机值 |
| P1-04 | 同上 | `generateSuccessRateData`、`generateVolumeData`、`updateSuccessRateChart` | 删除随机生成逻辑，改为真实趋势接口数据映射 | 原 ECharts 配置 | 刷新后图线随真实数据变化 |
| P1-05 | 同上 | `loadTaskStats` 与“任务关联区块” | 移除该区块，职责迁移到任务中心 | - | 运行总览页面不再显示任务列表 |
| P1-06 | `backend/api/v1/crawler_monitor.py` | `get_system_health`、`get_metrics` | 从真实表统计输出，不再硬编码成功率/质量分 | 现有任务日志表 | 指标可用 SQL 复算 |
| P1-07 | 同上 | `get_alerts`、`acknowledge_alert` | 从告警记录/规则结果读取并更新 | 现有告警模型或最小状态表 | 告警状态流转可追踪 |
| P1-08 | 同上 | `get_success_rate_trend`、`get_data_volume_stats` | 改为按时间窗聚合真实数据 | 现有日志与采集表 | 趋势数据与数据库一致 |

## 3.3 Phase P2（任务中心页面重构）

| 编号 | 文件 | 函数/位置 | 改造动作 | 复用来源 | 验收标准 |
|---|---|---|---|---|---|
| P2-01 | `frontend/src/views/admin/crawler/TaskConsole.vue` | 页面主结构 | 改为 Tab1: 任务配置；Tab2: 执行监控（嵌入 ExecutionList + LogViewer） | 原 TaskConsole + TaskExecutionMonitor | 原两个页面合并为一个入口 |
| P2-02 | `frontend/src/views/admin/crawler/TaskExecutionMonitor.vue` | 全组件 | 下沉为 `TaskCenterExecutionTab.vue`（被任务中心引用） | 当前组件完整复用 | 功能不丢失，路径统一 |
| P2-03 | `frontend/src/stores/taskMonitorStore.js` | `fetchExecutions` | 清理多分支兼容，统一解析单一响应结构 | 当前 normalizeExecution | 解析逻辑可预测，无类型漂移 |
| P2-04 | 同上 | `connectWebSocket` | 若后端未提供 WS，禁用自动重连并改为轮询策略 | 当前 store | 控制台无无效重连噪音 |
| P2-05 | `frontend/src/views/admin/crawler/components/LogViewer.vue` | `fallbackLogs`、`fetchLogs` | 移除生产兜底假日志；失败时显示错误态 | 原日志UI | 生产不再出现“示例日志” |
| P2-06 | `frontend/src/views/admin/crawler/components/ExecutionList.vue` | 筛选与分页 | 保留前端筛选展示；分页统计改后端总量驱动 | 原列表组件 | 分页总数与后端一致 |
| P2-07 | `backend/api/v1/task_monitor.py` | `get_executions`、`get_realtime_overview`、`get_top_issues` | 作为任务中心“执行监控”唯一读接口，补齐字段一致性 | 现有真实查询 | 前端不需要多种字段兼容分支 |
| P2-08 | `backend/api/v1/admin/task_management.py` 与 `backend/api/v1/admin/crawler_tasks.py` | 路由能力重叠区 | 选定“唯一写接口”并对另一套标记 deprecated | 现有两套实现 | 任务写路径只剩一套主入口 |

## 3.4 Phase P3（数据资产中心重构）

| 编号 | 文件 | 函数/位置 | 改造动作 | 复用来源 | 验收标准 |
|---|---|---|---|---|---|
| P3-01 | `frontend/src/views/admin/crawler/DataCenter.vue` | 页面主结构 | 变更为三 Tab: 数据清单/质量新鲜度/期号覆盖 | 原 DataCenter 壳 | 信息架构与新 IA 一致 |
| P3-02 | 同上 | `sources` 初始化 | 删除硬编码源列表，改为数据源配置接口拉取 | `DataSourceManagement` 接口 | 下拉源与配置页一致 |
| P3-03 | 同上 | `startRealtimeUpdate`、`initRealtimeChart` | 删除随机实时模拟，改为真实轮询/聚合 | 原图表容器 | 图表无随机值 |
| P3-04 | 同上 | `confirmExport` | 删除 `setTimeout` 模拟，接真实导出API | `exportData` API | 导出可下载真实文件 |
| P3-05 | 同上 | `handleSearch`、`applyFilters` | 筛选逻辑以后端为准，前端仅保留UI状态 | 原筛选表单 | 查询条件与后端结果一致 |
| P3-06 | `backend/api/v1/data_center_adapter.py` | `get_summary_stats` | 去模拟增长和质量值，改真实聚合 | 现有 DB 表 | 卡片数据可追溯 |
| P3-07 | 同上 | `get_data_list` | 实装 `type/source/status/date` 过滤；去 `pass` 占位 | 现有查询框架 | 筛选全部生效 |
| P3-08 | 同上 | `export_data_list` | 实装异步导出任务与下载URL | 现有导出接口壳 | 导出结果可落地下载 |
| P3-09 | `backend/api/v1/admin/data_center.py` | 全模块 | 与 adapter 二选一: 保留并真实化或下线；避免双轨 | 现有 admin 版本 | 数据资产接口仅一套主入口 |

## 3.5 Phase P4（联调、回归与灰度）

| 编号 | 文件 | 函数/位置 | 改造动作 | 验收标准 |
|---|---|---|---|---|
| P4-01 | `frontend/tests/unit/views/DataCenter.test.js` | 全文件 | 用真实契约更新断言，移除对模拟字段依赖 | 单测通过且断言契约一致 |
| P4-02 | `frontend/tests/e2e/menu-smoke-minimal.spec.js` | 数据源管理菜单场景 | 新增三页面冒烟：导航、查询、导出、日志抽屉 | E2E 冒烟通过 |
| P4-03 | `backend/tests/unit/api/admin/test_data_center.py` | 全文件 | 对选定主接口补齐过滤/导出/分页测试 | 后端单测通过 |
| P4-04 | `backend/tests/unit/api/admin/test_crawler_configs.py`（必要时） | 关联场景 | 校验数据源列表与资产页筛选一致性 | 契约回归通过 |
| P4-05 | `docs/*` | 文档章节更新 | 同步菜单结构、接口清单、灰度与回滚步骤 | 文档与实现一致 |

---

## 4. 页面职责最终定义（防重复红线）

1. 运行总览只负责健康、告警、SLO，不做任务CRUD与日志详情。
2. 任务中心只负责任务配置与执行过程，不做数据资产分析。
3. 数据资产中心只负责数据清单、质量、新鲜度、期号覆盖，不做任务运行控制。

---

## 5. 接口归一化清单（V2）

### 5.1 运行总览

1. `GET /api/v1/admin/crawler/monitor/health`
2. `GET /api/v1/admin/crawler/monitor/resources`
3. `GET /api/v1/admin/crawler/monitor/alerts`
4. `PUT /api/v1/admin/crawler/monitor/alerts/{id}/acknowledge`
5. `GET /api/v1/admin/crawler/monitor/trends/success-rate`
6. `GET /api/v1/admin/crawler/monitor/stats/data-volume`

### 5.2 任务中心

1. `GET /api/v1/admin/crawler/tasks`
2. `POST /api/v1/admin/crawler/tasks`
3. `PUT /api/v1/admin/crawler/tasks/{id}`
4. `DELETE /api/v1/admin/crawler/tasks/{id}`
5. `POST /api/v1/admin/crawler/tasks/{id}/trigger`
6. `POST /api/v1/admin/tasks/{id}/stop`
7. `GET /api/v1/task-monitor/executions`
8. `GET /api/v1/task-monitor/executions/{id}/logs`
9. `GET /api/v1/task-monitor/realtime/overview`
10. `GET /api/v1/task-monitor/statistics/top-issues`

### 5.3 数据资产中心

1. `GET /api/v1/stats/data-center`
2. `GET /api/v1/admin/data`
3. `POST /api/v1/admin/data/export`

---

## 6. PR 拆分建议（按周）

1. PR-1（路由与契约层）: P0 全部 + 菜单切换 + 旧路由重定向
2. PR-2（运行总览）: P1 全部
3. PR-3（任务中心）: P2 全部
4. PR-4（数据资产中心）: P3 全部
5. PR-5（测试与灰度）: P4 全部

---

## 7. 每阶段验收门槛

1. P0: 无 `/api/admin/*` 主链路调用；无 404/405 契约错误。
2. P1: 总览无随机图，无硬编码健康值。
3. P2: 任务配置+执行监控合并完成，日志无假数据。
4. P3: 数据中心导出真实可用，筛选全链路生效。
5. P4: 单测+冒烟通过，旧路由可回退。

---

## 8. 风险与回滚

1. 风险: 老缓存前端仍访问旧路由。  
回滚: 保留旧路由 redirect，不直接删除页面文件。

2. 风险: 双任务接口并存导致数据写入口冲突。  
回滚: 锁定写入口为一套，另一套只读或返回 deprecated。

3. 风险: 统计真实化后出现慢查询。  
回滚: 降级时间窗，增加索引，临时关闭重计算指标。

---

## 9. 融合“中英文映射+别名增强+官方信息自动收录”到三页面

### 9.1 融合目标（你能在三页面直接看到什么）

1. 运行总览:
显示“实体映射健康卡”和“官方链接健康卡”，可一眼看到 `映射覆盖率/未映射数/官方链接有效率/待更新数`。
2. 任务中心:
新增“实体与官方任务”分区，可触发 `全量验证` 与 `全量发现`，并查看最近批任务状态和耗时。
3. 数据资产中心:
新增“标准化质量与别名命中”视图，展示 `标准化成功率/回退原始名次数/Top未识别别名`，支持按数据源过滤。

### 9.1.1 强约束需求（本期必须满足）

1. 中英文映射与别名增强必须是“全自动补强”为主流程:
基于数据库新增/变更的球队、联赛、别名信息自动发现候选映射并自动补强，不依赖人工逐条触发。
2. 页面必须可查看自动补强真实情况:
在三页面入口可见 `自动补强任务状态/新增别名数/待人工确认数/最近失败原因`。
3. 官方信息必须支持“双轨”:
自动收录（定时发现+验证） + 手工补录（人工录入/修正/覆盖），两者都要有审计与来源标记。
4. 手工补录不是替代自动:
手工入口用于纠偏和补漏，自动收录仍持续运行并对后续变化负责。

### 9.2 现有可直接复用能力（不重复造轮子）

1. 后端:
`backend/api/v1/admin/entity_mapping.py`
已有 `summary / mappings / verify-all / discover-all / update`。
2. 服务:
`backend/services/data_processor.py`
已有 `_normalize_team_name`、`_normalize_league_name` 和模糊匹配逻辑。
3. 前端API:
`frontend/src/api/entityMapping.js`
已有 `getOfficialInfoSummary`、`getEntityMappings`、`verifyOfficialInfoAll`、`discoverOfficialInfoAll`。
4. 前端页面:
`frontend/src/views/admin/system/EntityMappings.vue`
`frontend/src/views/admin/crawler/OfficialInfoManagement.vue`
可作为三页面中的“深链详情页”。

### 9.3 文件到函数级改造清单（融合专项）

| 编号 | 文件 | 函数/位置 | 改造动作 | 验收标准 |
|---|---|---|---|---|
| EM-01 | `frontend/src/views/admin/crawler/SystemMonitor.vue` | 新增 `loadEntityMappingHealth` | 调 `getOfficialInfoSummary` 与 `getEntityMappings` 聚合健康卡数据 | 总览页可见映射与官方信息健康卡 |
| EM-02 | 同上 | 模板区块（卡片区域） | 增加“映射覆盖率/官方链接有效率/待更新数”三类卡片 + 深链按钮 | 点击可跳转实体映射页和官方信息页 |
| EM-03 | `frontend/src/views/admin/crawler/TaskConsole.vue` | 新增 `handleVerifyAllEntities`、`handleDiscoverAllEntities` | 接 `verifyOfficialInfoAll/discoverOfficialInfoAll`；展示最近触发结果 | 任务中心可直接触发并回显结果 |
| EM-04 | 同上 | 新增“实体与官方任务”Tab/Panel | 与任务配置、执行监控并列，避免职责混淆 | 任务中心内可完整查看实体/官方收录任务 |
| EM-05 | `frontend/src/views/admin/crawler/DataCenter.vue` | 新增 `loadNormalizationQuality` | 拉取标准化质量指标（成功率、回退次数、未识别别名TopN） | 资产中心可按源/日期查看标准化质量 |
| EM-06 | 同上 | 资产中心“质量与新鲜度”Tab | 增加实体标准化质量小节与官方信息新鲜度小节 | 数据资产页可见实际质量情况，不需切页 |
| EM-07 | `frontend/src/api/entityMapping.js` | `getOfficialInfoSummary` | 增加 `force_verify` 参数能力（可选） | 支持“快速读缓存”与“强制校验”两模式 |
| EM-08 | 同上 | 新增 `getNormalizationMetrics`（规划） | 对接统一统计端点，供总览与资产页复用 | 两页面共享同一统计接口，无重复拼装 |
| EM-09 | `backend/api/v1/admin/entity_mapping.py` | 新增 `GET /entity-mapping/stats/normalization` | 输出标准化成功率、回退次数、Top未识别别名、按source维度聚合 | 前端无需读日志拼接即可展示质量指标 |
| EM-10 | 同上 | `get_official_info_summary` | 增加轻量字段 `valid_rate`、`stale_rate`、`last_batch_job_at` | 总览卡片可直接显示比率与最近批次 |
| EM-11 | `backend/services/data_processor.py` | `_normalize_team_name`、`_normalize_league_name` | 未命中时记录审计事件（source/raw_name/entity_type/timestamp） | 可统计“未识别别名TopN” |
| EM-12 | `backend/models/`（新增） | `entity_normalization_audit` 模型（规划） | 持久化标准化失败与回退事件，支持时间窗统计 | 可按天/源查询失败趋势 |
| EM-13 | `backend/api/v1/data_center_adapter.py` | `get_summary_stats` | 纳入 `entityMappingCoverage`、`officialInfoValidRate` 指标 | 资产中心与总览口径一致 |
| EM-14 | `backend/api/v1/data_center_adapter.py` | 新增 `GET /admin/data/normalization-issues`（规划） | 返回未识别实体列表与出现频次 | 资产中心可 drill-down 明细 |
| EM-15 | `frontend/src/router/modules/crawler-routes.js` | `data-source` 子路由 | 保留 `official-info` 作为深链详情；主导航不新增重复入口 | 三页面主入口不膨胀但可深挖 |
| EM-16 | `backend/services/data_processor.py` | `_normalize_team_name`、`_normalize_league_name` | 新增“自动补强候选上报”逻辑（命中失败/模糊高置信候选写入候选池） | 候选池可持续增长并可统计来源 |
| EM-17 | `backend/models/`（新增） | `entity_alias_candidate` 模型（规划） | 存储自动补强候选（entity_type/raw_name/source/confidence/status） | 可区分 auto_confirmed/pending/rejected |
| EM-18 | `backend/services/task_scheduler_service.py`（或现有调度层） | 新增实体补强定时任务 | 定时执行别名自动补强与候选确认流程，写入任务日志 | 无人工操作时别名仍持续更新 |
| EM-19 | `backend/services/official_info_service.py` | `discover_official_links`、`verify_all_official_links` | 增加定时自动收录批任务入口和结果摘要输出 | 官方信息可按周期自动更新 |
| EM-20 | `backend/api/v1/admin/entity_mapping.py` | `update_official_info` | 明确手工补录语义（manual_source/manual_note/override_strategy 审计字段） | 手工补录可追溯且不丢来源 |
| EM-21 | `frontend/src/views/admin/crawler/OfficialInfoManagement.vue` | 新增 `handleManualUpsertOfficialInfo` | 增加“手工补录/修正”弹窗与提交流程（覆盖或合并） | 用户可手工补录并立即可见 |
| EM-22 | `frontend/src/views/admin/crawler/SystemMonitor.vue`、`TaskConsole.vue`、`DataCenter.vue` | 新增自动补强/自动收录状态区块 | 三页面均展示自动任务健康和手工补录统计（入口级可见） | 无需跳到系统页即可掌握现状 |

### 9.4 三页面展示口径（统一字段定义）

1. 映射覆盖率 `mapping_coverage_rate`:
`已映射实体数 / 总实体数 * 100`
2. 标准化成功率 `normalization_success_rate`:
`标准化命中次数 / 标准化总请求次数 * 100`
3. 官方链接有效率 `official_link_valid_rate`:
`有效官方链接实体数 / 已配置官方链接实体数 * 100`
4. 官方信息待更新率 `official_info_stale_rate`:
`last_verified 超过阈值天数 的实体数 / 总实体数 * 100`

### 9.5 接口清单补充（融合后）

1. `GET /api/v1/entity-mapping/official-info/summary`
2. `POST /api/v1/entity-mapping/official-info/verify-all`
3. `POST /api/v1/entity-mapping/official-info/discover-all`
4. `GET /api/v1/entity-mapping/mappings/{entity_type}`
5. `GET /api/v1/entity-mapping/stats/normalization`（新增规划）
6. `GET /api/v1/admin/data/normalization-issues`（新增规划）
7. `POST /api/v1/entity-mapping/aliases/auto-enhance/run`（新增规划）
8. `GET /api/v1/entity-mapping/aliases/auto-enhance/status`（新增规划）
9. `POST /api/v1/entity-mapping/official-info/manual-upsert`（新增规划；或复用 `PUT /official-info/{entity_type}/{entity_id}`）

### 9.6 验收用例补充（融合专项）

1. 打开运行总览可看到“映射覆盖率”和“官方链接有效率”实时值，且可跳转详情页。
2. 在任务中心点击“全量验证/全量发现”后，任务状态与摘要数字会刷新。
3. 在数据资产中心按数据源筛选后，标准化成功率与未识别别名榜单同步变化。
4. 三页面显示的映射与官方信息指标口径一致，无“同指标不同值”。
5. 任一实体映射更新后，三页面相关指标在可接受时间窗内（如 1-5 分钟）更新。
6. 在无人工操作 24 小时内，实体别名候选仍会自动产生并出现“自动补强任务执行记录”。
7. 官方信息在自动收录后可手工补录修正，且最终展示保留“auto/manual”来源与更新时间。
8. 手工补录不会关闭自动收录，后续自动批次仍会运行并可在页面查看状态。

### 9.7 PR拆分调整（并入主线）

1. PR-2（运行总览）追加 EM-01/02/07/10/22。
2. PR-3（任务中心）追加 EM-03/04/18/19。
3. PR-4（数据资产中心）追加 EM-05/06/13/14/16/17。
4. PR-5（测试与灰度）追加 EM-09/11/12/20/21 及融合专项测试。
