# 高可用性配置和负载均衡

## 1. 概述

本文档描述了项目中实现的高可用性配置和负载均衡策略，包括缓存管理、性能优化和故障转移机制。

## 2. 高可用性架构

### 2.1 缓存系统高可用性

项目实现了混合缓存系统，支持以下高可用特性：

- **Redis集群支持**：作为主缓存层，提供分布式缓存能力
- **内存缓存回退**：当Redis不可用时，自动回退到内存缓存
- **自动故障检测**：实时监控缓存服务状态
- **无缝切换**：在缓存服务故障时自动切换到备用方案

### 2.2 性能优化策略

- **请求缓存**：对GET请求的结果进行缓存，减少数据库压力
- **响应压缩**：减少网络传输数据量
- **智能缓存策略**：根据API路径设置不同的TTL（生存时间）
- **缓存键隔离**：为不同用户提供独立的缓存空间

## 3. 负载均衡配置

### 3.1 应用层负载均衡

在应用层面，我们实现了以下负载均衡策略：

- **API限流**：限制单个IP的请求频率，防止滥用
- **请求分发**：通过中间件均匀分发请求
- **健康检查**：提供健康检查端点，便于负载均衡器检测服务状态

### 3.2 数据库连接池

- **连接复用**：使用连接池复用数据库连接
- **最大连接数限制**：防止数据库过载
- **连接超时设置**：及时释放无效连接

## 4. 容错和故障转移

### 4.1 服务健康检查

提供了多个健康检查端点：

- `/health/live` - 检查服务是否启动
- `/health/ready` - 检查服务是否准备好接收流量
- `/api/v1/health` - 检查API服务健康状态

### 4.2 故障恢复机制

- **自动重连**：对数据库和缓存服务实现自动重连
- **优雅降级**：在部分服务不可用时，提供降级功能
- **错误日志记录**：详细记录错误信息，便于排查问题

## 5. 监控和指标

### 5.1 系统指标

- **CPU使用率**：监控CPU负载
- **内存使用率**：监控内存占用
- **磁盘使用率**：监控存储空间

### 5.2 API指标

- **请求总数**：统计总请求数
- **错误数量**：统计错误请求数
- **成功率**：计算请求成功率
- **平均响应时间**：监控性能表现

### 5.3 缓存指标

- **缓存命中率**：监控缓存效率
- **缓存大小**：监控缓存使用情况
- **内存缓存统计**：监控内存缓存状态
- **Redis缓存统计**：监控Redis缓存状态

## 6. 部署配置

### 6.1 Docker配置

在`docker-compose.production.yml`中配置了以下高可用性特性：

```yaml
services:
  backend:
    image: sport-lottery-sweeper:latest
    restart: always
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:password@postgres:5432/sport_lottery
    depends_on:
      - redis
      - postgres
    deploy:
      replicas: 3  # 启用3个副本以提高可用性
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

### 6.2 负载均衡器配置

使用Nginx作为反向代理和负载均衡器：

```nginx
upstream backend {
    server backend1:8000 weight=1;
    server backend2:8000 weight=1;
    server backend3:8000 weight=1;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 健康检查
    location /health {
        access_log off;
        proxy_pass http://backend/health/ready;
    }
}
```

## 7. 性能调优

### 7.1 应用性能调优

- **Gunicorn配置**：使用多个worker进程处理请求
- **异步处理**：使用async/await实现非阻塞IO
- **数据库查询优化**：使用索引和批量操作

### 7.2 缓存策略优化

- **热点数据预加载**：提前加载常用数据到缓存
- **缓存穿透防护**：对空结果也进行短暂缓存
- **缓存雪崩防护**：设置合理的过期时间随机值

## 8. 安全措施

- **限流保护**：防止DDoS攻击
- **认证授权**：保护敏感API端点
- **输入验证**：防止注入攻击
- **日志审计**：记录安全相关事件

## 9. 监控告警

- **性能告警**：响应时间超过阈值时告警
- **错误率告警**：错误率超过阈值时告警
- **资源使用告警**：资源使用率过高时告警
- **服务可用性告警**：服务不可用时告警

## 10. 部署验证

部署完成后，执行以下验证步骤：

1. 验证健康检查端点是否正常响应
2. 验证API端点是否正常工作
3. 验证缓存功能是否正常工作
4. 验证限流功能是否生效
5. 验证监控指标是否正确收集
6. 验证日志是否正确输出

通过以上配置，系统具备了高可用性、可扩展性和可靠性，能够在生产环境中稳定运行。