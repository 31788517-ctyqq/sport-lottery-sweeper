# 情报采集管理页面 PRD + 接口清单 + 数据库草案（V2）
更新时间：2026-02-19  
适用页面：`/admin/intelligence/collection`  
关联页面：`/admin/match-data/schedule/jczq`

相关版本文案：
1. 降本可落地版：`docs/reports/情报采集管理_降本可落地版_MVP_V1.md`
2. 全功能目标态：`docs/reports/情报采集管理_全功能版_目标态_V1.md`
3. 决策对比表：`docs/reports/情报采集管理_方案决策对比表_V1.md`

## 1. 目标
基于竞彩赛程采集多源足球情报，形成“少而准”的结构化信息，按用户偏好推送到钉钉，输出模板化 PDF，提升决策准确度与用户粘性。

## 2. 已确认约束
1. 预测信息“直接存来源观点”，不做改写融合。
2. 固定采集时点：赛前 `24h / 12h / 6h / 1h`。
3. 生产架构必须是“任务队列 + 独立 Worker”。
4. 推送默认降噪，不允许信息轰炸。
5. 本模块需独立建设为“微服务 + 小容器化”部署单元，可独立发布、扩缩容、回滚。

## 3. 情报范围
### 3.1 场外信息（off_field）
1. 伤病
2. 天气
3. 主裁判
4. 战意
5. 战术
6. 主帅
7. 历史交锋
8. 主场氛围
9. 更衣室

### 3.2 预测信息（prediction）
1. 胜平负（1X2）
2. 让球胜平负（handicap_1x2）
3. 比分（correct_score）
4. 总进球（total_goals）
5. 半全场（half_full_time）

### 3.3 数据源（V1）
新浪体育、网易体育、搜狐体育、腾讯体育、央视体育、新浪微博、微信公众号、500万彩票网、天天盈球网、今日头条。

## 4. 页面 PRD（/admin/intelligence/collection）
### 4.1 页面结构
1. 顶部筛选：日期、联赛、球队关键词、来源、情报类型。
2. 赛程选择：对接 jczq 赛程，支持批量勾选。
3. 任务管理：即时采集、计划采集、重试、取消、日志。
4. 结果查看：按比赛展示来源观点、发布时间、抓取时间、置信度、原文链接。
5. 推送预览：展示最终用户将收到的摘要卡片 + 展开详情。
6. 用户订阅模板管理（新增）：配置“看什么、看多少、多久推一次、推到哪里”。

### 4.2 核心交互
1. 批量创建任务：选比赛 -> 选来源/类型 -> 创建。
2. 计划任务：选比赛 -> 选 24/12/6/1h -> 自动反推执行时间。
3. 观点直存：同场多来源并存，不覆盖。
4. 预览推送：默认只显示结论与关键证据，可展开原文。
5. 一键生成 PDF：在预览页生成模板化 PDF 并测试发送到钉钉。

## 5. “少而准”策略（含你提出的 8 点）
### 5.1 三层输出
1. 默认层：1 条结论卡（结论 + 置信度 + 风险标签）。
2. 展开层：最多 3 条关键证据（来源/时间/摘要）。
3. 深度层：完整来源观点与原文链接。

### 5.2 推送门槛
推送需同时满足：置信度、来源一致性、完整度、时效性。  
默认阈值：
1. `confidence >= 0.72`
2. 近 6 小时 >= 3 个有效来源，核心一致率 >= 60%
3. 场外覆盖率 >= 50%
4. 最近采集距开赛 <= 90 分钟

### 5.3 时点版本对比（新增）
展示 `24h -> 12h -> 6h -> 1h` 观点变化轨迹：升温、降温、反转。

### 5.4 变化触发推送（新增）
不只按固定时点推送；当“结论反转”或“置信度变化 >= 0.12”触发增量提醒。

### 5.5 稳定性分（新增）
增加 `stability_score`（最近两次及跨来源是否稳定），和置信度并列展示。

### 5.6 来源质量权重（新增）
按历史命中率、时效性、可用率动态调整 `source_weight`，低质量来源降权。

### 5.7 时效衰减（新增）
旧数据自动降权，超过阈值标记“可能过期”。

### 5.8 用户反馈闭环（新增）
用户可标记“有用/无用/过载”，用于个性化调频和模板优化。

### 5.9 赛后复盘评分（新增）
按赛果回算来源与策略表现，持续更新权重和阈值。

### 5.10 节流策略（新增）
同一场默认最多 1 条主推 + 1 条重大变更提醒；单用户每日上限可配置。

## 6. 用户可定制 + 钉钉 + PDF
### 6.1 用户可定制项
1. 订阅范围：联赛、球队、玩法、情报类型。
2. 推送频率：仅重大变化 / 每个固定时点 / 每日汇总。
3. 风险偏好：保守、均衡、进取。
4. 信息密度：极简（1结论）、标准（1+3证据）、专业（含更多细节）。
5. PDF 模板：简版、标准版、复盘版。

### 6.2 钉钉打通
1. 支持绑定个人/群机器人 webhook（含签名密钥）。
2. 支持测试消息、失败重试、告警记录。
3. 支持按用户订阅策略路由发送。

### 6.3 模板化 PDF
1. 输出结构：比赛信息、结论卡、关键证据、风险提示、来源列表、时间戳。
2. 支持品牌样式（Logo/配色/页眉页脚）。
3. 生成方式：异步任务生成，支持下载、钉钉发送、归档追溯。

## 7. 技术架构
1. API Service：任务、规则、预览、发送接口。
2. Queue（Redis/RabbitMQ）：任务缓冲。
3. Collector Worker：采集与解析。
4. Scoring Worker：置信度/稳定性/权重计算。
5. PDF Worker：模板渲染与文件输出。
6. Scheduler：24/12/6/1h 与变更触发扫描。

### 7.1 微服务边界（新增）
1. 服务名建议：`intelligence-collection-service`。
2. 领域边界：仅负责情报采集、评分、推送编排、PDF 生成，不承担用户主数据管理。
3. 对外通过 REST API 提供能力，对内通过消息队列驱动异步任务。
4. 与主系统通过 API Gateway/反向代理集成，保持统一鉴权与审计。

### 7.2 小容器化要求（新增）
1. 镜像要求：多阶段构建、非 root 用户运行、精简基础镜像。
2. 进程拆分：`api`、`collector-worker`、`scoring-worker`、`pdf-worker`、`scheduler` 分容器部署。
3. 资源建议：每容器独立 `requests/limits`，支持 HPA 按队列积压和 CPU 扩缩容。
4. 配置管理：环境变量 + Secret（钉钉 webhook/签名密钥等），严禁写死。
5. 健康检查：`/healthz`、`/readyz`，支持滚动发布与自动摘流。
6. 可观测性：结构化日志、任务链路 ID、Prometheus 指标（成功率/耗时/队列积压/推送失败率）。
7. 发布策略：灰度发布 + 快速回滚，数据库变更采用向后兼容迁移策略。

## 8. 接口清单（V2）
前缀：`/api/v1/admin/intelligence/collection`

### 8.1 采集与任务
1. `POST /tasks` 创建即时采集任务
2. `POST /schedules` 创建计划采集任务
3. `GET /tasks` 任务列表
4. `GET /tasks/{task_id}` 任务详情
5. `GET /tasks/{task_id}/logs` 任务日志
6. `POST /tasks/{task_id}/retry` 重试
7. `POST /tasks/{task_id}/cancel` 取消
8. `GET /matches/{match_id}/items` 比赛情报

### 8.2 推送与预览
9. `POST /matches/{match_id}/push-preview` 生成推送预览
10. `POST /push/tasks` 提交推送任务
11. `GET /push/tasks/{task_id}` 推送状态
12. `POST /push/tasks/{task_id}/retry` 推送重试

### 8.3 用户订阅与个性化（新增）
13. `GET /subscriptions/me` 获取我的订阅配置
14. `PUT /subscriptions/me` 更新我的订阅配置
15. `GET /subscriptions/templates` 获取默认模板
16. `POST /feedback` 提交“有用/无用/过载”反馈

### 8.4 钉钉绑定（新增）
17. `GET /channels/dingtalk/bindings` 绑定列表
18. `POST /channels/dingtalk/bindings` 新增绑定（webhook+签名）
19. `PUT /channels/dingtalk/bindings/{id}` 编辑绑定
20. `POST /channels/dingtalk/bindings/{id}/test` 测试发送
21. `DELETE /channels/dingtalk/bindings/{id}` 删除绑定

### 8.5 PDF（新增）
22. `POST /reports/pdf/render` 生成 PDF
23. `GET /reports/pdf/{report_id}` 查询渲染状态
24. `GET /reports/pdf/{report_id}/download` 下载 PDF
25. `POST /reports/pdf/{report_id}/send-dingtalk` 发送 PDF 到钉钉

## 9. 数据库草案（V2）
### 9.1 已有核心表
1. `intel_collection_task`
2. `intel_item_raw`
3. `intel_item_structured`
4. `intel_source_config`
5. `intel_push_summary`

### 9.2 新增表
1. `intel_signal_snapshot`  
按时点保存每场比赛的结论快照（confidence、stability_score、risk_level、delta）。

2. `intel_source_quality`  
来源质量评分（hit_rate、timeliness_score、availability_score、weight、last_recalculated_at）。

3. `intel_user_subscription`  
用户订阅偏好（联赛、球队、玩法、情报类型、风险偏好、推送频率、信息密度、每日上限）。

4. `intel_channel_binding`  
渠道绑定（user_id、channel=dingtalk、webhook、secret、enabled、last_test_at）。

5. `intel_pdf_report`  
PDF 渲染任务（report_id、template_code、status、file_path、checksum、created_at）。

6. `intel_push_delivery_log`  
发送日志（push_task_id、user_id、channel、payload_type(text/pdf)、status、error、retry_count）。

7. `intel_user_feedback`  
用户反馈（useful/useless/overload + comment + event_ref）。

## 10. 调度与规则
1. 固定采集：`kickoff - 24h/12h/6h/1h`
2. 变化触发：当结论反转或 `abs(confidence_delta) >= 0.12`
3. 幂等键：`match_id + source + intel_type + planned_at`
4. 过期衰减：超过设定窗口的证据自动降权

## 11. 验收标准（V2）
1. 可完成单场/批量采集，任务可追踪可重试。
2. 能看到 24/12/6/1h 时点变化轨迹与稳定性分。
3. 推送遵守门槛与节流，不达标自动降级为观察中。
4. 用户可完成订阅自定义并即时生效。
5. 钉钉可绑定、测试、真实发送并记录日志。
6. 可生成模板化 PDF，支持下载与钉钉发送。
7. 用户反馈可回流到个性化策略与来源权重调优。
8. 微服务容器可独立部署、扩缩容、灰度发布与回滚，且健康检查与监控指标齐全。

## 12. 开发顺序
1. 数据层：新增 7 张表 + 索引 + 幂等约束。
2. 任务层：采集、调度、评分、推送、PDF 五类 worker。
3. 接口层：先任务与结果，再订阅/钉钉/PDF。
4. 前端层：先采集页，再订阅配置，再推送预览与 PDF。
5. 联调回归：真实后端、真实钉钉、真实 PDF 模板。
6. 部署层（新增）：补齐 Dockerfile、compose/Helm、健康检查、监控告警、灰度与回滚脚本。

## 13. 实施清单（可勾选，V2.1）
### 13.1 P0 上线必需（7-10 天）
- [ ] 任务模型改为“按比赛拆分”：创建父任务后自动生成 match_subtask，按场次并行执行。
- [ ] 任务执行全异步：`POST /tasks` 创建后 1s 内返回 `task_id`，前端仅轮询状态，不同步等待抓取完成。
- [ ] 落地首批专用解析器：`500w`、`ttyingqiu`、`sina`、`tencent`、`weibo`，通用解析器只做兜底。
- [ ] 链接质量硬约束：只允许详情页参与高分命中，首页/栏目页/聚合页默认拦截或降权。
- [ ] 匹配规则改为“硬门槛 + 分值”：主客队词命中 + 比赛时间窗口为硬门槛，标题/正文/联赛/来源权重参与评分。
- [ ] 结果质量字段入库并前端展示：`quality_score`、`quality_pass_reason`、`quality_block_reason`、`match_hit_terms`。
- [ ] 任务日志补齐可解释信息：候选链接数、详情抓取状态码、过滤原因、入库原因、来源解析器名。
- [ ] 超时与重试策略落地：来源级超时、子任务超时、最大重试次数、失败隔离与熔断。
- [ ] 基础验收通过：指定日期（例 2026-02-10）场次覆盖率达到 >=95%，详情页占比 >=90%。

### 13.2 P1 质量收敛（5-7 天）
- [ ] 建立球队/联赛别名词典（中英文/繁简/缩写），支持热更新与版本回滚。
- [ ] 建立来源健康度面板：成功率、超时率、空结果率、平均耗时，支持自动降级低健康来源。
- [ ] 增加去重与冲突识别：同场同类观点做聚类去重，冲突观点打标并保留来源证据。
- [ ] 增加调试接口：输入 `match_id + source` 返回候选链接、打分明细与拦截原因。
- [ ] 增加质量回放能力：按任务复盘“候选 -> 过滤 -> 入库”全链路。
- [ ] 完成人工抽检流程：每日抽样验证命中质量并回灌阈值。

### 13.3 P2 运营闭环（5-7 天）
- [ ] 推送节流策略上线：每场默认 Top-N（建议 3 条），仅推“新增变化”而非全量重复。
- [ ] 用户反馈闭环上线：有用/无用/过载反馈写回评分系统。
- [ ] 运营指标看板上线：点击率、阅读完成率、反馈有效率、误命中率。
- [ ] 阈值自动建议机制上线：按近 7 天数据给出评分阈值调整建议。
- [ ] 复盘机制上线：赛后对来源与规则进行回算评分，更新 `source_weight`。

### 13.4 合规与风控（并行项）
- [ ] 数据源合规清单落库：来源授权状态、robots 规则、频控上限、禁采范围。
- [ ] 请求审计落库：来源、请求时间、响应码、重试次数、错误类型。
- [ ] 高风险来源开关：支持按来源一键停用并记录操作审计。
- [ ] 推送溯源要求：每条推送必须带来源、抓取时间、原文链接。

### 13.5 测试与上线闸门（并行项）
- [ ] API 自动化覆盖：任务创建、轮询、重试、日志、结果质量字段完整性。
- [ ] Playwright 覆盖关键链路：创建任务 -> 完成 -> 校验质量字段 -> 重试 -> 缓存失效。
- [ ] 故障注入测试：来源超时、解析失败、队列堆积、worker 崩溃恢复。
- [ ] 上线闸门标准：连续 3 天达到 KPI 阈值且无 P1 级故障。
- [ ] 预发灰度策略：先 2 个来源灰度，再逐步放量至全来源。

### 13.6 里程碑（建议）
- [ ] M1（第 1 周）：P0 完成并可在页面稳定看到可解释结果。
- [ ] M2（第 2 周）：P1 完成，命中率与内容质量显著提升。
- [ ] M3（第 3 周）：P2 完成，推送与反馈闭环上线。

## 14. 补充要求（按比赛抓取 + 专用解析器 + 质量字段展示）
### 14.1 数据模型补充（最小新增）
1. `intel_item_structured` 建议新增字段：`quality_score`、`quality_pass_reason`、`quality_block_reason`、`match_hit_terms(json)`、`source_parser`、`is_article_page`、`content_length`。
2. `intel_collection_task` 建议新增：`total_matches`、`success_matches`、`failed_matches`、`coverage_rate`。
3. 新增 `intel_candidate_log`（或扩展现有日志表）：`task_id`、`match_id`、`source`、`candidate_url`、`http_status`、`score`、`decision`、`reason`、`created_at`。

### 14.2 接口补充（最小可用）
1. `POST /tasks`：立即返回 `task_id`，并返回预计完成时间与轮询建议间隔。
2. `GET /tasks/{task_id}`：返回总进度、按比赛进度、失败原因聚合。
3. `GET /tasks/{task_id}/logs`：支持 `match_id`、`source`、`decision` 条件过滤。
4. `GET /matches/{match_id}/items`：返回质量字段与“采纳/过滤原因”。
5. `GET /debug/match-candidates`：用于调参，返回候选链接和评分明细。

### 14.3 指标基线与阈值（建议初始值）
1. 覆盖率：`coverage_rate >= 0.95`。
2. 详情页占比：`article_page_ratio >= 0.90`。
3. 高质量命中率（人工抽检）：`>= 0.80`。
4. 任务成功率：`>= 0.98`。
5. 创建任务接口 P95：`< 1s`。

### 14.4 风险与应急预案
1. 外部来源结构变更：启用来源级降级与兜底策略，避免全链路失败。
2. 队列积压：自动扩容 worker，超阈值后暂停低优先级任务。
3. 大面积超时：触发熔断并降级为仅保留高健康来源。
4. 误推风险：未达推送门槛自动降级为“仅展示不推送”。
