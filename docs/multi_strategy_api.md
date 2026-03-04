# 多策略筛选与钉钉通知 API 文档

## 概述

多策略筛选与钉钉通知功能允许用户配置多个筛选策略并自动执行，执行结果可以通过钉钉机器人发送通知。该功能实现了自动化的彩票数据分析和通知机制。

## API 端点

### 获取多策略功能信息

```
GET /api/v1/multi-strategy/
```

获取多策略功能的基本信息和特性。

#### 响应示例

```json
{
  "success": true,
  "message": "多策略筛选与钉钉通知功能已启用",
  "features": [
    "自动执行策略筛选",
    "钉钉消息通知",
    "多种策略筛选",
    "表格形式结果展示"
  ]
}
```

### 获取可用策略列表

```
GET /api/v1/multi-strategy/strategies
```

获取系统中所有可用的筛选策略。

#### 响应示例

```json
{
  "success": true,
  "data": [
    "high_probability_winning",
    "balanced_odds",
    "recent_form"
  ]
}
```

### 执行多策略筛选

```
POST /api/v1/multi-strategy/execute
```

执行指定的多个策略筛选，并将结果通过钉钉机器人发送。

#### 请求体参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| strategy_ids | array[string] | 是 | 要执行的策略ID数组 |
| message_format | string | 否 | 结果消息格式，默认为 "table" |

#### 请求示例

```json
{
  "strategy_ids": ["high_probability_winning", "balanced_odds"],
  "message_format": "table"
}
```

#### 响应示例

```json
{
  "success": true,
  "message": "多策略筛选执行成功",
  "results": {
    "high_probability_winning": [],
    "balanced_odds": []
  },
  "formatted_message": "📊【策略筛选场次表】\n\n**high_probability_winning**..."
}
```

### 启动/停止定时任务

```
POST /api/v1/multi-strategy/toggle-task
```

启动或停止多策略的定时执行任务。

#### 请求体参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| enabled | boolean | 是 | 是否启用定时任务 |

#### 请求示例

```json
{
  "enabled": true
}
```

## 支持的策略类型

1. **high_probability_winning (高概率胜平负)**: 筛选胜平负概率较高的比赛
2. **balanced_odds (均衡赔率)**: 筛选赔率相对均衡的比赛
3. **recent_form (近期表现)**: 根据球队近期表现进行筛选

## 钉钉机器人配置

要启用钉钉通知功能，需要在后端配置钉钉机器人的 webhook URL。具体配置方法请参见主配置文档。

## 使用示例

### 1. 获取所有可用策略

```bash
curl -X GET "http://localhost:8000/api/v1/multi-strategy/strategies"
```

### 2. 执行多策略筛选

```bash
curl -X POST "http://localhost:8000/api/v1/multi-strategy/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_ids": ["high_probability_winning", "balanced_odds"],
    "message_format": "table"
  }'
```

### 3. 启动定时任务

```bash
curl -X POST "http://localhost:8000/api/v1/multi-strategy/toggle-task" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true
  }'
```

## 返回码说明

| 状态码 | 含义 | 描述 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 400 | Bad Request | 请求参数错误 |
| 500 | Internal Server Error | 服务器内部错误 |

## 错误处理

所有错误响应都包含以下格式：

```json
{
  "success": false,
  "message": "错误信息描述"
}
```