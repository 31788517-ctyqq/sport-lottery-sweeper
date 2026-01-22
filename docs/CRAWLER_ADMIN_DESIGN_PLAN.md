# 爬虫后台管理模块设计规划文档

## 1. 概述
本文档基于项目现状与需求，设计爬虫后台管理模块的目录结构与功能规划，限定为 **4 个子菜单**，覆盖从配置、监控、调度到数据分析的全流程管理，确保模块职责清晰、易于开发与维护。

---

## 2. 子菜单目录结构
采用模块化思路，将功能划分为以下 4 个子菜单：

### 2.1 菜单导航（YAML格式）
```yaml
爬虫管理:
  icon: 🕷️
  path: /admin/crawler
  children:
    - title: 源配置
      icon: 📋
      path: /admin/crawler/source-config
    - title: 数据源管理
      icon: 🌐
      path: /admin/crawler/data-source
    - title: 任务调度
      icon: ⚙️
      path: /admin/crawler/task-scheduler
    - title: 数据情报
      icon: 📊
      path: /admin/crawler/data-intelligence
```

---

## 3. 子菜单功能规划

### 3.1 源配置
**功能定位**：统一管理爬虫数据源的参数与策略，支持全局与单源差异化配置。

#### 核心功能
- **全局参数配置**：
  - 默认请求头、超时、重试次数、代理池策略
  - 公共 User-Agent 列表与轮换规则
- **单源参数配置**：
  - 针对特定网站的抓取频率、深度、页面解析规则
  - 自定义请求参数与认证信息（如 Cookie、Token）
- **配置版本管理**：
  - 保存历史配置快照，支持一键回滚
- **导入/导出**：
  - YAML/JSON 格式批量导入或导出配置

#### 界面原型
- 左侧树形结构列出所有数据源
- 右侧表单编辑参数，支持 JSON 高亮显示
- 顶部操作栏：新增、复制、删除、导入、导出、回滚

#### 操作流程
1. 选择数据源 → 2. 加载/编辑配置 → 3. 校验合法性 → 4. 保存并生效

#### 按钮集合
- 新增源、复制配置、删除、保存、测试连接、导入、导出、回滚

---

### 3.2 数据源管理
**功能定位**：监控数据源可用性与性能，提供健康检查与统计分析。

#### 核心功能
- **数据源列表**：
  - 显示名称、状态（在线/离线）、最近抓取时间、成功率
- **健康检查**：
  - 实时检测响应时间、状态码、内容完整性
  - 异常自动告警（邮件/企业微信）
- **性能分析**：
  - 抓取耗时趋势图（近 24h/7d）
  - 成功率与失败原因分布
- **批量操作**：
  - 批量启用/停用、批量测试、批量刷新缓存

#### 界面原型
- 表格展示数据源列表，支持排序与筛选
- 详情抽屉：健康指标图表 + 日志预览
- 顶部筛选栏：按状态、类型、关键字过滤

#### 操作流程
1. 进入列表 → 2. 查看状态/指标 → 3. 点击检查/分析 → 4. 处理异常或调整策略

#### 按钮集合
- 刷新、批量测试、批量启用、批量停用、查看日志、导出报告

---

### 3.3 任务调度
**功能定位**：管理爬虫任务的执行计划，支持定时与手动触发。

#### 核心功能
- **任务列表**：
  - 显示任务名称、关联数据源、Cron 表达式、下次执行时间、状态
- **定时调度**：
  - 可视化 Cron 编辑器（支持表达式与图形化选择）
  - 支持一次性、循环、依赖触发（上游任务完成后执行）
- **手动触发**：
  - 即时启动任务，支持参数覆盖（调试模式）
- **执行日志**：
  - 实时日志流、历史执行记录、失败原因追溯
- **并发控制**：
  - 设置同一数据源最大并发数，防止封禁

#### 界面原型
- 列表 + 甘特图展示任务时间线
- 右侧抽屉：Cron 编辑器 + 参数覆盖表单
- 顶部操作栏：新增、立即执行、暂停、恢复、删除

#### 操作流程
1. 创建/编辑任务 → 2. 设置调度规则 → 3. 启用 → 4. 监控执行状态与日志

#### 按钮集合
- 新增、编辑、立即执行、暂停、恢复、删除、查看日志、复制

---

### 3.4 数据情报
**功能定位**：汇总与分析抓取结果，提供多维度统计与洞察。

#### 核心功能
- **数据总览**：
  - 今日/累计抓取条目数、成功率、异常分布
- **多维度筛选**：
  - 按时间范围、数据源、数据类型、状态过滤
- **趋势分析**：
  - 抓取量趋势图、错误类型变化曲线
- **批量操作**：
  - 导出选中数据为 CSV/Excel
  - 标记无效数据、重新抓取指定条目
- **异常预警**：
  - 连续失败告警、数据量骤降提醒

#### 界面原型
- 顶部 KPI 卡片（抓取量、成功率、异常数）
- 中间图表区：折线图 + 饼图
- 下方数据表格：支持分页、排序、筛选
- 侧边栏：快速筛选器与导出选项

#### 操作流程
1. 进入情报页 → 2. 查看 KPI 与趋势 → 3. 筛选/分析数据 → 4. 导出或处理异常

#### 按钮集合
- 刷新、导出、批量标记、重新抓取、筛选、重置

---

## 4. 技术实现方案

### 4.1 前端结构
```
frontend/src/views/admin/crawler/
├── SourceConfig.vue         # 源配置
├── DataSource.vue           # 数据源管理
├── TaskScheduler.vue        # 任务调度
└── DataIntelligence.vue     # 数据情报

frontend/src/api/
├── crawlerConfig.js         # 源配置相关 API
├── crawlerSource.js         # 数据源管理 API
├── crawlerTask.js           # 任务调度 API
└── crawlerIntelligence.js   # 数据情报 API
```

### 4.2 后端 API 示例（Python风格）
```python
# 源配置
GET    /api/admin/crawler/config
POST   /api/admin/crawler/config
PUT    /api/admin/crawler/config/{id}
DELETE /api/admin/crawler/config/{id}

# 数据源管理
GET    /api/admin/crawler/sources
GET    /api/admin/crawler/sources/{id}/health
PUT    /api/admin/crawler/sources/{id}/status

# 任务调度
GET    /api/admin/crawler/tasks
POST   /api/admin/crawler/tasks
PUT    /api/admin/crawler/tasks/{id}
POST   /api/admin/crawler/tasks/{id}/trigger
GET    /api/admin/crawler/tasks/{id}/logs

# 数据情报
GET    /api/admin/crawler/intelligence/stats
GET    /api/admin/crawler/intelligence/data
GET    /api/admin/crawler/intelligence/export
```

### 4.3 UI 设计规范
```css
:root {
  --primary-color: #1890ff;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --error-color: #f5222d;
  --bg-color: #f5f7fa;
  --text-primary: #333;
  --card-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
```
- PC ≥1024px：左右布局，侧边栏固定
- 平板 768-1023px：上下布局，可折叠菜单
- 移动 <768px：抽屉式菜单，全屏表单

---

## 5. 总结
本规划通过 **源配置 → 数据源管理 → 任务调度 → 数据情报** 四层递进结构，实现爬虫全生命周期的可视化管理。各子菜单职责单一、交互直观，配合统一的技术栈与响应式设计，可快速落地并支持后续扩展。