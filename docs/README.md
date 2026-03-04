# 竞彩足球扫盘系统 - 后端服务

## 项目简介

竞彩足球扫盘系统是一个专业的足球数据采集、分析和预测平台，专门为竞彩足球提供全面的数据支持和智能分析。

## 功能特性

- 🚀 **高性能API服务**: 基于FastAPI构建的异步API
- 🕷️ **智能爬虫系统**: 多源数据采集，支持反爬策略
- 📊 **数据仓库**: 结构化存储比赛、球队、联赛、情报等数据
- 🔐 **完善的安全体系**: RBAC权限控制、JWT认证、数据加密
- 📈 **实时数据处理**: Celery分布式任务队列
- 📡 **WebSocket实时通信**: 实时比赛更新和通知
- 📱 **多格式输出**: 支持JSON、CSV、Excel、PDF导出
- 🎯 **智能预测**: 基于历史数据和机器学习的预测模型
- 📝 **完整的文档**: 自动生成的API文档和开发文档

## 技术栈

### 后端框架
- **FastAPI** - 高性能异步Web框架
- **SQLAlchemy** - Python SQL工具包和ORM
- **Alembic** - 数据库迁移工具
- **Pydantic** - 数据验证和设置管理

### 数据库
- **PostgreSQL** - 主关系型数据库
- **Redis** - 缓存和消息队列
- **Elasticsearch** - 日志和搜索服务

### 异步任务
- **Celery** - 分布式任务队列
- **RabbitMQ/Redis** - 消息代理
- **Flower** - Celery监控界面

### 爬虫系统
- **Scrapy** - 专业爬虫框架
- **Playwright** - 动态页面爬取
- **BeautifulSoup4** - HTML解析

### 数据处理
- **Pandas** - 数据分析库
- **NumPy** - 数值计算
- **WeasyPrint** - PDF生成

### 部署运维
- **Docker & Docker Compose** - 容器化部署
- **Nginx** - 反向代理和负载均衡
- **Prometheus & Grafana** - 监控和告警
- **ELK Stack** - 日志管理

## 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose（推荐）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/football-scan/backend.git
cd backend