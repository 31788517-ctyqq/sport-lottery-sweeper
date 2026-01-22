# 情报管理模块开发指南

> **项目名称**: Sport Lottery Sweeper (体育彩票扫描系统)  
> **文档版本**: v1.0  
> **更新时间**: 2026-01-21  
> **适用对象**: 后端开发工程师、前端开发工程师、系统架构师

## 📋 目录

- [1. 模块概述](#1-模块概述)
- [2. 功能架构设计](#2-功能架构设计)
  - [2.1 信息筛选模块](#21-信息筛选模块)
  - [2.2 信息采集模块](#22-信息采集模块)
  - [2.3 情报模型模块](#23-情报模型模块)
  - [2.4 情报权重模块](#24-情报权重模块)
  - [2.5 情报图谱模块](#25-情报图谱模块)
- [3. 数据库设计](#3-数据库设计)
  - [3.1 核心数据表](#31-核心数据表)
  - [3.2 关系模型](#32-关系模型)
  - [3.3 枚举类型](#33-枚举类型)
- [4. API接口设计](#4-api接口设计)
  - [4.1 情报管理API](#41-情报管理api)
  - [4.2 情报筛选API](#42-情报筛选api)
  - [4.3 情报分析API](#43-情报分析api)
- [5. 前端组件设计](#5-前端组件设计)
  - [5.1 页面结构](#51-页面结构)
  - [5.2 组件清单](#52-组件清单)
  - [5.3 数据流设计](#53-数据流设计)
- [6. 任务调度设计](#6-任务调度设计)
  - [6.1 定时任务](#61-定时任务)
  - [6.2 异步处理](#62-异步处理)
- [7. 开发指南与实现要点](#7-开发指南与实现要点)
  - [7.1 后端实现要点](#71-后端实现要点)
  - [7.2 前端实现要点](#72-前端实现要点)
  - [7.3 数据迁移指南](#73-数据迁移指南)
- [8. 测试与部署](#8-测试与部署)
  - [8.1 单元测试](#81-单元测试)
  - [8.2 集成测试](#82-集成测试)
  - [8.3 部署配置](#83-部署配置)

---

## 1. 模块概述

### 1.1 模块定位

情报管理模块是足球预测系统的核心信息支撑模块，负责汇集、整理足球比赛相关情报信息，为AI预测模型提供多维度数据参考。模块不仅仅是信息存储，更是信息资产化的关键步骤。

### 1.2 核心目标

1. **信息汇集**: 整合多渠道足球信息源（爬虫、手工录入、API接口）
2. **信息筛选**: 对原始信息进行质量评估和筛选过滤
3. **信息分析**: 提取情报特征，计算权重，生成可视化图谱
4. **信息应用**: 为AI预测模型提供高质量特征数据

### 1.3 情报分类体系

情报主要分为两大类：

#### A. 赛事场外信息
- **伤病信息**: 球员伤病情况、恢复时间
- **天气信息**: 比赛当日天气、温度、湿度、风向
- **主裁判信息**: 主裁判执法记录、执法风格
- **战意分析**: 球队比赛动机、排名压力、杯赛重要性
- **战术分析**: 战术打法、阵型布置、人员配置
- **主帅信息**: 主教练执教风格、历史战绩
- **历史交锋**: 两队历史对战记录
- **主场氛围**: 主场球迷气氛、场馆特点
- **更衣室信息**: 球队内部关系、士气状况

#### B. 比赛结果预测情报信息
- **胜平负预测**: 胜负平预测情报
- **让球胜平负预测**: 让球盘口的胜负预测
- **比分预测**: 具体比分预测情报
- **总进球预测**: 总进球数预测情报
- **半全场预测**: 上半场/全场结果预测情报

### 1.4 信息来源渠道

1. **官方渠道**: 竞彩官方、俱乐部官网、联赛官网
2. **主流媒体**: ESPN、天空体育、BBC体育
3. **社交平台**: Twitter官方、记者推文
4. **博彩公司**: 威廉希尔、立博、bet365
5. **专业网站**: 足球数据中心、体育数据服务商

### 1.5 情报字段标准

每条情报包含以下标准字段：

| 字段名称 | 数据类型 | 说明 | 必填 |
|---------|---------|------|------|
| 标题 | String(500) | 情报标题，简要概括内容 | ✓ |
| 关键内容 | Text | 关键信息摘要 | ✓ |
| 内容详情 | Text | 详细情报内容 | ✓ |
| 信息时间 | DateTime | 信息发布时间 | ✓ |
| 关联比赛 | ForeignKey | 关联的比赛ID | ✓ |
| 开赛时间 | DateTime | 比赛开始时间 | ✓ |
| 信息来源 | ForeignKey | 信息来源ID | ✓ |
| 权重 | Float(0-1) | 信息可信度权重 | ✓ |
| 情报类型 | Enum | 情报分类 | ✓ |
| 置信度 | Enum | 信息可信度等级 | ✓ |
| 重要性 | Enum | 信息重要性等级 | ✓ |
| 关键词 | JSON Array | 关键词标签数组 |  |
| 附件 | JSON | 相关附件信息 |  |

---

## 2. 功能架构设计

情报管理模块采用模块化设计，分为5个核心子模块：

### 2.1 信息筛选模块

#### 功能职责
- **信息推送**: 从信息采集模块接收原始情报数据
- **质量评估**: 对情报进行初步质量评分和可信度判断
- **内容编辑**: 允许管理员对情报内容进行编辑和补充
- **状态管理**: 标记情报处理状态（待审核、已审核、已发布、已废弃）

#### 核心功能
1. **信息列表展示**
   - 多维度列表视图：时间线、分类视图、优先级视图
   - 支持关键字搜索和高级筛选
   - 批量操作支持（批量审核、批量标记、批量删除）

2. **信息审核流程**
   - 人工审核：管理员手动审核情报质量
   - 自动审核：基于规则的初步筛选
   - 分级审核：重要情报需要多级审核

3. **权重初始化**
   - 基于来源可信度的基础权重设置
   - 基于情报类型的默认权重调整
   - 人工权重修正功能

#### 技术实现
- **前端**: 基于 `IntelTable.vue` 组件扩展筛选功能
- **后端**: 新增 `intelligence_screening_service.py` 服务
- **API**: 新增 `/api/v1/intelligence/screening/` 路由组

### 2.2 信息采集模块

#### 功能职责
- **多渠道采集**: 支持爬虫爬取、手工录入、API集成三种方式
- **数据标准化**: 统一不同来源的数据格式和字段映射
- **增量更新**: 智能识别新数据，避免重复采集
- **异常处理**: 采集失败重试机制和错误日志记录

#### 核心功能

1. **手工录入界面**
   - 直观的表单录入界面
   - 数据验证和实时提示
   - 模板化录入支持

32. **API集成管理**
   - 外部API对接配置管理
   - 数据同步策略配置
   - API调用监控和限流

#### 技术实现
- **现有组件**: 爬虫服务已在 `backend/scrapers/` 中实现
- **扩展功能**: 在 `backend/services/crawler_integration.py` 基础上扩展
- **新增API**: 集成管理相关的API端点

### 2.3 情报模型模块

#### 功能职责
- **特征提取**: 将原始情报转化为AI模型可用的特征向量
- **模型训练**: 管理情报特征与预测结果的关联关系
- **版本管理**: 不同版本的情报模型管理和对比
- **效果评估**: 评估情报特征对预测准确率的贡献度

#### 核心功能
1. **特征工程**
   - 文本特征提取：TF-IDF、关键词频率、情感分析
   - 时间特征处理：距离比赛时间、信息新鲜度
   - 组合特征生成：来源可信度×情报类型×时间衰减

2. **模型配置**
   - 特征选择器配置：哪些特征参与模型训练
   - 权重计算规则：特征权重的动态调整规则
   - 更新策略：模型定期更新和增量训练

3. **效果监控**
   - 特征重要性排名
   - 模型性能对比
   - 预测贡献度分析

#### 技术实现
- **机器学习**: 使用scikit-learn进行特征工程
- **模型存储**: 在数据库中存储模型配置和版本信息
- **API设计**: 提供模型训练、评估、部署的API

### 2.4 情报权重模块

#### 功能职责
- **权重初始化**: 为不同类型、不同来源的情报设置初始权重
- **权重调整**: 基于情报反馈和实际效果动态调整权重
- **权重计算**: 综合多因素计算情报最终权重
- **权重应用**: 权重应用于情报排序和特征计算

#### 核心权重因素
1. **来源权重**（基础权重）
   - 官方渠道：0.9-1.0
   - 权威媒体：0.7-0.8
   - 社交媒体：0.4-0.6
   - 用户提交：0.2-0.3

2. **时效权重**（时间衰减因子）
   - 24小时内：1.0
   - 1-3天：0.8
   - 3-7天：0.6
   - 7天以上：0.3

3. **相关性权重**
   - 直接相关（伤病、停赛）：0.9
   - 间接相关（天气、历史）：0.7
   - 背景信息（战意、氛围）：0.5

4. **置信度权重**
   - 已确认：1.0
   - 非常高：0.9
   - 高：0.8
   - 中等：0.6
   - 低：0.4

#### 权重计算公式
```
最终权重 = 基础权重 × 时效因子 × 相关因子 × 置信因子 × 人工修正
```

#### 技术实现
- **计算公式**: 在 `Intelligence.calculate_weight()` 方法中实现
- **权重存储**: 在 `intelligence` 表的 `calculated_weight` 字段
- **调整接口**: 提供权重调整和规则配置API

### 2.5 情报图谱模块

#### 功能职责
- **关系可视化**: 展示比赛与情报之间的关联关系
- **情报聚合**: 将分散的情报按比赛聚合展示
- **交互探索**: 支持用户交互式探索情报关系
- **趋势展示**: 可视化展示情报时间线和趋势变化

#### 核心功能
1. **单场比赛情报图谱**
   - 以比赛为中心的情报网络图
   - 情报分类聚合视图
   - 时间线展示情报发展过程

2. **多场比赛情报对比**
   - 多场比赛情报横向对比
   - 相似比赛情报模式识别
   - 跨比赛情报关联分析

3. **动态情报监控**
   - 实时情报更新展示
   - 重要情报突出显示
   - 情报关系动态演化

#### 技术实现
- **可视化库**: 使用ECharts或D3.js进行数据可视化
- **数据接口**: 提供图谱数据生成和更新API
- **前端组件**: 开发专用情报图谱组件

---

## 3. 数据库设计

### 3.1 核心数据表

#### 3.1.1 情报主表 (`intelligence`)
存储所有情报信息，是模块的核心表。

| 字段名 | 数据类型 | 必填 | 说明 |
|--------|---------|------|------|
| `id` | Integer | ✓ | 主键 |
| `match_id` | Integer | ✓ | 关联比赛ID |
| `team_id` | Integer |  | 关联球队ID |
| `player_id` | Integer |  | 关联球员ID |
| `type_id` | Integer | ✓ | 情报类型ID |
| `source_id` | Integer | ✓ | 信息来源ID |
| `title` | String(500) | ✓ | 情报标题 |
| `content` | Text | ✓ | 详细内容 |
| `summary` | Text |  | AI生成的摘要 |
| `keywords` | Text |  | JSON数组，关键词 |
| `tags` | Text |  | JSON数组，标签 |
| `confidence` | Enum | ✓ | 置信度（VERY_LOW~CONFIRMED） |
| `confidence_score` | Float | ✓ | 数值化置信度（0-1） |
| `importance` | Enum | ✓ | 重要性（LOW~CRITICAL） |
| `base_weight` | Float | ✓ | 基础权重（0-1） |
| `weight_multiplier` | Float | ✓ | 权重乘数（0.5-2.0） |
| `calculated_weight` | Float | ✓ | 计算后权重（0-1） |
| `status` | String(50) | ✓ | 状态（active~deleted） |
| `is_verified` | Boolean | ✓ | 是否已验证 |
| `is_duplicate` | Boolean | ✓ | 是否重复情报 |
| `view_count` | Integer | ✓ | 查看次数 |
| `like_count` | Integer | ✓ | 点赞次数 |
| `comment_count` | Integer | ✓ | 评论次数 |
| `share_count` | Integer | ✓ | 分享次数 |
| `popularity_score` | Float | ✓ | 热门度得分 |

#### 3.1.2 情报类型表 (`intelligence_types`)
管理情报类型分类。

| 字段名 | 数据类型 | 必填 | 说明 |
|--------|---------|------|------|
| `id` | Integer | ✓ | 主键 |
| `name` | String(100) | ✓ | 类型名称 |
| `code` | String(50) | ✓ | 类型代码（唯一） |
| `description` | Text |  | 类型描述 |
| `category` | String(50) | ✓ | 大类（player, team, match...） |
| `subcategory` | String(50) |  | 子类 |
| `default_weight` | Float | ✓ | 默认权重（0-1） |
| `default_confidence` | Enum | ✓ | 默认置信度 |
| `display_order` | Integer | ✓ | 显示顺序 |
| `color` | String(20) |  | 显示颜色 |

#### 3.1.3 信息来源表 (`intelligence_sources`)
管理情报来源渠道。

| 字段名 | 数据类型 | 必填 | 说明 |
|--------|---------|------|------|
| `id` | Integer | ✓ | 主键 |
| `name` | String(100) | ✓ | 来源名称 |
| `code` | String(50) | ✓ | 来源代码（唯一） |
| `description` | Text |  | 来源描述 |
| `source_type` | String(50) | ✓ | 来源类型（website, api...） |
| `url` | String(500) |  | 来源网址 |
| `reliability_score` | Float | ✓ | 可信度评分（0-1） |
| `is_verified` | Boolean | ✓ | 是否已验证 |
| `is_official` | Boolean | ✓ | 是否官方渠道 |
| `last_crawled_at` | DateTime |  | 最后采集时间 |
| `total_items` | Integer | ✓ | 总采集条数 |
| `success_rate` | Float | ✓ | 采集成功率 |

#### 3.1.4 情报关联表 (`intelligence_relations`)
管理情报之间的关联关系。

| 字段名 | 数据类型 | 必填 | 说明 |
|--------|---------|------|------|
| `id` | Integer | ✓ | 主键 |
| `intelligence_id` | Integer | ✓ | 情报ID |
| `related_intelligence_id` | Integer | ✓ | 关联情报ID |
| `relation_type` | String(50) | ✓ | 关系类型（confirms...） |
| `relation_strength` | Float | ✓ | 关联强度（0-1） |

#### 3.1.5 情报分析表 (`intelligence_analytics`)
存储情报分析统计数据。

| 字段名 | 数据类型 | 必填 | 说明 |
|--------|---------|------|------|
| `id` | Integer | ✓ | 主键 |
| `date` | Date | ✓ | 统计日期 |
| `total_items` | Integer | ✓ | 总条数 |
| `verified_items` | Integer | ✓ | 已验证条数 |
| `avg_confidence_score` | Float | ✓ | 平均置信度 |
| `avg_weight` | Float | ✓ | 平均权重 |
| `total_views` | Integer | ✓ | 总查看次数 |
| `total_likes` | Integer | ✓ | 总点赞次数 |
| `trending_items` | Integer | ✓ | 趋势情报数 |

### 3.2 关系模型

```
比赛 (matches)
   ↑ 1:n
情报 (intelligence) -- 1:n --> 情报关联 (intelligence_relations)
   ↑ n:1                   ↑ n:1
情报类型 (intelligence_types)   关联情报 (intelligence)
   ↑ n:1
情报来源 (intelligence_sources)
```

### 3.3 枚举类型

#### 情报类型枚举 (`IntelligenceTypeEnum`)
```python
INJURY = "injury"           # 伤病信息
SUSPENSION = "suspension"   # 停赛信息  
LINEUP = "lineup"           # 阵容信息
TACTICS = "tactics"         # 战术分析
WEATHER = "weather"         # 天气信息
REFEREE = "referee"         # 裁判信息
VENUE = "venue"             # 场地信息
ODDS = "odds"               # 赔率信息
TRANSFER = "transfer"       # 转会信息
RUMOR = "rumor"             # 传闻信息
PREDICTION = "prediction"   # 预测分析
STATISTICS = "statistics"   # 统计数据
PREVIEW = "preview"         # 赛前预告
REVIEW = "review"           # 赛后回顾
MOTIVATION = "motivation"   # 战意分析
HISTORY = "history"         # 历史交锋
FORM = "form"               # 近期状态
OTHER = "other"             # 其他信息
```

#### 信息来源枚举 (`IntelligenceSourceEnum`)
```python
OFFICIAL = "official"              # 官方渠道
BOOKMAKER = "bookmaker"            # 博彩公司
MEDIA = "media"                    # 媒体
SOCIAL_MEDIA = "social_media"      # 社交媒体
EXPERT = "expert"                  # 专家分析
AI_ANALYSIS = "ai_analysis"        # AI分析
USER_SUBMISSION = "user_submission" # 用户提交
SYSTEM = "system"                  # 系统生成
```

#### 置信度枚举 (`ConfidenceLevelEnum`)
```python
VERY_LOW = "very_low"      # 非常低 (0-20%)
LOW = "low"                # 低 (21-40%)
MEDIUM = "medium"          # 中等 (41-60%)
HIGH = "high"              # 高 (61-80%)
VERY_HIGH = "very_high"    # 非常高 (81-100%)
CONFIRMED = "confirmed"    # 已确认 (100%)
```

#### 重要性枚举 (`ImportanceLevelEnum`)
```python
LOW = "low"                # 低重要性
MEDIUM = "medium"          # 中重要性
HIGH = "high"              # 高重要性
CRITICAL = "critical"      # 关键重要性
```

---

## 4. API接口设计

### 4.1 情报管理API

#### 4.1.1 获取情报列表
```http
GET /api/v1/intelligence/
```
**查询参数**:
- `league`: 联赛名称（默认"all"）
- `type`: 情报类型（默认"all"）
- `source`: 信息来源（默认"all"）
- `match_id`: 比赛ID
- `sort_by`: 排序方式（created_at, weight, match_time）
- `sort_order`: 排序顺序（asc, desc）
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "match_id": 1001,
      "title": "主力球员伤病缺席",
      "content": "主队主力前锋因膝伤缺席本场比赛...",
      "type": "injury",
      "source": "official",
      "weight": 0.85,
      "confidence": "high",
      "importance": "high",
      "created_at": "2026-01-21T10:00:00Z",
      "updated_at": "2026-01-21T10:00:00Z"
    }
  ],
  "message": "获取成功",
  "timestamp": "2026-01-21T10:00:00Z"
}
```

#### 4.1.2 获取情报详情
```http
GET /api/v1/intelligence/{id}
```

#### 4.1.3 创建情报
```http
POST /api/v1/intelligence/
```
**请求体**:
```json
{
  "match_id": 1001,
  "title": "情报标题",
  "content": "详细内容",
  "type": "injury",
  "source": "official",
  "confidence": "high",
  "importance": "medium",
  "base_weight": 0.8
}
```

#### 4.1.4 更新情报
```http
PUT /api/v1/intelligence/{id}
```

#### 4.1.5 删除情报
```http
DELETE /api/v1/intelligence/{id}
```

### 4.2 情报筛选API

#### 4.2.1 获取筛选列表
```http
GET /api/v1/intelligence/screening/
```
**查询参数**:
- `status`: 状态筛选（pending, reviewed, published, archived）
- `min_weight`: 最小权重
- `max_weight`: 最大权重
- `date_from`: 开始日期
- `date_to`: 结束日期
- `sort_by`: 排序字段（weight, created_at, updated_at）
- `sort_order`: 排序顺序（asc, desc）

#### 4.2.2 批量审核
```http
POST /api/v1/intelligence/screening/batch-review
```
**请求体**:
```json
{
  "ids": [1, 2, 3],
  "action": "approve",
  "notes": "审核通过"
}
```

#### 4.2.3 权重调整
```http
PUT /api/v1/intelligence/screening/{id}/weight
```
**请求体**:
```json
{
  "weight_multiplier": 1.2,
  "reason": "信息来源可信度提高"
}
```

### 4.3 情报分析API

#### 4.3.1 获取统计摘要
```http
GET /api/v1/intelligence/analytics/summary
```
**查询参数**:
- `days`: 统计天数（默认7天）

#### 4.3.2 获取趋势分析
```http
GET /api/v1/intelligence/analytics/trend
```
**查询参数**:
- `days`: 分析天数（默认30天）

#### 4.3.3 获取质量报告
```http
GET /api/v1/intelligence/analytics/quality
```
**查询参数**:
- `days`: 分析天数（默认7天）

---

## 5. 前端组件设计

### 5.1 页面结构

```
情报管理模块
├── 情报列表页面 (IntelligenceList.vue)
│   ├── 筛选面板 (FilterPanel.vue)
│   ├── 情报表格 (IntelTable.vue)
│   └── 分页组件 (Pagination.vue)
├── 情报详情页面 (IntelligenceDetail.vue)
│   ├── 情报内容 (IntelligenceContent.vue)
│   ├── 相关情报 (RelatedIntelligence.vue)
│   └── 评论区域 (CommentsSection.vue)
├── 情报编辑页面 (IntelligenceEdit.vue)
│   ├── 表单组件 (IntelligenceForm.vue)
│   └── 预览组件 (PreviewPanel.vue)
├── 情报图谱页面 (IntelligenceGraph.vue)
│   ├── 关系图组件 (RelationGraph.vue)
│   ├── 时间线组件 (TimelineViewer.vue)
│   └── 筛选控件 (GraphFilter.vue)
└── 情报分析页面 (IntelligenceAnalytics.vue)
    ├── 统计卡片 (StatsCards.vue)
    ├── 图表组件 (AnalyticsCharts.vue)
    └── 数据表格 (AnalyticsTable.vue)
```

### 5.2 组件清单

#### 5.2.1 核心组件

| 组件名称 | 文件路径 | 说明 |
|---------|---------|------|
| `IntelTable` | `frontend/src/components/intelligence/IntelTable.vue` | 情报表格组件，支持筛选、排序、分页 |
| `IntelWeight` | `frontend/src/components/intelligence/IntelWeight.vue` | 权重展示组件，可视化显示权重值 |
| `IntelSource` | `frontend/src/components/intelligence/IntelSource.vue` | 信息来源组件，显示来源可信度 |
| `IntelTags` | `frontend/src/components/intelligence/IntelTags.vue` | 标签组件，显示情报标签 |
| `RelationGraph` | `frontend/src/components/intelligence/RelationGraph.vue` | 关系图组件，可视化情报关联 |

#### 5.2.2 页面组件

| 组件名称 | 文件路径 | 说明 |
|---------|---------|------|
| `IntelligenceList` | `frontend/src/views/intelligence/List.vue` | 情报列表页面 |
| `IntelligenceDetail` | `frontend/src/views/intelligence/Detail.vue` | 情报详情页面 |
| `IntelligenceEdit` | `frontend/src/views/intelligence/Edit.vue` | 情报编辑页面 |
| `IntelligenceGraph` | `frontend/src/views/intelligence/Graph.vue` | 情报图谱页面 |
| `IntelligenceAnalytics` | `frontend/src/views/intelligence/Analytics.vue` | 情报分析页面 |

#### 5.2.3 功能组件

| 组件名称 | 文件路径 | 说明 |
|---------|---------|------|
| `FilterPanel` | `frontend/src/components/intelligence/FilterPanel.vue` | 筛选面板组件 |
| `SearchBar` | `frontend/src/components/intelligence/SearchBar.vue` | 搜索栏组件 |
| `BatchActions` | `frontend/src/components/intelligence/BatchActions.vue` | 批量操作组件 |
| `TimelineViewer` | `frontend/src/components/intelligence/TimelineViewer.vue` | 时间线查看组件 |
| `StatsCards` | `frontend/src/components/analytics/StatsCards.vue` | 统计卡片组件 |

### 5.3 数据流设计

#### 5.3.1 组件通信
```
父组件 (IntelligenceList)
  ↓ props
子组件 (IntelTable) → emits事件 → 父组件处理
  ↓ 
子组件 (FilterPanel) → emit筛选条件 → 父组件更新数据
```

#### 5.3.2 状态管理
使用Pinia进行全局状态管理：

```javascript
// store/intelligence.js
export const useIntelligenceStore = defineStore('intelligence', {
  state: () => ({
    list: [],
    currentItem: null,
    filters: {
      type: '',
      source: '',
      minWeight: 0,
      maxWeight: 1
    },
    pagination: {
      page: 1,
      pageSize: 20,
      total: 0
    },
    loading: false
  }),
  
  actions: {
    async fetchList(params) {
      this.loading = true;
      const response = await intelligenceAPI.getIntelligenceReports(params);
      this.list = response.data;
      this.pagination.total = response.total;
      this.loading = false;
    },
    
    async fetchDetail(id) {
      this.currentItem = await intelligenceAPI.getIntelligenceReportById(id);
    }
  }
});
```

#### 5.3.3 API集成
```javascript
// api/intelligence.js
import client from './client';

export const intelligenceAPI = {
  getIntelligenceReports(params) {
    return client.get('/intelligence', { params });
  },
  
  getIntelligenceReportById(id) {
    return client.get(`/intelligence/${id}`);
  },
  
  createIntelligence(data) {
    return client.post('/intelligence', data);
  },
  
  updateIntelligence(id, data) {
    return client.put(`/intelligence/${id}`, data);
  },
  
  deleteIntelligence(id) {
    return client.delete(`/intelligence/${id}`);
  }
};
```

---

## 6. 任务调度设计

### 6.1 定时任务

#### 6.1.1 情报数据采集任务
```python
# backend/tasks/intelligence_tasks.py

@shared_task(base=DatabaseTask, bind=True)
def crawl_intelligence_periodic(self):
    """
    定期爬取情报数据
    执行频率：每30分钟
    """
    # 1. 获取最近24小时内即将开始的比赛
    # 2. 遍历比赛，调用相应爬虫采集情报
    # 3. 处理采集结果，创建或更新情报数据
    # 4. 记录采集日志和统计信息
```

#### 6.1.2 权重更新任务
```python
@shared_task(base=DatabaseTask, bind=True)
def update_intelligence_weights(self):
    """
    更新情报权重
    执行频率：每小时
    """
    # 1. 获取最近7天内的活跃情报
    # 2. 重新计算每条情报的权重
    # 3. 更新数据库中的权重值
    # 4. 记录权重变更日志
```

#### 6.1.3 情报去重任务
```python
@shared_task(base=DatabaseTask, bind=True)
def deduplicate_intelligence(self, hours_back=24):
    """
    情报去重处理
    执行频率：每6小时
    """
    # 1. 查找指定时间范围内的重复情报
    # 2. 合并重复情报，保留高质量信息
    # 3. 更新情报关联关系
    # 4. 记录去重处理日志
```

### 6.2 异步处理

#### 6.2.1 情报质量分析
```python
@shared_task(base=DatabaseTask, bind=True)
def analyze_intelligence_quality(self, intelligence_ids):
    """
    异步分析情报质量
    """
    # 1. 获取指定情报的详细数据
    # 2. 执行质量分析算法
    # 3. 更新情报质量评分
    # 4. 发送分析结果通知
```

#### 6.2.2 情报关联分析
```python
@shared_task(base=DatabaseTask, bind=True)
def analyze_intelligence_relations(self, intelligence_ids):
    """
    异步分析情报关联
    """
    # 1. 分析情报之间的关联关系
    # 2. 建立关系网络图
    # 3. 更新关联关系数据
    # 4. 生成关系图谱数据
```

#### 6.2.3 情报特征提取
```python
@shared_task(base=DatabaseTask, bind=True)
def extract_intelligence_features(self, intelligence_ids):
    """
    异步提取情报特征
    """
    # 1. 对情报内容进行文本分析
    # 2. 提取关键特征和关键词
    # 3. 计算特征权重
    # 4. 更新情报特征数据
```

---

## 7. 开发指南与实现要点

### 7.1 后端实现要点

#### 7.1.1 数据模型设计
1. **继承关系**: 使用SQLAlchemy的Base类继承体系
2. **枚举类型**: 使用SQLAlchemy Enum类型存储状态字段
3. **JSON字段**: 使用MutableDict处理JSON数据
4. **索引优化**: 为查询频繁的字段创建索引

#### 7.1.2 服务层设计
1. **服务分离**: 不同功能模块使用独立的服务类
2. **事务管理**: 使用数据库事务保证数据一致性
3. **异常处理**: 统一的异常处理机制和错误响应格式
4. **日志记录**: 详细的业务操作日志和错误日志

#### 7.1.3 API设计规范
1. **RESTful风格**: 遵循RESTful API设计原则
2. **版本管理**: API版本前缀，向后兼容
3. **认证授权**: JWT令牌认证和RBAC权限控制
4. **响应格式**: 统一响应格式和错误码体系

### 7.2 前端实现要点

#### 7.2.1 组件设计原则
1. **单一职责**: 每个组件只负责一个功能
2. **可复用性**: 设计通用的基础组件
3. **可组合性**: 支持组件自由组合
4. **响应式设计**: 支持不同屏幕尺寸

#### 7.2.2 状态管理策略
1. **本地状态**: 组件内部状态使用ref/reactive
2. **组件通信**: 父子组件使用props/emit
3. **全局状态**: 共享状态使用Pinia管理
4. **数据缓存**: 频繁访问的数据进行缓存

#### 7.2.3 用户体验优化
1. **加载状态**: 数据加载时显示loading状态
2. **错误处理**: 友好的错误提示和恢复机制
3. **表单验证**: 实时表单验证和错误提示
4. **响应反馈**: 用户操作及时反馈

### 7.3 数据迁移指南

#### 7.3.1 数据库迁移步骤
1. **创建迁移文件**: 使用Alembic生成迁移脚本
2. **定义变更内容**: 创建表、修改字段、添加索引等
3. **执行迁移**: 在目标环境执行迁移脚本
4. **验证结果**: 检查迁移后的数据结构和内容

#### 7.3.2 数据初始化脚本
```python
# scripts/init_intelligence_data.py

def init_system_intelligence_types():
    """初始化系统情报类型"""
    types = [
        {"name": "球员伤病", "code": "injury", "category": "player"},
        {"name": "球员停赛", "code": "suspension", "category": "player"},
        # ... 其他类型定义
    ]
    # 插入数据库逻辑

def init_system_intelligence_sources():
    """初始化系统信息来源"""
    sources = [
        {"name": "竞彩官方", "code": "official_jc", "source_type": "official"},
        {"name": "俱乐部官网", "code": "club_official", "source_type": "official"},
        # ... 其他来源定义
    ]
    # 插入数据库逻辑
```

#### 7.3.3 数据备份策略
1. **定期备份**: 每天自动备份数据库
2. **增量备份**: 记录变更日志，支持增量恢复
3. **多版本存储**: 保留多个历史版本备份
4. **异地备份**: 重要数据异地存储

---

## 8. 测试与部署

### 8.1 单元测试

#### 8.1.1 后端单元测试
```python
# tests/backend/unit/test_intelligence_service.py

class TestIntelligenceService:
    def test_create_intelligence(self):
        """测试创建情报功能"""
        # 准备测试数据
        # 调用服务方法
        # 验证返回结果
        # 验证数据库状态
    
    def test_update_intelligence_weight(self):
        """测试更新情报权重功能"""
        # 测试权重计算逻辑
        # 验证权重更新结果
    
    def test_get_intelligence_list(self):
        """测试获取情报列表功能"""
        # 测试筛选条件
        # 验证分页功能
        # 验证排序功能
```

#### 8.1.2 前端单元测试
```javascript
// tests/frontend/unit/intelligence/IntelTable.spec.js

describe('IntelTable Component', () => {
  it('should render table with data', () => {
    // 测试组件渲染
    // 验证表格数据显示
  })
  
  it('should handle filter change', () => {
    // 测试筛选功能
    // 验证数据过滤结果
  })
  
  it('should handle sort click', () => {
    // 测试排序功能
    // 验证排序结果
  })
})
```

### 8.2 集成测试

#### 8.2.1 API集成测试
```python
# tests/backend/integration/test_intelligence_api.py

class TestIntelligenceAPI:
    def test_get_intelligence_list(self):
        """测试情报列表API"""
        # 发送API请求
        # 验证响应状态
        # 验证响应数据格式
    
    def test_create_intelligence(self):
        """测试创建情报API"""
        # 测试请求参数验证
        # 测试权限验证
        # 测试数据持久化
```

#### 8.2.2 端到端测试
```javascript
// tests/e2e/intelligence.spec.js

describe('Intelligence Module E2E', () => {
  it('should navigate to intelligence list', () => {
    // 测试页面导航
    // 验证页面内容
  })
  
  it('should create new intelligence', () => {
    // 测试表单填写
    // 测试表单提交
    // 验证创建结果
  })
})
```

### 8.3 部署配置

#### 8.3.1 Docker配置
```dockerfile
# Dockerfile.backend
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: sport_lottery
  redis:
    image: redis:7-alpine
    
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    depends_on:
      - postgres
      - redis
```

#### 8.3.2 环境配置
```env
# .env.production
DATABASE_URL=postgresql://user:pass@postgres:5432/sport_lottery
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-here
LOG_LEVEL=INFO
```

#### 8.3.3 监控配置
```yaml
# monitoring/prometheus.yml
scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
```

---

## 📋 附录

### A. 常用工具函数
```python
# backend/utils/intelligence_utils.py

def calculate_time_decay(published_at: datetime) -> float:
    """计算时间衰减因子"""
    hours_passed = (datetime.utcnow() - published_at).total_seconds() / 3600
    if hours_passed <= 24:
        return 1.0
    elif hours_passed <= 72:
        return 0.8
    elif hours_passed <= 168:
        return 0.6
    else:
        return 0.3

def extract_keywords(content: str) -> List[str]:
    """提取关键词"""
    # 使用jieba或其他分词库
    pass

def format_intelligence_response(intelligence: Intelligence) -> Dict:
    """格式化情报响应数据"""
    pass
```

### B. 错误码定义
| 错误码 | 说明 | HTTP状态码 |
|-------|------|-----------|
| `INT001` | 情报不存在 | 404 |
| `INT002` | 情报类型不存在 | 400 |
| `INT003` | 信息来源不存在 | 400 |
| `INT004` | 比赛不存在 | 400 |
| `INT005` | 权限不足 | 403 |
| `INT006` | 参数验证失败 | 400 |
| `INT007` | 重复情报 | 409 |
| `INT008` | 权重计算错误 | 500 |

### C. 开发规范

1. **代码规范**
   - Python: 遵循PEP 8规范
   - JavaScript: 使用ESLint和Prettier
   - 注释: 重要函数和类必须有文档注释

2. **提交规范**
   - 使用Conventional Commits格式
   - 提交前运行测试
   - 提交信息清晰明了

3. **分支管理**
   - `main`: 生产环境分支
   - `develop`: 开发主分支
   - `feature/*`: 功能分支
   - `hotfix/*`: 热修复分支

---

## 🎯 总结

情报管理模块是体育彩票扫描系统的核心信息支撑模块，通过5个子模块的协同工作，实现了从数据采集到分析应用的全流程管理：

1. **信息筛选模块**: 负责情报质量评估和内容审核
2. **信息采集模块**: 支持多渠道数据采集和标准化处理
3. **情报模型模块**: 实现特征提取和模型训练管理
4. **情报权重模块**: 提供动态权重计算和调整机制
5. **情报图谱模块**: 支持情报关系可视化和交互探索

模块采用分层架构设计，前后端分离开发，具有良好的扩展性和维护性。通过规范的开发流程和质量保障措施，确保模块的稳定性和可靠性。

---

**文档维护**: 随着模块功能演进持续更新  
**最后更新**: 2026-01-21  
**编写团队**: 后端开发组、前端开发组、产品设计组