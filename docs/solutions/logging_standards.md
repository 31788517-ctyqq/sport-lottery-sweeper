# 日志系统使用规范

## 📋 规范概述

本规范旨在统一项目中的日志记录方式，确保日志系统的一致性、可维护性和可监控性。所有Python代码必须遵循此规范。

## ✅ 核心原则

1. **统一使用Python logging模块**：禁止使用`print()`语句记录日志信息
2. **集中化日志管理**：所有日志输出到`logs/app.log`文件
3. **分级日志记录**：合理使用不同日志级别
4. **结构化日志格式**：包含时间戳、模块名、日志级别、函数名、行号等信息

## 📊 日志级别使用指南

| 级别 | 使用场景 | 示例 |
|------|----------|------|
| **DEBUG** | 调试信息，开发环境详细跟踪 | `logger.debug(f"Processing item {item_id}")` |
| **INFO** | 常规操作信息，生产环境可见 | `logger.info("User login successful")` |
| **WARNING** | 警告信息，不影响系统运行 | `logger.warning("Cache miss for key {key}")` |
| **ERROR** | 错误信息，需要关注但可恢复 | `logger.error(f"API call failed: {exc}")` |
| **CRITICAL** | 严重错误，可能导致系统崩溃 | `logger.critical("Database connection lost")` |

## 🛠️ 代码实现规范

### 1. 基础导入和配置

```python
import logging

# 获取当前模块的logger
logger = logging.getLogger(__name__)

# 在应用启动时初始化日志系统
from backend.utils.logging_config import setup_logging
setup_logging()
```

### 2. 正确使用示例

```python
# ✅ 正确示例
logger.info("正在注册API路由...")
logger.debug(f"处理参数: {params}")
logger.error(f"数据库连接失败: {exc}", exc_info=True)
logger.warning("缓存已过期，重新加载")

# ❌ 错误示例
print("正在注册API路由...")  # 禁止使用
print(f"[ERROR] 数据库连接失败: {exc}")  # 禁止使用
```

### 3. 异常日志记录

```python
try:
    result = process_data(data)
except Exception as e:
    # 记录完整异常堆栈
    logger.error(f"数据处理失败: {e}", exc_info=True)
    # 或者
    logger.exception("数据处理失败")  # 自动包含堆栈信息
```

## 📁 日志文件管理

### 1. 日志目录结构

```
logs/
├── app.log          # 当前活动日志文件
├── app.log.1        # 轮转备份文件1
├── app.log.2        # 轮转备份文件2
└── ...              # 最多保留30个备份文件
```

### 2. 轮转策略

- **大小轮转**：单个文件超过10MB时自动轮转
- **时间轮转**：每天午夜自动轮转
- **备份保留**：最多保留30个备份文件

### 3. 禁止的日志实践

- ❌ 在项目根目录创建分散的`.log`文件
- ❌ 使用`print()`语句输出日志信息
- ❌ 将敏感信息记录到日志中（密码、密钥等）
- ❌ 日志级别滥用（如生产环境使用DEBUG级别）

## 🔧 配置说明

### 1. 默认日志配置

```python
# backend/utils/logging_config.py 中的默认配置
DEFAULT_LOG_CONFIG = {
    "max_bytes": 10 * 1024 * 1024,  # 10MB
    "backup_count": 30,             # 30个备份
    "rotation_interval": "midnight", # 每天轮转
    "encoding": "utf-8",
    "log_level": logging.INFO       # 默认级别
}
```

### 2. 环境变量配置

```bash
# 在.env文件中配置
LOG_LEVEL=DEBUG      # 可选: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_MAX_BYTES=10485760  # 文件大小限制（字节）
LOG_BACKUP_COUNT=30     # 备份文件数量
```

## 🚀 最佳实践

### 1. 性能优化

- 使用参数化日志消息避免不必要的字符串拼接
- 在循环中谨慎使用DEBUG级别日志
- 使用适当的日志级别避免生产环境日志过多

```python
# ✅ 性能友好
logger.debug("Processing item %s with data %s", item_id, data_summary)

# ❌ 性能较差（即使DEBUG级别禁用也会执行字符串拼接）
logger.debug(f"Processing item {item_id} with data {data_summary}")
```

### 2. 上下文信息

- 在关键操作中添加用户ID、请求ID等上下文信息
- 使用日志字段进行结构化日志记录

```python
logger.info("用户操作完成", extra={
    "user_id": user.id,
    "request_id": request.state.request_id,
    "operation": "data_export"
})
```

### 3. 安全考虑

- **绝不记录敏感信息**：密码、API密钥、令牌等
- **脱敏处理**：对个人身份信息（PII）进行脱敏
- **访问控制**：确保日志文件权限适当

## 📈 监控和告警

### 1. 错误监控

- 监控ERROR和CRITICAL级别日志
- 设置错误率告警阈值
- 定期检查日志文件大小和轮转情况

### 2. 性能监控

- 记录API响应时间
- 监控数据库查询性能
- 跟踪关键业务流程耗时

### 3. 审计日志

- 用户登录/登出操作
- 敏感数据访问
- 系统配置变更

## 🔄 迁移指南

### 1. 从print迁移到logging

```python
# 迁移前
print(f"[INFO] 正在处理请求: {request_id}")

# 迁移后
logger.info(f"正在处理请求: {request_id}")
```

### 2. 批量替换工具

```bash
# 使用sed或脚本批量替换（Linux/Mac）
find backend -name "*.py" -not -path "*/venv/*" -exec sed -i 's/print(/logger.debug(/g' {} \;

# 注意：需要根据实际情况调整日志级别
```

## 📚 相关文档

- [Python官方logging文档](https://docs.python.org/3/library/logging.html)
- [项目日志配置](../backend/utils/logging_config.py)
- [日志中间件](../backend/core/logging_middleware.py)
- [问题解决库索引](../README.md)

---

**最后更新**: 2026-01-29  
**维护者**: 系统架构团队  
**状态**: 正式生效