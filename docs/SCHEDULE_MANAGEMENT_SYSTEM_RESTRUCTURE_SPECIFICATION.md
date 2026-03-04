# 赛程管理系统改造技术文档

## 1. 概述

本文档详细描述了对后台管理系统中比赛管理菜单的改造方案。本次改造旨在完善赛程管理功能，支持多种足球联赛（西甲、英超、澳超、德甲等）的管理，并实现竞彩赛程、北单赛程和赛程配置三个子菜单的独立管理功能。

### 改造目标
- 实现赛程的增删改查功能
- 支持多种数据源导入（爬虫、外部接口、文件导入）
- 按照业务需求划分三个子菜单进行管理
- 重用现有数据模型，避免重复开发

## 2. 功能说明

### 2.1 赛程数据模型

基于现有[League](file://c:\Users\11581\Downloads\sport-lottery-sweeper\backend\models\match.py#L47-L108)模型进行扩展，保留以下核心字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| name | String | 赛程名称（如：英超、西甲等） |
| current_season | String | 当前赛季（如：2023-2024） |
| season_start | Date | 赛季开始时间 |
| season_end | Date | 赛季结束时间 |
| round_number | Integer | 当前轮次 |
| total_teams | Integer | 参赛队伍数量 |
| config | JSON | 配置信息（包含数据源、排名规则等） |

### 2.2 三个子菜单功能

#### 2.2.1 竞彩赛程管理
- 展示中国体彩竞彩近5天的比赛场次（展示天数可以筛选，默认配置5天）
- 支持增删改查操作
- 支持从爬虫、外部接口、文件三种方式导入数据
- 显示比赛基本信息：联赛、轮次、日期、主客队、状态等

#### 2.2.2 北单赛程管理
- 展示北单足球近5天的比赛场次（展示天数可以筛选，默认配置5天）
- 功能与竞彩赛程类似，但数据源不同
- 界面布局与竞彩赛程保持一致，便于用户操作

#### 2.2.3 赛程配置管理
- 联赛基础配置：当前赛季、当前轮次
- 数据导入配置：支持配置多个数据源（名称、URL、启用状态）
- 排名计算规则配置：自定义积分规则
- 支持配置保存与重置

## 3. 后端改造

### 3.1 API接口设计

#### 3.1.1 赛程配置相关API
| 接口 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/admin/matches/league/config` | GET | league_id | 获取联赛配置信息 |
| `/admin/matches/league/config` | PUT | league_id, config | 更新联赛配置信息 |

#### 3.1.2 数据导入相关API
| 接口 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/admin/matches/import/file` | POST | league_id, file | 从文件导入比赛数据 |
| `/admin/matches/jingcai/matches` | GET | days | 获取竞彩足球近N天比赛 |
| `/admin/matches/beidan/matches` | GET | days | 获取北单足球近N天比赛 |

### 3.2 代码改造细节

#### 3.2.1 后端API改造（`backend/admin/api/v1/match_admin.py`）

1. **新增赛程配置管理API**
   - 实现了`get_league_config`和`update_league_config`两个接口
   - 验证配置结构，确保数据完整性
   - 更新数据库时记录时间戳

2. **新增文件导入API**
   - 支持CSV、Excel格式文件导入
   - 验证文件格式和必要字段
   - 使用Pandas处理表格数据
   - 返回导入结果统计信息

3. **新增竞彩/北单赛程API**
   - 分别实现`get_jingcai_matches`和`get_beidan_matches`
   - 调用爬虫服务获取相应数据
   - 统一返回格式，便于前端处理

#### 3.2.2 依赖库添加
```python
# 需要添加的依赖
pip install pandas openpyxl xlrd
```

## 4. 前端改造

### 4.1 组件结构调整

将原有的`MatchManagement.vue`重构为三个独立组件：

| 组件 | 功能 |
|------|------|
| `JingcaiMatchManagement.vue` | 竞彩赛程管理 |
| `BeidanMatchManagement.vue` | 北单赛程管理 |
| `LeagueConfigManagement.vue` | 赛程配置管理 |

### 4.2 代码改造细节

#### 4.2.1 主管理页面改造（`MatchManagement.vue`）

1. **使用Tabs组件重构界面**
   - 将三个子菜单组织在Tabs中
   - 按需加载对应组件
   - 保持界面简洁一致

2. **组件化改造**
   - 将原有单页面拆分为三个独立组件
   - 每个组件负责单一功能
   - 便于维护和扩展

#### 4.2.2 竞彩赛程管理组件（`JingcaiMatchManagement.vue`）

1. **表格展示优化**
   - 显示关键信息：联赛、轮次、日期、主客队、状态
   - 状态使用标签颜色区分
   - 日期格式化显示

2. **数据导入功能**
   - 支持三种导入方式选择
   - 文件上传组件
   - 导入进度反馈

#### 4.2.3 赛程配置组件（`LeagueConfigManagement.vue`）

1. **配置表单设计**
   - 联赛选择下拉框
   - 当前赛季和轮次输入
   - 数据源配置（名称、URL、启用状态）
   - 排名规则文本编辑

2. **动态数据源管理**
   - 支持添加/删除数据源
   - 实时保存配置
   - 配置重置功能

## 5. 数据导入方案

### 5.1 文件导入流程

1. **前端流程**
   - 用户选择联赛
   - 选择导入方式（文件导入）
   - 上传Excel/CSV文件
   - 确认导入

2. **后端处理**
   ```python
   # 读取文件内容
   contents = await file.read()
   if file.filename.endswith('.csv'):
       df = pd.read_csv(BytesIO(contents))
   else:
       df = pd.read_excel(BytesIO(contents))
       
   # 验证必要字段
   required_columns = ['home_team', 'away_team', 'match_date', 'match_time']
   if not all(col in df.columns for col in required_columns):
       return error_response("缺少必要字段")
       
   # 处理数据导入
   for _, row in df.iterrows():
       # 创建/更新比赛记录
   ```

### 5.2 爬虫导入方案

1. **爬虫服务扩展**
   - 实现`crawl_jingcai_matches`方法
   - 实现`crawl_beidan_matches`方法
   - 处理数据清洗和格式化

2. **调用示例**
   ```python
   # 获取竞彩近5天比赛
   matches = await crawler_service.crawl_jingcai_matches(5)
   ```

## 6. 注意事项

### 6.1 部署注意事项
1. **依赖安装**
   - 需要安装Pandas及相关Excel处理库
   - 确保生产环境有足够权限读取上传文件

2. **文件上传配置**
   - 调整Nginx配置以支持大文件上传
   - 设置合理的超时时间

### 6.2 测试建议
1. **功能测试**
   - 验证三种数据导入方式
   - 测试配置保存与加载
   - 验证边界条件（如轮次超出范围）

2. **性能测试**
   - 大文件导入性能测试
   - 多用户并发操作测试

### 6.3 扩展性考虑
1. **数据源扩展**
   - 当前设计支持动态添加数据源
   - 可轻松扩展新的数据导入方式

2. **联赛类型扩展**
   - 现有模型已支持多种联赛类型
   - 无需修改核心代码即可支持新联赛

## 7. 附录

### 7.1 文件变更清单

| 文件路径 | 变更类型 | 说明 |
|----------|----------|------|
| `backend/admin/api/v1/match_admin.py` | 修改 | 新增赛程配置、数据导入、竞彩/北单API |
| `frontend/src/admin/MatchManagement.vue` | 修改 | 重构为Tabs结构，引入子组件 |
| `frontend/src/admin/JingcaiMatchManagement.vue` | 新增 | 竞彩赛程管理组件 |
| `frontend/src/admin/BeidanMatchManagement.vue` | 新增 | 北单赛程管理组件 |
| `frontend/src/admin/LeagueConfigManagement.vue` | 新增 | 赛程配置管理组件 |

### 7.2 数据库变更

本次改造**不涉及**数据库表结构变更，仅使用[League](file://c:\Users\11581\Downloads\sport-lottery-sweeper\backend\models\match.py#L47-L108)模型的[config](file://c:\Users\11581\Downloads\sport-lottery-sweeper\backend\models\match.py#L96-L96)字段存储配置信息，符合现有数据库设计。