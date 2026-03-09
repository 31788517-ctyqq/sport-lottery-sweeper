# 情报采集系统改进方案 v3.0（综合可执行版）

> 合并来源：`INTELLIGENCE_COLLECTION_IMPROVEMENT_PLAN.md` + `INTELLIGENCE_COLLECTION_IMPROVEMENT_PLAN_V2.md`  
> 页面：`/admin/intelligence/collection`  
> 更新日期：2026-02-20  
> 执行周期：2026-02-23 至 2026-03-29（5 周）  
> 执行目标：先消除发布阻塞，再完成提质能力，最后交付可运营能力

---

## 1. 文档定位与合并原则

- 本文档是唯一执行基线，后续需求和变更以本文档为准。
- 以 v2.1 的阻塞项和接口口径作为上线前硬约束。
- 吸收 v1 的智能化能力（去重、增量、热度、推荐、告警、AI 摘要），按阶段落地。
- 所有任务必须具备：交付物、验收标准、回归用例、回滚策略。

---

## 2. 当前基线（2026-02-20）

### 2.1 已具备能力（可复用）

- 统一接口基座：`/api/v1/admin/intelligence/collection/*`
- 参数配置：time-window/network/source-rules/quality-thresholds/alias-dictionary
- 调试能力：候选调试、回放调试、任务日志、任务重试、子任务进度
- 来源健康看板与质量字段展示
- 回归脚本：`scripts/run-intelligence-regression.bat`、`scripts/run-all-tests.bat`（含 Playwright）

### 2.2 发布阻塞（必须先清）

- B1：任务最终状态误判（全失败仍 success）
- B2：计划任务未真正调度（scheduled 未被 worker 拉起）
- B3/B4：超时策略冲突、来源默认超时偏低
- B5：日志可诊断性不足（缺失败摘要）
- B6：质量字段过度依赖 `content_raw` 反解析
- B7/B8：文档口径不一致、重复实现未收敛

---

## 3. 范围与优先级

### 3.1 本期必做（Go-Live 必须完成）

- P0 稳定性：B1~B4 + 失败摘要接口
- P1 提质：结构化质量字段、解析器收敛、时间窗/别名精修、智能去重、增量采集、多维质量评分、异常检测
- 门禁：任务状态准确率 100%、关键 E2E 100%、超时率 <= 5%

### 3.2 本期可选（有余力再做）

- P2 可运营：SSE 实时进度、质量趋势看板、推送收敛、比赛热度评分、智能推荐、AI 摘要（Feature Flag）

### 3.3 非目标（本期不承诺）

- 大规模模型训练平台化
- 全量历史数据重清洗
- 非管理端采集链路重构

---

## 4. 分阶段执行计划（含具体日期）

## 4.1 Phase P0：先稳（2026-02-23 ~ 2026-03-01）

### 工作包 P0-1：任务状态机收敛（B1）
- 后端：
  - 统一终态：`success / partial / failed / cancelled`
  - 增加 `success_rate` 计算（按子任务 accepted/total）
  - `GET /tasks/{task_id}` 返回状态与成功率
- 前端：
  - 列表/详情支持 `partial`
  - 状态筛选与文案同步
- 验收：
  - 全失败任务显示 `failed`，不再误报 `success`
  - 回归用例覆盖“全成功/部分成功/全失败”

### 工作包 P0-2：任务调度落地（B2）
- 后端：
  - `POST /tasks` 改为“入队即返回”（`accepted + task_id + queue_job_id`）
  - worker 执行采集主流程；scheduled 任务支持 offset/cron 拉起
  - 重启恢复策略（未完成任务可续跑或重试）
- 验收：
  - 创建接口 P95 < 2s
  - 服务重启后排队任务可继续执行

### 工作包 P0-3：统一超时/重试策略（B3/B4）
- 后端：
  - 来源默认 timeout 上调（保留来源级覆盖）
  - 网络重试与退避策略统一
- 前端：
  - 保留全局 15s，但采集链路接口独立超时设置
  - 轮询改指数退避（2.5s -> 4s -> 6s）
- 验收：
  - 创建/重试 timeout 率 <= 5%
  - 轮询日志不再持续刷 timeout

### 工作包 P0-4：失败摘要与排障提效（B5）
- 后端新增：
  - `GET /tasks/{task_id}/failure-summary`
  - 返回：`top_reasons`、`source_failures`、`sample_logs`
- 前端：
  - 任务详情弹窗加入“失败摘要卡片”
- 验收：
  - 失败任务 3 分钟内可定位主因

---

## 4.2 Phase P1：再准（2026-03-02 ~ 2026-03-15）

### 工作包 P1-1：结构化质量字段入库（B6）
- 数据库迁移：
  - `intel_collection_items` 新增  
    `quality_status, quality_score, quality_pass_reason, quality_block_reason, source_parser, article_url, match_hit_terms_json`
  - `intel_collection_tasks` 新增  
    `success_rate, queue_job_id, request_payload_json, config_snapshot_json`
  - `intel_collection_match_subtasks` 新增  
    `candidate_count, parsed_count, matched_count, accepted_count, blocked_count`
- 后端：
  - 写入时直落结构化字段
  - `GET /matches/{match_id}/items` 优先输出结构化字段
- 验收：
  - 前端无需解析 `content_raw` 也可完整展示质量信息

### 工作包 P1-2：解析器质量收敛
- 后端：
  - 重点来源解析器强化（500w/ttyingqiu/weibo/tencent/sina）
  - 黑名单/降权规则参数化并支持热更新
  - 固定回放样例集 + 自动对比报告
- 验收：
  - 详情命中率、accepted 率持续提升，回放不回退

### 工作包 P1-3：时间窗与别名匹配精修
- 后端：
  - 时间窗硬门槛 + 软门槛（严格模式可切换）
  - 联赛/球队别名字典扩展（中英/简称/繁简）
- 验收：
  - `quality_block_reason` 可解释率 > 95%

### 工作包 P1-4：提质能力落地（来自 v1）
- 智能去重：
  - 文本相似度 + 标题归一化 + 来源交叉去重
  - 提供 `POST /deduplicate` 或并入采集流水线
- 增量采集：
  - 已采内容指纹跳过抓取
  - 缓存/DB 双层判重
- 多维质量评分：
  - 标题质量、正文长度、关键词命中、来源可信度、时间窗匹配综合评分
- 异常检测与告警：
  - 采集量骤降、质量骤降、来源失败、采纳率异常、重复率异常
  - 高危异常推送钉钉/邮件
- 验收：
  - 去重率 >= 85%
  - 抓取成功率 >= 95%
  - 异常检测召回率 >= 90%

---

## 4.3 Phase P2：可运营（2026-03-16 ~ 2026-03-29）

### 工作包 P2-1：实时进度推送（建议 SSE）
- 新增 SSE 通道（先不做 WebSocket）
- 事件字段：阶段、完成数、失败数、当前 source/match
- 验收：手动刷新次数显著下降

### 工作包 P2-2：质量趋势看板
- 新增趋势接口（日维度 success/accepted/blocked/avg_quality）
- 前端 ECharts 看板（可按来源、日期区间筛选）
- 验收：支持按周调参与效果追踪

### 工作包 P2-3：推送收敛与智能化（来自 v1）
- `push-preview` 支持 `top_n/min_score/include_blocked`
- 比赛热度评分（联赛权重/排名/交锋/赛事重要性）
- 智能推荐（推荐来源、推荐采集时机、推荐情报类型）
- AI 摘要（Feature Flag，灰度启用）
- 验收：
  - 可用情报率（accepted）>= 50%
  - 推荐采纳率 >= 60%
  - AI 摘要失败不影响主链路

---

## 5. 接口与数据口径（统一版）

### 5.1 路径规范
- 所有接口统一前缀：`/api/v1/admin/intelligence/collection/*`

### 5.2 必新增接口
- `GET /tasks/{task_id}/failure-summary`
- `GET /tasks/{task_id}/events`（SSE，可选）

### 5.3 必增强接口
- `POST /tasks`：返回 `accepted + task_id + queue_job_id + estimated_start`
- `GET /tasks/{task_id}`：返回阶段进度、`success_rate`、终态 `partial`
- `POST /tasks/{task_id}/retry`：支持按 `source/match` 定向重试
- `GET /matches/{match_id}/items`：结构化质量字段优先输出

---

## 6. 测试与门禁（Go/No-Go）

### 6.1 自动化回归（每阶段必跑）
- 脚本：
  - `scripts/run-intelligence-regression.bat`
  - `scripts/run-all-tests.bat`
- 覆盖：
  - API 集成测试
  - 关键 Playwright E2E（创建任务、轮询、查看结果、失败诊断）
  - 回放样例对比

### 6.2 上线门禁阈值

| 指标 | 门禁值 |
|---|---|
| 任务状态准确率 | 100%（无“全失败仍 success”） |
| 创建/重试请求超时率 | <= 5% |
| 抓取成功率（HTTP） | >= 95% |
| 解析成功率（详情页） | >= 80% |
| 可用情报率（accepted） | >= 50% |
| 关键 E2E 用例通过率 | 100% |

---

## 7. 发布、灰度、回滚

### 7.1 发布顺序

1. DB 迁移（先加字段、后切读、最后清旧逻辑）
2. 后端发布（状态机、队列、超时、failure-summary）
3. 前端发布（partial 状态、失败摘要、超时与轮询策略）
4. P2 能力按 Feature Flag 灰度（SSE/AI 摘要/推荐）

### 7.2 回滚策略

- 代码回滚：按服务独立回滚，不回滚已执行迁移。
- 数据回滚：结构化字段保留，读逻辑可切回 raw 兼容模式（临时）。
- 开关回滚：关闭 SSE、推荐、AI 摘要，不影响主采集链路。

---

## 8. 角色分工（RACI，按职能）

- 后端：任务状态机、队列调度、采集链路、接口与告警
- 前端：任务页交互、状态展示、失败诊断、趋势看板
- 数据库：迁移脚本、索引优化、回滚预案
- QA：回归脚本维护、E2E 门禁、性能与稳定性测试
- 运维：worker 部署、监控告警、灰度与发布窗口控制

---

## 9. 周计划（建议排期）

- 2026-02-23 ~ 2026-03-01：完成 P0（B1~B5），通过稳定性门禁
- 2026-03-02 ~ 2026-03-08：完成 P1-1/P1-2（结构化字段 + 解析器收敛）
- 2026-03-09 ~ 2026-03-15：完成 P1-3/P1-4（精修匹配 + 去重/增量/评分/告警）
- 2026-03-16 ~ 2026-03-22：完成 P2-1/P2-2（SSE + 趋势看板）
- 2026-03-23 ~ 2026-03-29：完成 P2-3 与灰度验证（推荐/热度/AI 摘要）

---

## 10. 完成定义（Definition of Done）

- 需求：对应工作包全部勾选并有 PR 记录
- 代码：通过静态检查与单元/集成/E2E 回归
- 数据：迁移脚本可重复执行且可回滚
- 文档：接口文档、运维说明、异常排查手册已更新
- 验收：达到第 6 节门禁后方可进入上线窗口

---

## 11. 版本记录

| 版本 | 日期 | 说明 |
|---|---|---|
| v3.0 | 2026-02-20 | 合并 v1 蓝图与 v2 实施版，形成单一可执行基线 |

