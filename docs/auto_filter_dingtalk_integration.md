# 自动策略筛选与钉钉通知功能技术开发文档

## 1. 功能概述

本文档描述了体育彩票筛选系统中新增的两个核心功能：
1. **自动执行策略筛选** - 通过定时任务机制，按照预设策略自动执行筛选
2. **钉钉消息通知** - 将筛选结果通过钉钉机器人发送给用户
3. **多种策略筛选** - 支持配置和执行多个不同的筛选策略
4. **表格形式结果展示** - 结果以表格形式发送到钉钉

## 2. 架构设计

### 2.1 系统架构图

```
前端 (Vue.js) → 后端API → 定时任务调度器 → 策略管理器 → 多策略筛选服务 → 钉钉机器人
                          ↓
                       任务管理器
                          ↓
                       策略配置存储
```

### 2.2 技术栈

- **前端**: Vue.js 3.x, Element UI
- **后端**: Python Flask/FastAPI
- **定时任务**: APScheduler (Advanced Python Scheduler)
- **钉钉集成**: requests库调用钉钉机器人Webhook API

## 3. 功能模块设计

### 3.1 策略管理模块

#### 3.1.1 StrategyManager 类设计

```python
class StrategyManager:
    def __init__(self):
        self.strategies = {}
    
    def register_strategy(self, strategy_id, strategy_func):
        """注册筛选策略"""
        self.strategies[strategy_id] = strategy_func
    
    def execute_strategy(self, strategy_id, data):
        """执行特定策略"""
        if strategy_id not in self.strategies:
            raise ValueError(f"策略 {strategy_id} 未找到")
        return self.strategies[strategy_id](data)
    
    def get_all_strategies(self):
        """获取所有策略列表"""
        return list(self.strategies.keys())
```

#### 3.1.2 策略定义示例

```python
def high_probability_winning_strategy(data):
    """高胜率策略"""
    filtered = []
    for match in data:
        if match['home_win_probability'] > 0.6 or match['away_win_probability'] > 0.6:
            filtered.append(match)
    return filtered

def balanced_odds_strategy(data):
    """平衡赔率策略"""
    filtered = []
    for match in data:
        if 1.5 <= match['home_odds'] <= 3.0 and 1.5 <= match['away_odds'] <= 3.0:
            filtered.append(match)
    return filtered

def recent_form_strategy(data):
    """近期状态策略"""
    filtered = []
    for match in data:
        if match['home_recent_form'] >= 3 or match['away_recent_form'] >= 3:
            filtered.append(match)
    return filtered
```

### 3.2 定时任务调度器

#### 3.2.1 MultiStrategyScheduler 类设计

```python
class MultiStrategyScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.strategy_manager = StrategyManager()
        self.scheduler.start()

    def add_scheduled_task(self, task_config):
        """
        添加定时筛选任务
        :param task_config: 任务配置，包含strategy_ids列表
        """
        def task_wrapper():
            try:
                results_map = {}
                for strategy_id in task_config['strategy_ids']:
                    results = self.strategy_manager.execute_strategy(strategy_id, {})
                    if results:
                        results_map[strategy_id] = results
                
                if results_map:
                    message = self._format_multi_strategy_results(task_config['user_id'], results_map)
                    send_dingtalk_message(task_config['dingtalk_webhook'], message)
            except Exception as e:
                logger.error(f"执行多策略任务时出错: {str(e)}", exc_info=True)
        
        trigger = CronTrigger.from_crontab(task_config['cron_expression'])
        self.scheduler.add_job(
            task_wrapper, 
            trigger,
            id=f"multi_filter_task_{task_config['user_id']}",
            replace_existing=True
        )

    def _format_multi_strategy_results(self, user_id, results_map):
        """格式化多策略筛选结果消息"""
        header = f"【多策略筛选结果】\n\n"
        content = ""
        
        for strategy_id, results in results_map.items():
            content += f"📊 {strategy_id} 策略:\n"
            content += f"共筛选出 {len(results)} 场比赛:\n"
            
            for i, match in enumerate(results[:3], 1):  # 每个策略只显示前3场
                content += (
                    f"  {i}. {match['home_team']} vs {match['away_team']} "
                    f"({match['match_time']})\n"
                )
            
            if len(results) > 3:
                content += f"  ... 还有{len(results)-3}场比赛\n\n"
            else:
                content += "\n"
        
        content += "完整结果请登录系统查看: http://localhost:3000/admin/beidan-filter"
        return header + content
```

### 3.3 钉钉表格消息格式化

#### 3.3.1 表格格式化函数

```python
def format_results_as_table(results_map):
    """
    将筛选结果格式化为钉钉表格消息
    :param results_map: 策略ID到结果的映射
    :return: 格式化的表格消息文本
    """
    message = "📊【多策略筛选结果表格】\n\n"
    
    for strategy_id, results in results_map.items():
        strategy_name = get_strategy_name(strategy_id)  # 获取策略名称
        message += f"*{strategy_name}* ({strategy_id}):\n\n"
        
        # 表格头部 - 基于BeidanFilterPanel筛选结果列表的字段
        message += "| 比赛ID | 主队 | 客队 | 联赛 | 比赛时间 | ΔP | ΔWP | P级 | 主队实力 | 客队实力 | 主队赢盘 | 客队赢盘 | 主队特征 | 客队特征 |\n"
        message += "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        
        # 表格内容
        for match in results[:10]:  # 限制显示前10场比赛
            message += (
                f"| {match['match_id']} | {match['home_team']} | {match['away_team']} | {match['league']} | "
                f"{match['match_time']} | {match['power_diff']} | {match['delta_wp']} | P{match['p_level']} | "
                f"{match['power_home']} | {match['power_away']} | {match['win_pan_home']} | {match['win_pan_away']} | "
                f"{match['home_feature']} | {match['away_feature']} |\n"
            )
        
        message += "\n"
    
    message += "\n🔗 完整结果请登录系统查看: http://localhost:3000/admin/beidan-filter"
    return message
```

#### 3.3.2 钉钉Markdown表格支持

钉钉机器人支持Markdown格式，包括表格格式：

```python
def send_markdown_table_to_dingtalk(webhook_url, table_content):
    """
    发送Markdown表格到钉钉
    :param webhook_url: 钉钉机器人Webhook URL
    :param table_content: Markdown格式的表格内容
    :return: 是否发送成功
    """
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "多策略筛选结果",
            "text": table_content
        }
    }
    
    try:
        response = requests.post(webhook_url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if result.get('errcode') == 0:
            return True
        else:
            logger.error(f"钉钉消息发送失败: {result.get('errmsg')}")
            return False
    except Exception as e:
        logger.error(f"发送钉钉消息时出错: {str(e)}", exc_info=True)
        return False
```

### 3.4 前端多策略管理界面

#### 3.4.1 策略选择面板

```vue
<template>
  <!-- 现有内容 -->
  
  <!-- 新增多策略配置面板 -->
  <el-card class="multi-strategy-card" v-if="showMultiStrategyPanel">
    <div slot="header" class="clearfix">
      <span>多策略筛选配置</span>
    </div>
    
    <el-form :model="multiStrategyForm" label-width="120px">
      <el-form-item label="选择策略">
        <el-checkbox-group v-model="multiStrategyForm.selectedStrategies">
          <el-checkbox 
            v-for="strategy in availableStrategies" 
            :key="strategy.id" 
            :label="strategy.id"
          >
            {{ strategy.name }}
          </el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      
      <el-form-item label="执行频率">
        <el-select v-model="multiStrategyForm.cronType" @change="updateCronExpression">
          <el-option label="每天" value="daily"></el-option>
          <el-option label="每周" value="weekly"></el-option>
          <el-option label="每小时" value="hourly"></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="消息格式">
        <el-radio-group v-model="multiStrategyForm.messageFormat">
          <el-radio label="text">纯文本</el-radio>
          <el-radio label="table">表格形式</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="钉钉通知">
        <el-switch v-model="multiStrategyForm.dingtalkEnabled"></el-switch>
        <div v-if="multiStrategyForm.dingtalkEnabled" style="margin-top: 10px;">
          <el-input 
            v-model="multiStrategyForm.dingtalkWebhook" 
            placeholder="请输入钉钉机器人Webhook URL"
            style="width: 80%;"
          ></el-input>
        </div>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="saveMultiStrategyConfig">保存配置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>
```

### 3.5 筛选服务模块

#### 3.5.1 execute_multiple_strategies 函数

```python
def execute_multiple_strategies(strategy_ids):
    """
    执行多个策略筛选
    :param strategy_ids: 策略ID列表
    :return: 各策略的筛选结果字典
    """
    results = {}
    for strategy_id in strategy_ids:
        try:
            result = execute_strategy_filter(strategy_id)
            results[strategy_id] = result
        except Exception as e:
            logger.error(f"执行策略 {strategy_id} 时出错: {str(e)}")
            results[strategy_id] = []
    
    return results
```

## 4. 用户策略保存逻辑

### 4.1 三维筛选面板操作流程

用户在[BeidanFilterPanel](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/frontend/src/views/admin/BeidanFilterPanel.vue#L1-L2656)页面上的策略保存流程：

1. **选择筛选条件**：
   - 在"实力等级差 ΔP"面板选择需要的实力差分层选项
   - 在"赢盘等级差 ΔWP"面板选择需要的盘路兑现力选项
   - 在"一赔稳定性 P-Tier"面板选择需要的正路可信度等级
   
2. **设置高级筛选**：
   - 选择联赛范围
   - 设置date_time筛选条件
   - 设置日期范围
   - 选择排序方式和顺序
   - 决定是否应用降级规则

3. **保存策略**：
   - 点击"保存策略"下拉菜单
   - 选择"保存当前策略"
   - 输入策略名称

### 4.2 策略数据结构

保存的策略包含以下字段：

```javascript
// 前端策略对象
const strategy = {
  name: "策略名称",                    // 策略名称
  powerDiffs: [],                     // ΔP筛选条件数组
  winPanDiffs: [],                    // ΔWP筛选条件数组
  stabilityTiers: [],                 // P-Tier筛选条件数组
  leagues: [],                        // 联赛筛选条件
  dateTime: "",                       // date_time筛选条件
  dateRange: [],                      // 日期范围
  sortBy: "p_level",                  // 排序字段
  sortOrder: "desc",                  // 排序顺序
  includeDerating: false,             // 是否包含降级规则
  preset: null                        // 快捷组合类型
};
```

### 4.3 策略保存API

```javascript
// 保存策略
async function saveStrategy(strategy) {
  const response = await fetch('/api/strategies', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify(strategy)
  });
  
  if (response.ok) {
    const result = await response.json();
    return result.id; // 返回策略ID
  } else {
    throw new Error('保存策略失败');
  }
}

// 加载策略
async function loadStrategy(strategyId) {
  const response = await fetch(`/api/strategies/${strategyId}`, {
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (response.ok) {
    return await response.json();
  } else {
    throw new Error('加载策略失败');
  }
}
```

### 4.4 策略应用逻辑

```javascript
// 应用策略到筛选面板
function applyStrategyToPanel(strategy) {
  // 应用筛选条件
  this.filterForm.powerDiffs = strategy.powerDiffs || [];
  this.filterForm.winPanDiffs = strategy.winPanDiffs || [];
  this.filterForm.stabilityTiers = strategy.stabilityTiers || [];
  
  // 应用高级筛选
  this.filterForm.leagues = strategy.leagues || [];
  this.filterForm.dateTime = strategy.dateTime || '';
  this.filterForm.dateRange = strategy.dateRange || [];
  this.filterForm.sortBy = strategy.sortBy || 'p_level';
  this.filterForm.sortOrder = strategy.sortOrder || 'desc';
  this.filterForm.includeDerating = strategy.includeDerating || false;
  
  // 更新策略详情显示
  this.selectedStrategy = strategy;
  this.strategyDetailItems = this.generateStrategyDetailItems(strategy);
}
```

### 4.5 策略自动执行配置

用户可以在已保存的策略基础上配置自动执行：

1. 选择已保存的策略
2. 配置执行频率（每天/每周/每小时）
3. 选择消息格式（文本/表格）
4. 配置钉钉通知
5. 保存自动执行设置

## 5. 数据库设计

### 5.1 multi_strategy_tasks 表

```sql
CREATE TABLE multi_strategy_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name VARCHAR(100) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    strategy_ids TEXT NOT NULL, -- JSON格式存储策略ID列表
    cron_expression VARCHAR(100) NOT NULL,
    message_format VARCHAR(20) DEFAULT 'text', -- 'text' 或 'table'
    dingtalk_webhook TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 strategies 表（如果需要存储策略定义）

```sql
CREATE TABLE strategies (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    definition TEXT NOT NULL, -- JSON格式存储策略配置
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 6. 筛选结果场次表设计

### 6.1 场次数据结构

基于[BeidanFilterPanel](file:///c%3A/Users/11581/Downloads/sport-lottery-sweeper/frontend/src/views/admin/BeidanFilterPanel.vue#L1-L2656)业务模块，筛选结果包含以下字段：

```python
# 场次数据结构示例
match_result = {
    "match_id": "20260212_001",      # 比赛ID
    "home_team": "AC米兰",            # 主队
    "away_team": "国际米兰",          # 客队
    "league": "意甲",                 # 联赛
    "match_time": "2026-02-12 19:30",  # 比赛时间
    "power_diff": 0.8,               # ΔP (实力等级差)
    "delta_wp": 0.5,                 # ΔWP (赢盘等级差)
    "p_level": 3,                    # P级 (一赔稳定性等级)
    "power_home": 85,                # 主队实力
    "power_away": 78,                # 客队实力
    "win_pan_home": 0.65,            # 主队赢盘率
    "win_pan_away": 0.45,            # 客队赢盘率
    "home_feature": "主强客弱",        # 主队特征
    "away_feature": "客队稳健",        # 客队特征
}
```

### 6.2 表格字段映射

基于BeidanFilterPanel筛选结果列表的字段，钉钉表格消息将包含以下字段（排除操作字段）：

| 表头 | 对应数据字段 | 说明 |
|------|-------------|------|
| 比赛ID | match_id | 比赛唯一标识 |
| 主队 | home_team | 比赛主队名称 |
| 客队 | away_team | 比赛客队名称 |
| 联赛 | league | 比赛所属联赛 |
| 比赛时间 | match_time | 比赛开始时间 |
| ΔP | power_diff | 实力等级差 |
| ΔWP | delta_wp | 赢盘等级差 |
| P级 | p_level | 一赔稳定性等级 |
| 主队实力 | power_home | 主队实力值 |
| 客队实力 | power_away | 客队实力值 |
| 主队赢盘 | win_pan_home | 主队赢盘率 |
| 客队赢盘 | win_pan_away | 客队赢盘率 |
| 主队特征 | home_feature | 主队特征 |
| 客队特征 | away_feature | 客队特征 |

注意：不包含"操作"列（如"分析"按钮等UI操作元素）

### 6.3 表格格式化实现

```python
def format_match_results_as_table(results_map):
    """
    将筛选结果格式化为场次表格
    :param results_map: 策略ID到筛选结果的映射
    :return: Markdown格式的表格内容
    """
    message = "📊【策略筛选场次表】\n\n"
    
    for strategy_id, results in results_map.items():
        strategy_name = get_strategy_name(strategy_id)
        message += f"**{strategy_name}** ({strategy_id}):\n\n"
        
        # 表格头部 - 基于BeidanFilterPanel筛选结果列表的字段
        message += "| 比赛ID | 主队 | 客队 | 联赛 | 比赛时间 | ΔP | ΔWP | P级 | 主队实力 | 客队实力 | 主队赢盘 | 客队赢盘 | 主队特征 | 客队特征 |\n"
        message += "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        
        # 表格内容
        for match in results[:10]:  # 限制显示前10场比赛
            message += (
                f"| {match['match_id']} | {match['home_team']} | {match['away_team']} | {match['league']} | "
                f"{match['match_time']} | {match['power_diff']} | {match['delta_wp']} | P{match['p_level']} | "
                f"{match['power_home']} | {match['power_away']} | {match['win_pan_home']} | {match['win_pan_away']} | "
                f"{match['home_feature']} | {match['away_feature']} |\n"
            )
        
        message += "\n"
    
    message += "\n🔗 完整结果请登录系统查看: http://localhost:3000/admin/beidan-filter"
    return message
```

## 7. API接口设计

### 7.1 保存多策略配置

```
POST /api/multi-strategy/config
Content-Type: application/json

{
  "task_name": "综合策略筛选",
  "strategy_ids": ["high_prob", "balanced_odds", "recent_form"],
  "cron_expression": "0 9 * * *",
  "message_format": "table",  -- 新增字段：消息格式
  "user_id": "user_456",
  "dingtalk_webhook": "https://oapi.dingtalk.com/robot/send?access_token=xxx",
  "enabled": true
}
```

### 7.2 获取用户的所有多策略配置

```
GET /api/multi-strategy/config?user_id=user_456
Response:
[
  {
    "id": 1,
    "task_name": "综合策略筛选",
    "strategy_ids": ["high_prob", "balanced_odds", "recent_form"],
    "cron_expression": "0 9 * * *",
    "message_format": "table",
    "dingtalk_webhook": "https://oapi.dingtalk.com/robot/send?access_token=xxx",
    "enabled": true
  }
]
```

### 7.3 手动执行多策略筛选

```
POST /api/multi-strategy/execute
Content-Type: application/json

{
  "strategy_ids": ["high_prob", "balanced_odds", "recent_form"],
  "message_format": "table"
}
```

## 8. 实现步骤

### 8.1 后端实现

1. 创建策略管理器类，支持注册和执行多种策略
2. 实现多策略定时任务调度器
3. 扩展筛选逻辑服务，支持多策略同时执行
4. 实现场次结果格式化为钉钉表格消息
5. 添加多策略相关的API端点
6. 更新数据库表结构，支持存储多策略配置和消息格式

### 8.2 前端实现

1. 修改BeidanFilterPanel.vue，增加多策略配置面板
2. 实现策略选择和批量配置功能
3. 添加消息格式选择（文本/表格）
4. 实现多策略执行历史展示
5. 实现手动执行多策略筛选按钮

### 8.3 策略扩展

1. 定义多种筛选策略算法
2. 提供策略测试接口，允许用户验证策略效果
3. 支持策略组合，允许用户自定义策略权重

## 9. 表格格式设计

### 9.1 表格列设计

基于BeidanFilterPanel筛选结果列表的字段，表格应包含以下列：
- 比赛ID
- 主队
- 客队
- 联赛
- 比赛时间
- ΔP (实力等级差)
- ΔWP (赢盘等级差)
- P级 (一赔稳定性等级)
- 主队实力
- 客队实力
- 主队赢盘
- 客队赢盘
- 主队特征
- 客队特征

注意：排除操作列（如"分析"按钮等UI操作元素）

### 9.2 Markdown表格格式

```markdown
| 比赛ID | 主队 | 客队 | 联赛 | 比赛时间 | ΔP | ΔWP | P级 | 主队实力 | 客队实力 | 主队赢盘 | 客队赢盘 | 主队特征 | 客队特征 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260212_001 | AC米兰 | 国际米兰 | 意甲 | 2026-02-12 19:30 | 0.8 | 0.5 | P3 | 85 | 78 | 0.65 | 0.45 | 主强客弱 | 客队稳健 |
```

## 10. 安全考虑

1. **策略权限控制**: 确保用户只能访问和执行自己有权使用的策略
2. **Webhook URL安全**: 加密存储钉钉Webhook URL，避免明文保存
3. **认证授权**: 确保只有任务所有者可以修改其多策略配置
4. **频率限制**: 防止过于频繁的任务创建，避免系统负载过高
5. **资源隔离**: 不同用户的策略任务在执行时应隔离，避免相互影响

## 11. 性能优化

1. **并发执行**: 多个策略可以并行执行以提高效率
2. **结果缓存**: 对相同输入的策略结果进行短期缓存
3. **任务队列**: 使用任务队列系统（如Celery）处理大量策略筛选任务
4. **分页处理**: 对大量筛选结果进行分页处理，避免一次性发送过多数据

## 12. 错误处理

1. **策略执行错误**: 单个策略失败不应影响其他策略的执行
2. **钉钉发送失败**: 实现重试机制和错误通知
3. **API验证**: 输入参数验证，防止恶意请求
4. **资源超限**: 监控内存和CPU使用，防止长时间运行任务

## 13. 部署配置

### 13.1 依赖安装

```bash
pip install apscheduler requests celery redis
```

### 13.2 系统初始化

确保在应用启动时初始化策略管理器和调度器：

```python
from services.multi_strategy_service import multi_strategy_scheduler
from services.strategy_manager import StrategyManager

# 注册内置策略
strategy_manager = StrategyManager()
strategy_manager.register_strategy('high_probability_winning', high_probability_winning_strategy)
strategy_manager.register_strategy('balanced_odds', balanced_odds_strategy)
strategy_manager.register_strategy('recent_form', recent_form_strategy)

# 初始化多策略调度器
multi_strategy_scheduler = MultiStrategyScheduler()
multi_strategy_scheduler.set_strategy_manager(strategy_manager)
```

## 14. 测试计划

### 14.1 单元测试

- 多策略管理器功能测试
- 策略注册和执行逻辑测试
- 多策略结果格式化测试
- 定时任务调度器功能测试
- 表格格式化函数测试

### 14.2 集成测试

- 前端多策略配置界面测试
- API端到端测试
- 多策略任务执行测试
- 钉钉表格消息发送测试

## 15. 维护指南

1. **监控任务执行**: 定期检查多策略任务执行日志
2. **性能监控**: 监控多策略筛选对系统资源的消耗
3. **错误恢复**: 实现任务失败后的恢复机制
4. **策略管理**: 提供策略效果统计和优化建议

## 16. 常见问题

1. **策略冲突**: 不同策略可能筛选出相同比赛，需去重处理
2. **执行时间过长**: 多策略并发执行可能导致系统负载过高
3. **表格长度限制**: 钉钉消息有长度限制，需限制表格行数
4. **配置复杂**: 多策略配置可能对用户来说过于复杂，需提供简单模式

---
文档版本: 1.5  
最后更新: 2026年2月11日