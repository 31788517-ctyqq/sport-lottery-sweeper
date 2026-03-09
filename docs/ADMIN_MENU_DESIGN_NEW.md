# 新后台管理系统菜单设计

## 设计理念

基于AI原生管理、模块化设计和用户体验优化的理念，重新设计后台管理系统菜单结构。新菜单将整合现有功能与新增的AI能力，提供更加直观和高效的管理体验。

## 菜单结构设计

### 1. 仪表台 (Dashboard)
- **路径**: `/admin/dashboard`
- **图标**: `<House />`
- **功能**:
  - 系统概览统计
  - AI服务监控
  - 数据采集监控
  - 智能体状态
  - 预警系统

### 2. 用户管理 (User Management)
- **路径**: `/admin/users`
- **图标**: `<UserFilled />`
- **子菜单**:
  - 用户列表 (`/admin/users/list`) - 现有功能
  - 角色与权限 (`/admin/users/roles`) - 现有功能
  - 部门管理 (`/admin/users/departments`) - 现有功能
  - 个人中心 (`/admin/users/profile`) - 现有功能
  - 用户画像管理 (`/admin/users/profiles`) - 新增AI功能
  - 行为日志 (`/admin/users/logs`) - 现有功能

### 3. 数据源管理 (Data Source Management)
- **路径**: `/admin/data-source`
- **图标**: `<SetUp />`
- **子菜单**:
  - 数据源配置 (`/admin/data-source/config`) - 新增功能
  - 爬虫监控 (`/admin/data-source/monitor`) - 新增功能
  - IP池管理 (`/admin/data-source/ip-pool`) - 新增功能
  - 请求头管理 (`/admin/data-source/headers`) - 新增功能

### 4. 比赛数据管理 (Match Data Management)
- **路径**: `/admin/match-data`
- **图标**: `<Soccer />`
- **子菜单**:
  - 比赛管理 (`/admin/match-data/matches`) - 整合现有功能
  - 赔率管理 (`/admin/match-data/odds`) - 新增功能
  - 数据验证 (`/admin/match-data/validation`) - 新增功能
  - 异常检测 (`/admin/match-data/anomaly-detection`) - 新增功能

### 5. AI服务管理 (AI Services Management) - **全新模块**
- **路径**: `/admin/ai-services`
- **图标**: `<ChatLineRound />`
- **子菜单**:
  - LLM提供商管理 (`/admin/ai-services/providers`) - 新增功能
  - 成本监控 (`/admin/ai-services/costs`) - 新增功能
  - 智能体管理 (`/admin/ai-services/agents`) - 新增功能
  - 预测模型管理 (`/admin/ai-services/models`) - 新增功能
  - 对话助手 (`/admin/ai-services/conversation`) - 新增功能

### 6. 智能决策 (Intelligent Decision)
- **路径**: `/admin/intelligent-decision`
- **图标**: `<Management />`
- **子菜单**:
  - 对冲策略管理 (`/admin/intelligent-decision/hedging`) - 新增功能
  - 推荐系统管理 (`/admin/intelligent-decision/recommendations`) - 新增功能
  - 风险控制 (`/admin/intelligent-decision/risk-control`) - 新增功能

### 7. 情报分析 (Intelligence Analysis)
- **路径**: `/admin/intelligence`
- **图标**: `<Document />`
- **子菜单**:
  - 智能筛选 (`/admin/intelligence/screening`) - 现有功能
  - 采集管理 (`/admin/intelligence/collection`) - 现有功能
  - 模型管理 (`/admin/intelligence/model`) - 现有功能
  - 情报来源管理 (`/admin/intelligence/sources`) - 新增功能
  - 情感分析 (`/admin/intelligence/sentiment`) - 新增功能
  - 多模态分析 (`/admin/intelligence/multimodal`) - 新增功能

### 8. 报告生成 (Report Generation)
- **路径**: `/admin/reports`
- **图标**: `<Memo />`
- **子菜单**:
  - 自动报告 (`/admin/reports/auto`) - 新增功能
  - 自定义报告 (`/admin/reports/custom`) - 新增功能
  - 模板管理 (`/admin/reports/templates`) - 新增功能
  - 报告分发 (`/admin/reports/distribution`) - 新增功能

### 9. 系统管理 (System Management)
- **路径**: `/admin/system`
- **图标**: `<Setting />`
- **子菜单**:
  - 系统配置 (`/admin/system/config`) - 现有功能
  - 性能监控 (`/admin/system/monitoring`) - 现有功能
  - 数据备份 (`/admin/system/backup`) - 现有功能
  - API管理 (`/admin/system/api`) - 现有功能

### 10. 日志管理 (Log Management)
- **路径**: `/admin/logs`
- **图标**: `<Tickets />`
- **子菜单**:
  - 日志总览 (`/admin/logs`) - 现有功能
  - 系统日志 (`/admin/logs/system`) - 现有功能
  - 用户日志 (`/admin/logs/user`) - 现有功能
  - 安全日志 (`/admin/logs/security`) - 现有功能
  - AI服务日志 (`/admin/logs/ai`) - 新增功能

## 菜单设计原则

### 1. 层次清晰
- 主菜单项不超过10个，避免过多选择干扰
- 子菜单项控制在合理范围内，便于查找
- 功能相近的模块归类到同一个主菜单下

### 2. 易于导航
- 菜单项命名简洁明了，符合用户认知
- 常用功能放在易于访问的位置
- 提供面包屑导航，方便用户定位当前位置

### 3. 适应性
- 保持现有功能的路径不变，确保向后兼容
- 新增功能按照模块化原则组织
- 支持权限控制，不同角色用户看到不同的菜单项

### 4. AI集成突出
- 新增专门的AI服务管理模块
- 在相关功能模块中集成AI能力展示
- 提供AI服务监控和成本管理功能

## 实现建议

### 1. 渐进式改造
- 保留现有菜单结构，逐步添加新功能模块
- 确保现有功能不受影响
- 按优先级逐步开发新功能

### 2. 用户过渡
- 提供菜单使用指南
- 保留旧路径的重定向（如有必要）
- 逐步引导用户适应新菜单结构

### 3. 权限控制
- 按照新的菜单结构设计权限
- AI相关功能设置专门的权限控制
- 确保敏感功能的安全访问

## 预期效果

新菜单设计将使后台管理系统更符合AI原生理念，提供更清晰的导航体验，同时保留现有功能的完整性。AI服务管理模块的引入将使AI能力更加突出和易于管理，提升系统的智能化水平。