# 北单三维筛选页操作文案（评审版）

更新时间：2026-02-15  
适用页面：`/admin/beidan-filter`

## 1. 文档来源（项目内检索）
- `frontend/src/views/admin/BeidanFilterPanel.vue`
- `frontend/src/views/admin/components/FilterCardHeader.vue`
- `frontend/src/views/admin/components/FilterSection.vue`
- `frontend/src/views/admin/components/StrategySection.vue`
- `frontend/src/views/admin/components/StatsCard.vue`
- `frontend/src/views/admin/components/ResultsSection.vue`
- `frontend/src/views/admin/components/AnalysisDialog.vue`
- `frontend/src/components/admin/MultiStrategyManager.vue`
- `backend/app/api_v1/endpoints/beidan_filter_api.py`
- `backend/app/api_v1/endpoints/multi_strategy_api.py`
- `BEIDAN_FILTER_MANUAL_TEST_CHECKLIST.md`
- `frontend/interface_test_guide.md`
- `docs/北单三维筛选器前端页面文案与接口说明.md`
- `docs/北单过滤功能开发计划.md`

## 2. 页面操作总流程（用户视角）
1. 进入页面或者刷新页面，自动加载最新期号的比赛数据、其它条件的date_time默认加载最新比赛期号；。
2. 用户可通过三维条件（ΔP、ΔWP、P-Tier）筛选后生成当前策略或者保存策略。
3. 点击“生成当前策略”执行筛选，生成“当前策略”，策略筛选卡片中会多一个“当前策略”，在策略筛选卡片中点击当前策略，进行逻辑匹配并把结果展示在统计与结果卡片中。
4. 可保存当前条件为命名策略，后续在“策略筛选”中快速复用。
5. 可导出当前结果（Excel/CSV/JSON），可点击分析按钮进入“分析弹窗”。
6. 可进入“多策略管理”执行组合策略、定时任务、即时执行。

## 3. 页面模块文案（建议稿）

### 3.1 页头区（FilterCardHeader）
- 页面标题：`三维精算筛选器`
- 页面副标题：`基于 ΔP / ΔWP / P-Tier 的联动筛选`
- 实时统计：`实时匹配 {N} 场`
- 按钮：`获取实时数据`
- 按钮：`显示P级规则`
- 入口按钮：`多策略管理`

#### 页头操作反馈文案
- 成功：`实时数据已更新，共匹配 {N} 场`
- 失败（通用）：`实时数据获取失败，请稍后重试`
- 网络异常：`网络连接异常，请检查网络后重试`
- 401：`登录已过期，请重新登录`
- 403：`权限不足，请联系管理员`
- 5xx：`服务暂时不可用，请稍后再试`

### 3.2 筛选区（FilterSection）
- 分组标题：`实力等级差 ΔP`
- 分组标题：`赢盘等级差 ΔWP`
- 分组标题：`一赔稳定性 P-Tier`
- 分组标题：`其他条件`
- 字段：`联赛筛选`
- 字段：`期号(date_time)`
- 字段：`日期范围`
- 分组标题：`策略筛选`
- 字段：`排序方式`
- 字段：`排序顺序`
- 字段：`应用降级规则`
- 预览提示：`排序预览：P级降序 -> ΔWP降序`

#### 示例策略区
- 按钮：`强势正路`
- 按钮：`冷门潜质`
- 按钮：`均衡博弈`
- 提示：`示例策略仅加载条件，不会自动执行筛选`

#### 操作按钮
- 主按钮：`生成当前策略`
- 次按钮：`重置`
- 成功按钮：`保存策略`
- 次按钮：`管理策略`

#### 筛选区反馈文案
- 三维为空时：`三维筛选条件为空，未生成“当前策略”。请先设置筛选条件。`
- 加载示例策略：`请手动点击“生成当前策略”执行筛选。`
- 重置完成：`筛选条件已重置，“当前策略”已移除。`

### 3.3 策略区（StrategySection）
- 标题：`策略筛选`
- 下拉占位：`请选择策略`
- 按钮：`刷新`
- 列表标题：`策略列表`
- 选中标识：`已选`
- 临时标识：`NEW`
- 空列表：`暂无已保存策略`
- 详情空态：`选择策略后将显示详情`

#### 策略管理弹窗文案
- 弹窗标题：`管理筛选策略`
- 列：`策略名称` / `条件摘要` / `操作`
- 操作：`修改` / `删除`
- 编辑弹窗标题：`修改策略`
- 输入标签：`策略名称`
- 输入占位：`请输入新策略名称`
- 按钮：`取消` / `保存修改`

#### 策略反馈文案
- 保存成功：`策略保存成功，正在刷新策略列表...`
- 同名冲突：`策略“{name}”已存在，请更换名称`
- 删除成功：`删除成功`
- 删除失败：`删除失败：{reason}`
- 修改成功：`策略修改成功`
- 示例策略不可改删：`示例策略不能修改或删除`

### 3.4 统计区（StatsCard）
- 显示条件：已执行过策略筛选
- 统计项建议文案：
  - `总场次`
  - `ΔP命中场次`
  - `ΔWP命中场次`
  - `P-Tier命中场次`
- 无设置提示：`未设置`

### 3.5 结果区（ResultsSection）
- 卡片标题：`筛选结果`
- 按钮：`导出Excel` / `导出CSV` / `显示统计（或隐藏统计）`
- 空状态：`没有符合场次`
- 操作列按钮：`分析`
- 分页文案：`共 {N} 条`

#### 结果区反馈文案
- 筛选成功：`筛选完成，共找到 {N} 场符合条件的比赛`
- 无结果提示：`暂无符合条件的比赛数据`
- 导出前校验：`没有数据可导出，请先进行筛选操作`
- 导出成功：`成功导出 {N} 条数据到 {FORMAT} 文件`
- 导出失败：`导出失败：{reason}`

### 3.6 分析弹窗（AnalysisDialog）
- 弹窗标题：`比赛分析`
- 分区标题：
  - `比赛基本信息`
  - `球队实力对比`
  - `赔率对比分析`
  - `历史交锋`
  - `数据源信息`
- 空数据提示：`暂无原始数据，请先抓取并入库`

### 3.7 多策略管理（MultiStrategyManager）
- 标题：`多策略筛选配置`
- 字段：`选择策略` / `执行频率` / `Cron表达式` / `消息格式` / `钉钉通知`
- 按钮：`保存配置` / `刷新任务` / `立即执行`
- 列表标题：`我的定时任务`
- 历史标题：`执行历史`
- 常见反馈：
  - `请填写完整的配置信息`
  - `请先选择策略`
  - `多策略配置保存成功`
  - `策略执行成功`

## 4. 接口映射（以当前代码为准）

### 4.1 北单筛选页接口
- `GET /api/v1/beidan-filter/latest-date-times`
- `GET /api/v1/beidan-filter/real-time-count`
- `POST /api/v1/beidan-filter/advanced-filter`
- `GET /api/v1/beidan-filter/strategies`
- `POST /api/v1/beidan-filter/strategies`
- `DELETE /api/v1/beidan-filter/strategies/{id}`

### 4.2 多策略接口
- `GET /api/multi-strategy/config?user_id={user}`
- `POST /api/multi-strategy/config`
- `POST /api/multi-strategy/execute`
- `POST /api/multi-strategy/toggle-task/{user_id}`
- `DELETE /api/multi-strategy/config/{task_id}`

## 5. 待完善逻辑清单（用于下一步开发）
1. `AnalysisDialog` 里大量统计字段目前为前端默认占位值，需后端补齐真实分析数据。
2. `Excel` 导出目前为 CSV 内容 + `.xlsx` 文件名，需改为真实 Excel 文件流。
3. “应用降级规则”开关目前未明确贯穿后端筛选规则，需确认并落地业务逻辑。
4. 策略详情摘要存在“旧结构/新结构”兼容分支，建议统一策略数据结构。
5. 多策略管理依赖用户认证与任务表，建议补充健康检查与初始化自检提示。
6. 部分旧文档中的接口路径和交互流程已过时（如旧版 `/api/filter`、dropdown保存策略），以本页映射为准。

## 6. 发布验收建议（文案维度）
1. 所有成功/失败提示统一语气：短句、可执行、避免技术术语堆叠。
2. 所有空状态都要给下一步操作建议（如“去设置筛选条件”“去抓取数据”）。
3. 错误文案区分：网络、鉴权、权限、服务异常四类。
4. 对“示例策略”和“当前策略”要有明确解释，避免用户误解“为什么没立即出结果”。

---

如果你确认这版文案方向，我下一步可以直接按这份稿子把页面中的现有提示文案统一改成可发布版本（包括按钮、提示、弹窗、空状态、错误文案）。
