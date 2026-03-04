# LLM供应商配置页面完善开发计划

## 项目背景

当前系统已有一个远程AI服务配置页面（`/admin/ai-services/remote`），用于管理OpenAI、Anthropic、Google等主流LLM供应商的配置。然而，该页面目前使用前端模拟数据，缺乏与后端API的集成，功能不完整，无法满足运维人员的实际需求。

## 当前页面分析

### 现有功能
1. 供应商列表展示（模拟数据）
2. 添加/编辑供应商表单（模拟）
3. 搜索和筛选功能
4. 分页显示
5. 连接测试（模拟）

### 功能缺失
1. **后端API集成**：无真实数据存储和CRUD操作
2. **供应商状态管理**：缺少启用/禁用开关
3. **健康检查**：无真实连接测试
4. **统计监控**：无使用统计和成本监控
5. **配置验证**：无API密钥有效性验证
6. **批量操作**：无法批量启用/禁用供应商
7. **供应商扩展**：仅支持有限的供应商类型
8. **安全存储**：API密钥未加密存储

## 开发目标

### 总体目标
完善远程AI服务配置页面，使其成为功能完整、用户体验良好的LLM供应商管理平台，支持运维人员灵活配置和管理多种AI服务供应商。

### 具体目标
1. 实现供应商配置的持久化存储
2. 提供完整的CRUD操作API
3. 实现真实的连接测试和健康检查
4. 集成使用统计和成本监控
5. 提供友好的运维人员界面
6. 支持多种主流LLM供应商

## 技术架构

### 后端架构
```
数据库表：llm_providers
API端点：/api/v1/llm/providers
服务层：LLMProviderService
模型层：LLMProvider
```

### 前端架构
```
页面组件：RemoteAIService.vue
API客户端：@/api/llm-providers.js
状态管理：Vue reactive
UI框架：Element Plus
```

## 详细开发任务

### 第一阶段：数据库模型设计（第1天）

#### 1.1 创建LLM供应商数据模型
- 表名：`llm_providers`
- 字段设计：
  - `id`: 主键，自增
  - `name`: 服务名称（唯一）
  - `provider_type`: 供应商类型（openai、anthropic、google、azure、aliyun等）
  - `api_key`: API密钥（加密存储）
  - `base_url`: 基础URL（可选）
  - `model`: 默认模型名称
  - `enabled`: 是否启用
  - `priority`: 优先级（用于负载均衡）
  - `max_requests_per_minute`: 每分钟最大请求数
  - `health_status`: 健康状态（healthy、unhealthy、checking）
  - `last_checked_at`: 最后检查时间
  - `created_at`: 创建时间
  - `updated_at`: 更新时间

#### 1.2 创建数据库迁移文件
- 使用Alembic生成迁移脚本
- 确保兼容现有数据库结构

### 第二阶段：后端API开发（第2-3天）

#### 2.1 创建CRUD API端点
- `GET /api/v1/llm/providers`: 获取供应商列表（支持分页、筛选）
- `GET /api/v1/llm/providers/{id}`: 获取单个供应商详情
- `POST /api/v1/llm/providers`: 创建新供应商
- `PUT /api/v1/llm/providers/{id}`: 更新供应商
- `DELETE /api/v1/llm/providers/{id}`: 删除供应商
- `POST /api/v1/llm/providers/{id}/test`: 测试供应商连接

#### 2.2 实现供应商服务层
- `LLMProviderService`: 处理业务逻辑
- 供应商注册和初始化
- 连接测试和健康检查
- API密钥加密解密

#### 2.3 集成现有LLM服务
- 更新 `LLMService` 支持从数据库加载供应商
- 支持动态添加/移除供应商

### 第三阶段：前端功能完善（第4-5天）

#### 3.1 API客户端集成
- 创建 `@/api/llm-providers.js`
- 实现所有CRUD操作的API调用
- 错误处理和加载状态管理

#### 3.2 更新RemoteAIService.vue
- 替换模拟数据为真实API调用
- 实现供应商列表的动态加载
- 添加启用/禁用开关
- 实现批量操作功能

#### 3.3 增强用户界面
- 添加供应商健康状态指示器
- 实现实时连接测试
- 添加使用统计展示
- 优化表单验证

### 第四阶段：测试和文档（第6天）

#### 4.1 功能测试
- API端点测试
- 前端组件测试
- 集成测试

#### 4.2 性能测试
- 并发连接测试
- 响应时间测试

#### 4.3 文档编写
- 运维人员使用说明
- API接口文档
- 部署配置指南

## 数据库设计详述

### llm_providers 表结构
```sql
CREATE TABLE llm_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL UNIQUE,
    provider_type VARCHAR(50) NOT NULL,
    api_key TEXT NOT NULL,  -- 加密存储
    base_url VARCHAR(500),
    model VARCHAR(100),
    enabled BOOLEAN DEFAULT 1,
    priority INTEGER DEFAULT 10,
    max_requests_per_minute INTEGER DEFAULT 60,
    health_status VARCHAR(20) DEFAULT 'checking',
    last_checked_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES admin_users(id),
    updated_by INTEGER REFERENCES admin_users(id)
);
```

### 索引设计
- `idx_llm_providers_name`: 名称索引
- `idx_llm_providers_type`: 类型索引
- `idx_llm_providers_enabled`: 启用状态索引
- `idx_llm_providers_health`: 健康状态索引

## API设计

### 请求/响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "providers": [],
    "total": 0,
    "page": 1,
    "page_size": 20
  }
}
```

### 供应商对象结构
```json
{
  "id": 1,
  "name": "OpenAI-GPT4",
  "provider_type": "openai",
  "model": "gpt-4",
  "enabled": true,
  "priority": 5,
  "health_status": "healthy",
  "last_checked_at": "2024-01-01T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## 前端功能详述

### 1. 供应商列表页面
- 表格展示所有供应商
- 实时健康状态指示
- 启用/禁用开关
- 操作按钮（编辑、测试、删除）

### 2. 添加/编辑表单
- 供应商类型选择（下拉菜单）
- API密钥输入（密码框）
- 基础URL输入（可选）
- 模型名称输入
- 优先级设置
- 启用状态开关

### 3. 连接测试功能
- 实时测试供应商连接
- 显示测试结果（成功/失败）
- 错误信息展示
- 健康状态更新

### 4. 统计监控面板
- 本月总成本
- 总请求数
- 各供应商使用占比
- 健康状态概览

## 安全考虑

### 1. API密钥加密
- 使用AES加密存储API密钥
- 密钥仅在内存中解密
- 避免日志中泄露密钥

### 2. 访问控制
- 仅管理员和经理角色可访问
- API密钥不可通过列表接口返回

### 3. 速率限制
- 基于供应商配置的请求限制
- 防止滥用和超额费用

## 部署和运维

### 1. 数据库迁移
- 自动执行Alembic迁移
- 回滚机制

### 2. 监控告警
- 供应商健康状态监控
- 成本超限告警
- 请求失败率告警

### 3. 备份策略
- 定期备份供应商配置
- API密钥单独备份

## 时间计划

### 第1周：基础功能
- 第1天：数据库设计和迁移
- 第2天：后端CRUD API
- 第3天：前端API集成
- 第4天：基本功能测试
- 第5天：文档编写

### 第2周：高级功能
- 第6天：健康检查和统计
- 第7天：批量操作和UI优化
- 第8天：安全增强
- 第9天：性能测试
- 第10天：最终验收

## 成功标准

1. 运维人员可通过界面完整管理LLM供应商
2. 供应商配置持久化存储，重启不丢失
3. 实时健康检查，及时发现问题
4. 成本和使用统计清晰可查
5. 支持主流LLM供应商扩展
6. API密钥安全存储和传输

## 风险评估和缓解

### 风险1：API密钥泄露
- **缓解**：加密存储，最小权限访问，定期轮换

### 风险2：供应商服务不稳定
- **缓解**：健康检查，自动禁用异常供应商，故障转移

### 风险3：成本超支
- **缓解**：使用监控，告警机制，请求限制

### 风险4：兼容性问题
- **缓解**：标准化接口，供应商适配层，向后兼容

## 附录

### 支持的供应商类型
1. OpenAI: GPT-3.5, GPT-4, GPT-4 Turbo
2. Anthropic: Claude-3系列
3. Google: Gemini Pro, Gemini Ultra
4. Azure OpenAI: GPT-35-Turbo, GPT-4
5. Alibaba Cloud: Qwen系列
6. 本地部署: Ollama, vLLM等

### 相关技术栈
- 后端：FastAPI, SQLAlchemy, Alembic
- 前端：Vue 3, Element Plus, Axios
- 数据库：SQLite（开发），PostgreSQL（生产）
- 加密：cryptography库