# /api/v1/admin/headers 字段兼容与数据源/任务绑定改造计划

**文档版本**: v1.0  
**创建日期**: 2026-02-08  
**范围**: 请求头管理页（/admin/data-source/headers）与后端 `/api/v1/admin/headers` 接口  

## 目标
1. 在 **/api/v1/admin/headers** 上完成字段兼容，避免前端改路径。
2. 以 **“数据源/任务绑定”** 为主的生效机制，保证运维可控、可验证。
3. 打通请求头与爬虫执行闭环，真实记录使用次数、成功率、最后使用时间。
4. 补齐运维体验必需的批量操作、测试、统计与导入导出。

## 现状问题摘要
- 前端字段与后端 schema/枚举不一致（priority/type/usage 等）。
- `/api/v1/admin/headers` 返回字段与前端期望不一致。
- “测试/统计”接口为占位逻辑，无法反映真实效果。
- 请求头未真正被爬虫请求链路使用。

## 总体方案
### 方案 A（选择）
保持前端路径不变，**在 `/api/v1/admin/headers` 做字段兼容**，提供双向字段映射与枚举转换。

### 生效机制
**以“数据源/任务绑定”为主**：  
1. 在数据源或任务配置中显式绑定请求头集合。
2. 爬虫执行时优先使用绑定集合；无绑定时使用全局启用集合（可配置）。

## 数据模型与字段兼容设计
### 现有模型
`backend/models/headers.py`  
`request_headers` 表字段：
- `domain`, `name`, `value`, `type`, `priority`, `status`
- `usage_count`, `success_count`, `last_used`, `success_rate`（计算）

### 前端期望字段（现有 UI）
- `lastUsed`, `usageCount`, `successRate`
- `type`: `common/specific/mobile/desktop`
- `priority`: `low/medium/high`

### 兼容策略（API 适配层）
在 `/api/v1/admin/headers` 中增加 **字段映射与枚举转换**，对入参/出参均进行兼容。

**出参映射：**
| 存储字段 | 前端字段 |
| --- | --- |
| `usage_count` | `usageCount` |
| `success_count` | `successCount` |
| `last_used` | `lastUsed` |
| `success_rate` | `successRate` |

**入参兼容：**
- 支持 `priority` 字符串(`low/medium/high`)与数字(1/2/3)
- 支持 `type` 字符串(`common/specific/mobile/desktop`)并映射到存储值
- 如果传入 `lastUsed/usageCount` 等字段，忽略或用于校验（不直接写）

**枚举映射建议：**
| 前端 `type` | 存储 `type` |
| --- | --- |
| `common` | `general` |
| `specific` | `specific` |
| `mobile` | `mobile` |
| `desktop` | `desktop` |

| 前端 `priority` | 存储 `priority` |
| --- | --- |
| `low` | `1` |
| `medium` | `2` |
| `high` | `3` |

## 数据源/任务绑定设计
### 绑定关系
建议新增绑定表（建议命名）：
- `data_source_headers`
  - `id`, `data_source_id`, `header_id`, `priority_override`, `enabled`
- `crawler_task_headers`
  - `id`, `task_id`, `header_id`, `priority_override`, `enabled`

**优先级规则：**
1. **任务绑定** > **数据源绑定** > **全局启用**
2. 同名 header 冲突时按 `priority` 较高者生效

### 执行期选择逻辑
- 执行任务时，根据 `task_id` 查任务绑定
- 无绑定则使用数据源绑定
- 若无绑定且允许 fallback，则使用全局启用 headers
- 记录 `usage_count`, `success_count`, `last_used`

## 接口定义（/api/v1/admin/headers）
### 查询列表
`GET /api/v1/admin/headers`
参数：
- `page`, `size`, `domain`, `status`, `type`, `search`
返回字段（增加兼容字段）：
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "domain": "example.com",
        "name": "User-Agent",
        "value": "...",
        "type": "common",
        "priority": "high",
        "status": "enabled",
        "lastUsed": "2026-02-08T10:00:00Z",
        "usageCount": 12,
        "successRate": 91.67,
        "remarks": ""
      }
    ],
    "total": 1
  }
}
```

### 创建
`POST /api/v1/admin/headers`
入参示例：
```json
{
  "domain": "example.com",
  "name": "User-Agent",
  "value": "Mozilla/5.0 ...",
  "type": "common",
  "priority": "high",
  "status": "enabled",
  "remarks": "PC UA"
}
```

### 更新
`PUT /api/v1/admin/headers/{id}`
支持 `priority` 字符串或数字，`type` 前端枚举。

### 批量导入
`POST /api/v1/admin/headers/import`
支持：
- JSON 数组（与创建结构一致）
- CSV/文本导入由前端解析后仍调用此接口

### 测试
`POST /api/v1/admin/headers/{id}/test`
**实现真实测试**：
- 根据 `domain` 发起 `HEAD/GET`
- 返回结果写回 `success_count/usage_count/last_used`

### 绑定接口（新增）
1. `POST /api/v1/admin/headers/bind/data-source`
```json
{ "dataSourceId": 12, "headerIds": [1,2,3], "enabled": true }
```

2. `POST /api/v1/admin/headers/bind/task`
```json
{ "taskId": 33, "headerIds": [1,5], "enabled": true }
```

3. `GET /api/v1/admin/headers/bindings`
支持查询当前绑定关系。

## 前端页面改动点（HeadersManagement.vue）
1. **表格字段映射**
  - 支持 `lastUsed/usageCount/successRate` 显示
2. **新增绑定入口**
  - 在列表增加 “绑定数据源/任务” 操作按钮
  - 弹窗支持选择数据源、任务
3. **补齐筛选条件**
  - `type`、`priority`、`search`
4. **补齐批量操作**
  - 批量启用/禁用/测试/删除
5. **导入模板提示**
  - 显示示例格式
6. **统计卡片**
  - 总数、启用数、禁用数、成功率

## 后端改造清单（代码级）
1. `backend/api/v1/admin/headers_management.py`
  - 增加字段映射层
  - 兼容 `priority/type` 枚举
  - 真实测试逻辑（写回 usage/success/last_used）
2. 新增绑定表模型与 CRUD
  - `backend/models/data_source_headers.py`
  - `backend/models/task_headers.py`
  - 对应 schema 与 API router
3. 任务执行链路接入
  - `backend/services/task_scheduler_service.py`
  - 从绑定表读取 headers，并合并到请求中
4. 统计接口真实化
  - 返回成功率、最近一次使用时间
5. 迁移脚本
  - `alembic` 或 `docs/db_migrations` 增加绑定表

## 前端改造清单（代码级）
1. `frontend/src/views/admin/crawler/HeadersManagement.vue`
  - 增加批量选中/操作
  - 增加绑定弹窗
  - 增加统计卡片
2. `frontend/src/api/headers.js`
  - 新增绑定接口调用
  - 补齐批量测试/批量启用
3. 可选：`frontend/src/views/admin/crawler/DataSourceManagement.vue`
  - 数据源编辑页增加 “请求头绑定” 标签页

## 实施步骤
### 第 1 阶段（字段兼容 + 闭环基础）
1. `/api/v1/admin/headers` 增加字段映射
2. 真实测试逻辑，写回统计字段
3. 任务执行链路读取绑定 headers

### 第 2 阶段（运维体验增强）
1. 统计卡片
2. 批量操作
3. 绑定管理 UI

### 第 3 阶段（稳定性与审计）
1. 操作日志
2. 敏感字段脱敏
3. 告警与告知

## 验收清单
- 前端页面显示无编码/字段错乱
- 前端新增/编辑可成功保存
- 真实测试可写入成功率
- 任务运行时请求头来自绑定表
- 绑定关系可视化可配置

