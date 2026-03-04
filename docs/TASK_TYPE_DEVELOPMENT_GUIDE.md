# 任务类型开发说明文档

## 文档版本
- 版本：v1.0
- 创建日期：2026-02-04
- 适用系统：体育彩票数据清扫系统 v0.1.53+

## 概述

本文档详细说明系统中四种核心任务类型的开发原理、执行目标、实现路线图，以及与运维人员的交互机制和评估方法。

## 任务类型架构

| 任务类型 | 代码标识 | 核心服务 | 主要职责 |
|----------|----------|----------|----------|
| **数据采集** | `DATA_COLLECTION` | DataCollectionService | 从外部源获取原始数据 |
| **数据清洗** | `DATA_CLEANING` | DataProcessor | 清洗验证原始数据 |
| **数据分析** | `DATA_ANALYSIS` | DataAnalysisService | 统计分析生成洞察 |
| **报告生成** | `REPORT_GENERATION` | ReportGenerationService | 生成结构化报告 |

---

## 1. 数据采集任务 (DATA_COLLECTION)

### 1.1 执行原理

**核心流程**：
```python
# 主要调用链
task_scheduler_service.py → DataCollectionService.fetch_api_data() → aiohttp.ClientSession
                                     ↓
                           pandas.read_excel/csv/json (文件导入)
```

**关键技术点**：
- 异步HTTP客户端：`aiohttp` 实现高并发数据拉取
- 文件导入：`pandas` 处理CSV/Excel/JSON格式
- 数据源配置：URL、请求头、超时、认证信息
- 增量采集：基于时间戳或版本号的差量更新

### 1.2 执行目标

- **数据覆盖**：比赛信息、赔率数据、球队情报、历史统计
- **时效性**：支持分钟级实时采集和定时批量采集
- **可靠性**：网络异常重试、断点续传、数据完整性校验
- **扩展性**：插件化数据源适配器，支持新增API快速接入

### 1.3 任务执行路线图

```
任务启动 → 读取数据源配置 → 建立网络连接 → 发送请求获取数据 → 
数据预处理(格式转换) → 数据质量初检 → 入库存储 → 
更新数据源状态(最后更新时间/记录数) → 记录执行日志 → 任务完成
```

**关键节点验证**：
- 网络连通性检查
- 响应状态码验证 (200/201成功)
- 数据结构schema验证
- 必填字段完整性检查

### 1.4 开发要点

**配置文件结构**：
```json
{
  "source_id": "DS001",
  "source_name": "500彩票网",
  "source_type": "api",
  "api_url": "https://api.example.com/matches",
  "request_method": "GET",
  "headers": {"Authorization": "Bearer token"},
  "timeout": 30,
  "retry_times": 3,
  "cron_expression": "0 */2 * * *"
}
```

**错误处理策略**：
- HTTP错误：4xx客户端错误记录详情，5xx服务端错误重试
- 解析错误：跳过无效记录，记录错误日志
- 超时处理：指数退避重试机制

---

## 2. 数据清洗任务 (DATA_CLEANING)

### 2.1 执行原理

**核心流程**：
```python
# 主要调用链
task_scheduler_service.py → DataProcessor.clean_and_validate_datetime() → 
                           DataCollectionService.validate_data_quality() → 数据质量报告
```

**清洗规则引擎**：
- 字段映射：源字段名 → 标准字段名
- 类型转换：字符串 → 日期/数值/布尔值
- 值域验证：SP值(0-100)、概率(0-1)、日期有效性
- 去重逻辑：基于比赛ID+数据源+时间戳复合主键

### 2.2 执行目标

- **数据标准化**：统一字段命名、数据类型、时间格式
- **质量保证**：消除脏数据、修复格式错误、填补合理缺值
- **一致性**：跨数据源同场比赛信息对齐
- **可追溯**：保留原始数据和清洗日志

### 2.3 任务执行路线图

```
接收原始数据集 → 字段映射转换 → 数据类型强制转换 → 
缺失值检测与处理 → 异常值识别与修正 → 重复记录去重 → 
数据关联性验证 → 生成清洗报告 → 更新数据状态 → 推送下游
```

**质量检查点**：
- 必填字段缺失率 < 1%
- 数值字段越界率 < 0.1%
- 重复记录率 < 0.01%
- 时间逻辑一致性 100%

### 2.4 开发要点

**清洗规则配置**：
```python
CLEANING_RULES = {
    'match_time': {
        'required': True,
        'type': 'datetime',
        'format': '%Y-%m-%d %H:%M:%S',
        'validator': lambda x: x > datetime.now()
    },
    'home_win_sp': {
        'required': True,
        'type': 'float',
        'range': [0.01, 100.0],
        'precision': 2
    }
}
```

**数据修正策略**：
- 明显错误：直接使用业务规则修正
- 边界值：使用上下限值替换
- 缺失值：标记状态，不自动填充

---

## 3. 数据分析任务 (DATA_ANALYSIS)

### 3.1 执行原理

**核心流程**：
```python
# 主要调用链
task_scheduler_service.py → DataAnalysisService.analyze_sp_distribution() → 
                           SQLAlchemy查询 → 统计计算 → 图表数据生成
```

**分析算法库**：
- 描述统计：`statistics.mean()`, `statistics.stdev()`
- 分布分析：直方图、箱线图、概率密度估计
- 时间序列：移动平均、趋势分析、季节性分解
- 关联分析：相关系数、卡方检验、回归分析

### 3.2 执行目标

- **模式识别**：发现SP值分布规律、变盘时机特征
- **预测建模**：基于历史数据构建简单预测模型
- **对比分析**：不同公司、联赛、时间段的差异化分析
- **洞察生成**：量化指标转业务可理解的结论

### 3.3 任务执行路线图

```
加载清洗后数据集 → 应用分析模型(分布/关联/时序) → 
计算统计指标(均值/方差/分位数) → 生成图表坐标数据 → 
执行相关性分析 → 识别异常模式 → 保存分析结果 → 
生成分析摘要 → 推送可视化组件
```

**分析维度**：
- **时间维度**：赛季内、月度、周度趋势
- **空间维度**：联赛级别、地区分布
- **对象维度**：球队、球员、裁判表现
- **指标维度**：胜率、赔率、投注量关联

### 3.4 开发要点

**分析模板结构**：
```python
ANALYSIS_TEMPLATES = {
    'sp_distribution': {
        'metrics': ['mean', 'median', 'std', 'skewness'],
        'bins': 20,
        'chart_type': 'histogram'
    },
    'volatility_analysis': {
        'window_size': 5,  # 5期移动窗口
        'threshold': 0.15,  # 15%变化阈值
        'alert_enabled': True
    }
}
```

**性能优化**：
- 增量计算：仅处理新增/变更数据
- 采样策略：大数据集使用分层抽样
- 并行计算：多核CPU并行处理不同分析维度

---

## 4. 报告生成任务 (REPORT_GENERATION)

### 4.1 执行原理

**核心流程**：
```python
# 主要调用链
task_scheduler_service.py → ReportGenerationService.generate_match_report() → 
                           Jinja2模板渲染 → LLM洞察生成 → 文件导出
```

**报告引擎**：
- 模板引擎：`Jinja2` 实现动态内容填充
- 图表集成：`matplotlib`/`plotly` 生成嵌入式图表
- LLM增强：QWen API生成自然语言分析与建议
- 多格式输出：PDF/HTML/Markdown/JSON

### 4.2 执行目标

- **结构化呈现**：将复杂分析转为清晰可读的报告
- **智能洞察**：AI辅助识别关键模式和异常信号
- **决策支持**：提供可操作的投注建议与风险提示
- **自动化分发**：定时推送或事件触发报告发送

### 4.3 任务执行路线图

```
收集分析结果数据集 → 调用LLM生成文本洞察 → 填充报告模板变量 → 
渲染图表并嵌入 → 样式美化与格式化 → 导出目标格式文件 → 
记录报告元数据(大小/页数/生成时间) → 分发报告 → 任务完成
```

**报告类型**：
- **赛前分析**：球队实力对比、历史交锋、赔率趋势
- **临场监控**：实时变盘预警、异常波动提醒
- **赛后复盘**：预测准确率评估、模式验证
- **周期总结**：周/月度投注策略效果回顾

### 4.4 开发要点

**模板设计原则**：
```html
<!-- 报告模板示例 -->
<h1>{{ match.home_team }} vs {{ match.away_team }}</h1>
<div class="analysis-section">
  <h2>SP值分布分析</h2>
  <img src="{{ chart_urls.sp_distribution }}" alt="SP分布图">
  <p>{{ llm_insights.key_findings }}</p>
</div>
```

**LLM集成配置**：
```python
LLM_CONFIG = {
    'provider': 'qwen',
    'model': 'qwen-turbo',
    'temperature': 0.3,
    'max_tokens': 1000,
    'prompt_template': '基于以下数据分析结果，生成简洁的投资建议...'
}
```

---

## 5. 运维交互机制

### 5.1 任务生命周期管理

**创建阶段**：
- 前端表单：`TaskConsole.vue` 提供任务创建界面
- 后端验证：`task_scheduler_service.py` 校验参数合法性
- 持久化：`tasks` 表存储任务配置和调度信息

**执行阶段**：
- 状态跟踪：`TaskStatus` 枚举管理任务状态流转
- 进度反馈：WebSocket实时推送执行进度
- 日志流式：分块读取日志文件，支持暂停/继续

**监控阶段**：
- 仪表盘：`DashboardView.vue` 展示系统整体健康状况
- 告警机制：成功率/耗时阈值触发邮件/Slack通知
- 干预操作：手动停止、重试、参数调整

### 5.2 运维操作接口

| 操作类型 | 前端组件 | 后端API | 权限要求 |
|----------|----------|---------|----------|
| 任务创建 | TaskConsole.vue | POST /api/v1/crawler/tasks | admin |
| 任务启停 | TaskConsole.vue | PUT /api/v1/crawler/tasks/{id}/status | operator |
| 日志查看 | LogViewer.vue | GET /api/v1/crawler/tasks/{id}/logs | viewer |
| 批量操作 | TaskConsole.vue | DELETE /api/v1/crawler/tasks/batch | admin |
| 统计查询 | DashboardView.vue | GET /api/v1/crawler/stats | viewer |

### 5.3 实时通信机制

**WebSocket事件**：
```javascript
// 前端监听
socket.on('task_update', (data) => {
  updateTaskStatus(data.taskId, data.status);
});

socket.on('log_chunk', (data) => {
  appendLogContent(data.content);
});
```

**后端推送逻辑**：
```python
# task_scheduler_service.py
await websocket.send_json({
    'type': 'task_update',
    'task_id': task.id,
    'status': task.status,
    'progress': task.progress
})
```

---

## 6. 执行结果评估体系

### 6.1 核心绩效指标 (KPI)

| 指标类别 | 具体指标 | 计算公式 | 目标值 |
|----------|----------|----------|--------|
| **可靠性** | 任务成功率 | 成功次数/总执行次数×100% | ≥95% |
| **效率** | 平均执行耗时 | 总耗时/成功次数 | 数据采集<60s，分析<120s |
| **产出** | 数据处理量 | 成功处理的记录数 | 按需设定基线 |
| **质量** | 数据质量分数 | (1-错误率)×100 | ≥98% |

### 6.2 数据质量评估矩阵

| 质量维度 | 评估方法 | 权重 | 评分标准 |
|----------|----------|------|----------|
| **完整性** | 必填字段缺失率 | 30% | 缺失率<1%得满分 |
| **准确性** | 数值范围合理性 | 25% | 越界率<0.1%得满分 |
| **一致性** | 跨源数据匹配度 | 25% | 匹配率>99%得满分 |
| **时效性** | 数据延迟时间 | 20% | 延迟<5分钟得满分 |

### 6.3 可视化评估工具

**实时监控面板**：
- 任务状态热力图：按类型和状态聚合显示
- 执行时长趋势图：24小时滚动窗口
- 错误类型饼图：TOP5错误原因占比
- 数据流量监控：入库TPS和队列积压

**历史分析报表**：
- 周度/月度执行报告：KPI达成情况
- 根因分析报告：高频错误模式挖掘
- 容量规划报告：资源使用趋势预测

### 6.4 告警与自愈

**告警规则**：
```yaml
alerts:
  - name: low_success_rate
    condition: success_rate < 90% for 10m
    severity: warning
    actions: [email, slack]
  
  - name: high_execution_time
    condition: avg_duration > threshold for 5m
    severity: info
    actions: [slack]
```

**自愈策略**：
- 自动重试：瞬时故障指数退避重试
- 降级处理：非关键任务失败时跳过不影响主流程
- 资源扩容：CPU/内存超阈值时自动水平扩容

---

## 7. 开发最佳实践

### 7.1 代码组织原则

**服务层职责分离**：
```
backend/
├── services/
│   ├── data_collection_service.py    # 数据采集业务逻辑
│   ├── data_analysis_service.py      # 数据分析算法实现
│   ├── report_generation_service.py  # 报告生成与渲染
│   └── task_scheduler_service.py     # 任务调度与监控
├── processors/
│   └── data_processor.py             # 数据清洗与验证
└── models/
    └── crawler_tasks.py              # 任务数据模型
```

**配置外部化**：
- 任务参数通过数据库配置，支持运行时调整
- 算法参数使用YAML配置文件管理
- 第三方服务凭证存储在环境变量或密钥管理系统

### 7.2 测试策略

**单元测试覆盖**：
- 服务层：业务逻辑正确性验证
- 处理器：数据清洗规则准确性测试
- 模型层：数据库操作和约束验证

**集成测试场景**：
- 端到端任务流：创建→执行→监控→完成
- 异常恢复：网络中断、数据异常、资源不足
- 性能基准：大数据量下的执行时间和资源消耗

**测试数据管理**：
- 使用独立的测试数据库
- 准备标准化的测试数据集
- 模拟外部API的Mock服务

### 7.3 部署与运维

**容器化部署**：
```dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ ./backend/
WORKDIR /app
CMD ["python", "backend_start.py"]
```

**监控集成**：
- Prometheus指标暴露：任务执行次数、耗时、错误率
- Grafana仪表盘：可视化系统健康状况
- ELK日志收集：集中化日志分析和检索

---

## 8. 扩展与演进

### 8.1 新任务类型扩展

**开发流程**：
1. 在`TaskType`枚举中添加新类型
2. 实现对应的Service类和处理逻辑
3. 更新前端表单选项和验证逻辑
4. 添加专门的评估指标和监控面板

**示例：机器学习预测任务**
```python
class MLPredictionService:
    async def train_model(self, dataset):
        # 模型训练逻辑
        pass
    
    async def predict(self, match_data):
        # 预测逻辑
        pass
```

### 8.2 技术演进路线

**短期优化 (1-3个月)**：
- 提升数据采集并发性能
- 完善数据质量自动修复机制
- 增强报告模板的灵活性

**中期规划 (3-6个月)**：
- 引入实时流处理 (Apache Kafka + Flink)
- 集成更多AI分析模型
- 实现跨任务依赖编排

**长期愿景 (6-12个月)**：
- 构建统一的数据湖和数据仓库
- 实现智能化的任务调优和资源配置
- 支持多云部署和边缘计算场景

---

## 附录

### A. 相关代码文件索引

| 功能模块 | 主要文件 | 关键类/函数 |
|----------|----------|-------------|
| 任务调度 | `backend/services/task_scheduler_service.py` | `TaskSchedulerService` |
| 数据采集 | `backend/services/data_collection_service.py` | `DataCollectionService` |
| 数据清洗 | `backend/processors/data_processor.py` | `DataProcessor` |
| 数据分析 | `backend/services/data_analysis_service.py` | `DataAnalysisService` |
| 报告生成 | `backend/services/report_generation_service.py` | `ReportGenerationService` |
| 前端控制台 | `frontend/src/views/admin/crawler/TaskConsole.vue` | 任务管理界面 |

### B. 常见问题排查

**Q1: 数据采集任务频繁失败**
- 检查网络连通性和API限流策略
- 验证数据源配置参数的正确性
- 查看详细的错误日志和网络抓包

**Q2: 数据清洗质量不达标**
- 检查清洗规则配置是否过于严格
- 分析原始数据的质量问题
- 调整异常值处理策略

**Q3: 报告生成耗时过长**
- 优化LLM调用频率和缓存策略
- 检查图表生成的内存使用情况
- 考虑异步生成和预渲染机制

### C. 联系方式

- 技术支持：tech-support@sport-lottery.com
- 紧急联系：on-call@sport-lottery.com
- 文档维护：docs@sport-lottery.com

---

**文档结束**

*本文档将根据系统迭代持续更新，如有疑问请联系技术团队。*