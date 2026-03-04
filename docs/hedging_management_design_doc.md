# 对冲策略页面设计开发文档

## 1. 页面概述

对冲策略页面（`/admin/hedging`）是一个用于管理和分析体育彩票对冲机会的管理界面。该页面帮助管理员识别并管理通过竞彩和欧指之间的赔率差异获得稳定收益的机会。

## 2. 功能说明

### 2.1 主要功能
- 展示当天或指定日期的二串一对冲机会
- 显示对冲组合的详细信息（比赛、赔率、投资回报等）
- 提供利润分析和风险评估
- 支持日期筛选和数据刷

### 2.2 对冲原理
- 竞彩二串一固定投注C=1000元
- 欧指投入金额采用新公式计算
- 两场比赛的间隔必须大于1小时
- 核心验证条件：需满足 R > 0.02(E + C) 的盈利目标
- 确保竞彩中奖和不中奖两种情况下均有正收益

## 3. 界面布局

### 3.1 页面结构
```
┌─────────────────────────────────────┐
│ Card容器                            │
│ ┌─────────────────────────────────┐ │
│ │ Card头部                        │ │
│ │ [标题] [刷新按钮]               │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [日期选择] [查询按钮]               │
│                                     │
│ 表格区域                            │
│ ┌─────────────────────────────────┐ │
│ │ 表格内容                        │ │
│ └─────────────────────────────────┘ │
│                                     │
│ 分页区域                            │
└─────────────────────────────────────┘
```

### 3.2 组件构成
- `el-card`: 主容器，包含卡片头部和内容区
- `el-date-picker`: 日期选择器，用于选择分析日期
- `el-table`: 数据表格，展示对冲机会详情
- `el-pagination`: 分页组件
- `el-button`: 操作按钮

## 4. 数据字段说明

### 4.1 表格列说明
| 字段 | 说明 |
|------|------|
| 比赛1 | 第一场赛事的主队VS客队，包含比赛时间 |
| 比赛2 | 第二场赛事的主队VS客队，包含比赛时间 |
| 竞彩赔率 | 两场比赛在竞彩平台的组合赔率 |
| 欧指赔率 | 两场比赛在欧洲指数的组合赔率 |
| 欧指投入 | 欧洲指数投注金额，根据公式 E=C×(Sc-0.2)/Se 计算 |
| 收入 | 固定收益（通常是800元） |
| 利润 | 计算得出的利润额 |
| 利润率 | 投资收益率（利润/总投入） |

### 4.2 API接口
- [getParlayOpportunities(date)](file://c:\Users\11581\Downloads\sport-lottery-sweeper\frontend\src\api\hedging.js#L7-L71): 获取指定日期的对冲机会数据
- [getHedgingConfig()](file://c:\Users\11581\Downloads\sport-lottery-sweeper\frontend\src\api\hedging.js#L74-L86): 获取对冲配置参数
- [calculateManualHedging(data)](file://c:\Users\11581\Downloads\sport-lottery-sweeper\frontend\src\api\hedging.js#L89-L113): 手动计算对冲数据

## 5. 核心公式与盈利条件

下表汇总了为实现 R > 0.02(E + C) 目标所需的核心公式与更严格的筛选条件。

| 公式/条件名称 | 公式 | 参数说明 | 优化后的目标阈值 |
|---|---|---|---|
| 欧指投入金额公式 | E = C × (S<sub>c</sub> - 0.2) / S<sub>e</sub> | • C: 竞彩卖出本金<br>• S<sub>c</sub> = SP1 × SP2: 竞彩总赔率<br>• S<sub>e</sub> = O1 × O2: 欧指总赔率 | - |
| 收益公式 | R = C × [0.8 - (S<sub>c</sub> - 0.2) / S<sub>e</sub>] | R: 对冲后的稳定利润 | > 0.02(E + C) |
| 新盈利筛选条件 | (S<sub>c</sub> - 0.2) / S<sub>e</sub> < 0.7647 | 这是实现 R > 0.02(E + C) 的关键条件 | 必须 < 0.7647 |

**推导逻辑**：
新利润目标为 R > 0.02(E + C)。代入 E 和 R 的表达式：
C × [0.8 - K] > 0.02 × [C × K + C]，其中 K = (S<sub>c</sub> - 0.2) / S<sub>e</sub>
简化不等式：
0.8 - K > 0.02(K + 1)
求解得：
K < 1.02/1.32 ≈ 0.7647

## 6. 公式应用与验证示例

### 6.1 验证标准
筛选出的比赛必须满足以下条件：
1. 两场比赛间隔大于1小时
2. (S<sub>c</sub> - 0.2) / S<sub>e</sub> < 0.7647
3. 利润率 > 2%（即 R/(E + C) > 0.02）

### 6.2 应用示例

以提供的组合为例：
S<sub>c</sub> = 2.0468, S<sub>e</sub> = 2.52

1. 计算比值：(2.0468 - 0.2) / 2.52 = 1.8468 / 2.52 ≈ 0.732
2. 检查条件：0.732 < 0.7647，条件满足
3. 计算欧指投入：E = 1000 × 0.732 = 732元
4. 计算总投入：E + C = 732 + 1000 = 1732元
5. 计算利润：R = 1000 × (0.8 - 0.732) = 68元
6. 计算利润率：68 / 1732 ≈ 3.93% > 2%，达标

### 6.3 多组验证数据

| 组合 | 竞彩总赔率 | 欧指总赔率 | 比值 K | 是否满足 | 利润率 | 是否达标 |
|------|------------|------------|--------|----------|--------|----------|
| 组合1 (沙特联+荷乙) | 2.0468 | 2.52 | 0.732 | 是 | 3.93% | 是 |
| 组合2 (荷乙+意甲) | 4.5236 | 5.86 | 0.738 | 是 | 3.85% | 是 |

## 7. 交互逻辑

### 7.1 初始化逻辑
1. 页面加载时自动设置当前日期
2. 自动加载当天的对冲机会数据

### 7.2 查询逻辑
1. 用户选择日期
2. 点击"查询"按钮触发数据加载
3. 显示加载状态指示器
4. 请求API获取对冲机会数据
5. 后端自动应用新筛选条件 (K < 0.7647) 和比赛间隔过滤
6. 更新表格和总计数量

### 7.3 刷新逻辑
1. 点击"刷新数据"按钮
2. 重新加载当前筛选条件下的数据

## 8. 样式规范

### 8.1 CSS类说明
- `.profit-positive`: 正利润文本绿色显示
- `.profit-negative`: 负利润文本红色显示
- `.profit-high`: 高利润率文本绿色粗体显示（利润率≥3%）
- `.profit-medium`: 中等利润率文本绿色显示（2%≤利润率<3%）
- `.profit-low`: 低利润率文本橙色显示（利润率<2%）

### 8.2 布局样式
- 卡片容器边距：20px
- 分页组件右对齐
- 表格条纹样式

## 9. 错误处理

- 日期未选择时点击查询会提示警告
- API请求失败时显示错误消息
- 加载状态会在请求完成后正确关闭

## 10. 开发要点

### 10.1 技术栈
- Vue 3 Composition API
- Element Plus UI组件库
- Axios用于HTTP请求

### 10.2 响应式数据
- [loading](file://c:\Users\11581\Downloads\sport-lottery-sweeper\backend\app\api\v1\auth.py#L55-L55): 控制加载状态
- [parlayOpportunities](file://c:\Users\11581\Downloads\sport-lottery-sweeper\frontend\src\views\admin\hedging\HedgingManagement.vue#L6-L6): 存储对冲机会列表
- [selectedDate](file://c:\Users\11581\Downloads\sport-lottery-sweeper\frontend\src\views\admin\hedging\HedgingManagement.vue#L7-L7): 选定的日期
- [currentPage](file://c:\Users\11581\Downloads\sport-lottery-sweeper\frontend\src\views\admin\hedging\HedgingManagement.vue#L8-L8), [pageSize](file://c:\Users\11581\Downloads\sport-lottery-sweeper\frontend\src\views\admin\hedging\HedgingManagement.vue#L9-L9), [totalItems](file://c:\Users\11581\Downloads\sport-lottery-sweeper\frontend\src\views\admin\hedging\HedgingManagement.vue#L10-L10): 分页相关数据

### 10.3 工具函数
- [formatCurrency()](file://c:\Users\11581\Downloads\sport-lottery-sweeper\frontend\src\i18n\locale.js#L314-L343): 格式化货币显示
- [formatDate()](file://c:\Users\11581\Downloads\sport-lottery-sweeper\frontend\src\i18n\locale.js#L352-L391): 格式化时间显示
- [calculateProfitRate()](file://c:\Users\11581\Downloads\sport-lottery-sweeper\frontend\src\utils\hedging.js#L1-L50): 计算利润率并应用新筛选条件

## 11. 注意事项

1. 目前使用模拟数据，生产环境将替换为真实API
2. 需要关注后端API的实现进度
3. 对冲算法逻辑需要与后端保持一致
4. 分页功能目前未完全实现，API返回全部数据
5. 二串一当天两场比赛的间隔必须大于1小时
6. 后端筛选条件已更新为 (Sc - 0.2)/Se < 0.7647，确保利润率 > 2%
7. 前端需确保显示的利润率计算公式为 R/(E + C)

## 12. 扩展建议

1. 添加更详细的对冲分析功能
2. 增加历史数据对比
3. 实现对冲机会预警功能（当利润率>3%时标记为高收益）
4. 添加导出功能
5. 增加自定义参数配置界面（可调整利润率阈值）