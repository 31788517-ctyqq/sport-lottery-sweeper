# 足球SP管理模块 - 后端开发文档

## 1. 概述

### 1.1 模块定位
SP（Special Odds）管理模块是体育彩票扫盘系统的核心功能模块，负责足球比赛赔率数据的采集、存储、管理和分析。

### 1.2 功能架构
基于 `SP_guihua.md` 规划，后端需实现以下三大功能区块：
- **数据源管理模块**：API、本地文件数据源的统一管理（移除爬虫功能）
- **比赛信息管理模块**：比赛基础信息的CRUD和状态管理  
- **SP值管理模块**：SP值的录入、展示、历史记录和纠错
- **数据分析与洞察模块**：SP值统计分析、报表生成和规律发现

## 2. 数据库设计

### 2.1 核心数据表结构

#### 2.1.1 数据源配置表 (data_sources)
```sql
CREATE TABLE data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '数据源名称',
    type VARCHAR(20) NOT NULL COMMENT '类型: api/file',
    status BOOLEAN DEFAULT TRUE COMMENT '启用状态',
    url VARCHAR(500) COMMENT '接口地址或文件路径',
    config TEXT COMMENT '配置信息(JSON格式)',
    last_update DATETIME COMMENT '最后更新时间',
    error_rate DECIMAL(5,2) DEFAULT 0 COMMENT '错误率',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```



#### 2.1.3 比赛信息表 (matches)
```sql
CREATE TABLE matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id VARCHAR(50) UNIQUE NOT NULL COMMENT '比赛唯一标识',
    home_team VARCHAR(100) NOT NULL COMMENT '主队名称',
    away_team VARCHAR(100) NOT NULL COMMENT '客队名称',
    match_time DATETIME NOT NULL COMMENT '比赛时间',
    league VARCHAR(100) COMMENT '联赛/杯赛',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '比赛状态: pending/ongoing/finished',
    home_score INTEGER COMMENT '主队得分',
    away_score INTEGER COMMENT '客队得分',
    final_result VARCHAR(20) COMMENT '最终赛果',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2.1.4 赔率公司表 (odds_companies)
```sql
CREATE TABLE odds_companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '公司名称',
    short_name VARCHAR(20) COMMENT '简称',
    logo_url VARCHAR(200) COMMENT 'Logo地址',
    status BOOLEAN DEFAULT TRUE COMMENT '启用状态',
    weight DECIMAL(3,2) DEFAULT 1.0 COMMENT '权重/优先级',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2.1.5 SP值记录表 (sp_records)
```sql
CREATE TABLE sp_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    handicap_type VARCHAR(20) NOT NULL COMMENT '盘口类型: handicap/no_handicap',
    handicap_value DECIMAL(4,1) COMMENT '让球数值',
    sp_value DECIMAL(8,2) NOT NULL COMMENT 'SP值',
    recorded_at DATETIME NOT NULL COMMENT '记录时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (company_id) REFERENCES odds_companies(id),
    INDEX idx_match_time (match_id, recorded_at),
    INDEX idx_company_time (company_id, recorded_at)
);
```

#### 2.1.6 SP值修改日志表 (sp_modification_logs)
```sql
CREATE TABLE sp_modification_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sp_record_id INTEGER NOT NULL,
    original_value DECIMAL(8,2) NOT NULL,
    modified_value DECIMAL(8,2) NOT NULL,
    modified_by INTEGER NOT NULL COMMENT '修改人ID',
    reason TEXT COMMENT '修改原因',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sp_record_id) REFERENCES sp_records(id)
);
```



## 3. API接口设计

### 3.1 数据源管理接口

#### 3.1.1 数据源CRUD
```python
# GET /api/v1/sp/data-sources
# 获取数据源列表（支持分页、筛选）
# Query: type, status, search, page, size

# POST /api/v1/sp/data-sources  
# 创建数据源
# Body: {name, type, url, config}  # type: api/file

# PUT /api/v1/sp/data-sources/{id}
# 更新数据源

# DELETE /api/v1/sp/data-sources/{id}
# 删除数据源
```

#### 3.1.2 API数据源管理
```python
# GET /api/v1/sp/data-sources/api
# 获取API类型数据源列表

# POST /api/v1/sp/data-sources/api/test
# 测试API数据源连接
```

#### 3.1.3 文件数据源管理
```python
# GET /api/v1/sp/data-sources/file
# 获取文件类型数据源列表

# POST /api/v1/sp/data-sources/file/upload-template
# 上传文件导入模板
```

### 3.2 比赛信息管理接口

#### 3.2.1 比赛CRUD
```python
# GET /api/v1/sp/matches
# 获取比赛列表
# Query: status, league, team, date_range, page, size

# POST /api/v1/sp/matches
# 创建比赛

# PUT /api/v1/sp/matches/{id}
# 更新比赛信息

# GET /api/v1/sp/matches/{id}
# 获取比赛详情

# POST /api/v1/sp/matches/batch-update
# 批量更新比赛信息
```

### 3.3 SP值管理接口

#### 3.3.1 SP值操作
```python
# GET /api/v1/sp/records
# 获取SP值记录
# Query: match_id, company_id, handicap_type, date_range

# POST /api/v1/sp/records
# 手动录入SP值

# PUT /api/v1/sp/records/{id}
# 修改SP值（需记录日志）

# GET /api/v1/sp/records/{match_id}/history
# 获取比赛SP值历史

# GET /api/v1/sp/records/{match_id}/chart
# 获取SP值走势图数据
```

#### 3.3.2 赔率公司管理
```python
# GET /api/v1/sp/companies
# 获取赔率公司列表

# POST /api/v1/sp/companies
# 创建赔率公司

# PUT /api/v1/sp/companies/{id}
# 更新公司信息
```

### 3.4 数据分析接口

#### 3.4.1 统计分析
```python
# GET /api/v1/sp/analysis/distribution
# SP值分布统计
# Query: league, company_id, handicap_type, date_range

# GET /api/v1/sp/analysis/volatility  
# SP值变动分析（临场变盘）

# GET /api/v1/sp/analysis/company-comparison
# 赔率公司对比分析

# GET /api/v1/sp/analysis/correlation
# SP值与赛果关联分析

# POST /api/v1/sp/analysis/custom-query
# 自定义查询分析
```

#### 3.4.2 报表导出
```python
# GET /api/v1/sp/reports/sp-distribution
# 导出SP值分布报表

# GET /api/v1/sp/reports/match-analysis
# 导出比赛分析报表
```

## 4. 核心业务逻辑

### 4.1 数据采集服务
```python
class DataCollectionService:
    """数据采集服务（已移除爬虫功能）"""
    
    async def fetch_api_data(self, source_id: int):
        """从API拉取数据"""
        
    async def import_file_data(self, file_path: str, mapping: dict):
        """导入本地文件数据"""
        
    async def validate_data_quality(self, data_batch: list):
        """验证导入数据的质量和完整性"""
```

### 4.2 SP值管理服务
```python
class SPValueService:
    """SP值管理服务"""
    
    async def record_sp_value(self, match_id: int, company_id: int, 
                           handicap_type: str, handicap_value: float, 
                           sp_value: float):
        """记录SP值"""
        
    async def modify_sp_value(self, record_id: int, new_value: float, 
                            operator_id: int, reason: str):
        """修改SP值并记录日志"""
        
    async def get_sp_trend(self, match_id: int, company_id: int):
        """获取SP值走势"""
```

### 4.3 数据分析服务
```python
class DataAnalysisService:
    """数据分析服务"""
    
    async def analyze_distribution(self, filters: dict):
        """SP值分布分析"""
        
    async def analyze_volatility(self, time_before_match: int):
        """临场SP值变动分析"""
        
    async def calculate_correlation(self, sp_range: tuple, result_type: str):
        """SP值与赛果关联分析"""
```

## 5. 技术实现要点

### 5.1 异步任务处理
- 使用 Celery 或 FastAPI BackgroundTasks 处理数据导入等耗时操作
- 实现任务队列和重试机制
- 添加任务状态监控和告警
- 移除爬虫相关任务调度

### 5.2 缓存策略
- Redis 缓存热点数据：最新SP值、公司列表、联赛信息
- 缓存SP值统计数据，避免重复计算
- 实现缓存失效和更新机制

### 5.3 数据校验
- Pydantic 模型验证输入数据
- 赔率数据合理性校验（SP值范围、格式）
- 比赛时间逻辑校验

### 5.4 性能优化
- 数据库索引优化（按比赛ID、时间、公司ID建立复合索引）
- 分页查询避免大数据集返回
- 数据分表和归档策略

## 6. 安全考虑

### 6.1 权限控制
- 数据源管理：仅管理员可操作
- SP值修改：需记录操作人和原因
- 数据分析：根据用户角色限制数据范围

### 6.2 数据安全
- API接口身份验证和授权
- 敏感配置信息加密存储
- 操作日志记录和审计

## 7. 部署和运维

### 7.1 服务拆分
- 数据导入服务（独立进程，处理API拉取和文件导入）
- API服务（FastAPI应用）
- 分析计算服务（定时任务）

### 7.2 监控告警
- 数据导入任务成功率监控
- 数据库连接和性能监控  
- SP数据质量监控（异常值检测）
- API数据源可用性监控

### 7.3 数据备份
- 定期数据库备份
- SP历史数据归档策略
- 灾难恢复预案

---

**文档版本**: v1.0  
**创建时间**: 2026-01-21  
**基于文档**: SP_guihua.md