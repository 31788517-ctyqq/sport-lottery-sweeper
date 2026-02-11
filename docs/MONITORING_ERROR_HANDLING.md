# 监控和错误处理系统

## 1. 概述

本文档描述了项目中实现的监控和错误处理机制，包括API限流、性能监控、错误统计等功能。

## 2. 监控中间件

### 2.1 功能特性

- **请求ID生成**: 为每个请求分配唯一ID，便于跟踪和调试
- **性能监控**: 记录每个请求的处理时间
- **访问日志**: 记录请求的详细信息（方法、路径、客户端IP、状态码等）
- **错误统计**: 统计错误请求数量

### 2.2 实现细节

监控中间件位于 `backend/core/monitoring_middleware.py`，实现了以下功能：

```python
class MonitoringMiddleware:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
```

## 3. API限流中间件

### 3.1 功能特性

- **IP级限流**: 基于客户端IP地址进行限流
- **时间窗口**: 默认每分钟最多60个请求
- **自动封禁**: 超过限制的IP会被临时封禁
- **响应头信息**: 返回剩余请求数和限制总数

### 3.2 实现细节

API限流中间件位于 `backend/core/rate_limit_middleware.py`，支持以下配置：

```python
def __init__(self, requests_per_minute: int = 60, ban_duration: int = 300):
```

## 4. 监控指标端点

### 4.1 系统指标

- **路径**: `/api/v1/admin/metrics/system`
- **功能**: 获取CPU、内存、磁盘使用情况
- **权限**: 需要管理员身份验证

### 4.2 API指标

- **路径**: `/api/v1/admin/metrics/api`
- **功能**: 获取API请求统计、成功率、平均响应时间
- **权限**: 需要管理员身份验证

### 4.3 错误统计

- **路径**: `/api/v1/admin/metrics/errors`
- **功能**: 获取错误统计信息
- **权限**: 需要管理员身份验证

### 4.4 健康检查

- **路径**: `/api/v1/admin/metrics/health`
- **功能**: 获取系统整体健康状况
- **权限**: 需要管理员身份验证

## 5. 错误处理机制

### 5.1 异常层级

项目采用分层异常处理机制：

```
BaseAPIException
├── AuthenticationError
├── AuthorizationError
├── ValidationException
├── NotFoundException
├── ConflictException
├── RateLimitException
├── ExternalAPIError
├── CrawlerException
├── DatabaseException
└── BusinessException
```

### 5.2 异常处理器

- **统一响应格式**: 所有异常返回一致的JSON格式
- **详细错误信息**: 包含错误码、消息、时间戳
- **日志记录**: 自动记录异常信息到日志系统
- **请求关联**: 错误信息关联请求ID，便于调试

## 6. 部署和配置

### 6.1 环境变量

- `REQUESTS_PER_MINUTE`: 限制每分钟请求数（默认60）
- `BAN_DURATION`: IP封禁时长（秒，默认300）

### 6.2 Docker配置

在Docker部署中，监控和限流中间件会自动启用。

## 7. 监控最佳实践

### 7.1 性能指标阈值

- 平均响应时间应小于1秒
- 错误率应低于10%
- CPU使用率应低于90%

### 7.2 告警机制

- 当错误率超过阈值时发送告警
- 当响应时间超过阈值时发送告警
- 当系统资源使用率过高时发送告警

## 8. 故障排除

### 8.1 常见问题

1. **API响应缓慢**
   - 检查系统资源使用情况
   - 查看慢查询日志
   - 检查数据库连接池

2. **频繁限流**
   - 检查是否为恶意请求
   - 调整限流参数
   - 检查负载均衡配置

3. **错误率上升**
   - 查看错误日志
   - 检查第三方API可用性
   - 检查数据库连接

### 8.2 调试技巧

- 使用请求ID跟踪特定请求
- 查看监控指标端点获取实时数据
- 启用详细日志记录进行深入分析