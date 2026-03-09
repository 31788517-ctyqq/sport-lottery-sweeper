# 任务执行监控系统开发文档

## 文档概述

### 1.1 项目背景
随着体育彩票数据采集系统的业务规模不断扩大，爬虫任务的数量和复杂度显著增加。当前系统虽然具备基本的任务状态显示功能，但缺乏集中、实时的任务执行监控能力，导致运维人员无法快速掌握任务执行的全貌，问题定位效率低下。

### 1.2 目标与范围
本系统旨在为爬虫任务提供一站式的执行监控解决方案，实现以下核心目标：
- **实时监控**：提供任务执行的实时状态更新，延迟不超过3秒
- **集中视图**：在一个页面中展示任务执行的全生命周期信息
- **问题诊断**：快速定位任务执行失败的根本原因
- **性能分析**：统计任务执行的成功率、平均耗时等关键指标

### 1.3 目标用户
- **系统管理员**：监控所有爬虫任务的执行状态
- **数据运营人员**：关注关键数据采集任务的完成情况
- **开发工程师**：调试和优化爬虫任务性能

## 功能需求

### 2.1 功能模块概览

| 模块名称 | 功能描述 | 优先级 |
|----------|----------|--------|
| 实时状态看板 | 显示当前运行任务数、成功率、平均耗时等关键指标 | 高 |
| 任务执行列表 | 展示所有任务的执行历史记录，支持分页和筛选 | 高 |
| 详细日志视图 | 提供任务执行全流程的日志查看，支持搜索和高亮 | 高 |
| 执行结果汇总 | 统计成功/失败数据，提供问题分析和建议 | 中 |
| 实时进度监控 | 动态显示任务执行进度，预估完成时间 | 中 |
| 告警通知系统 | 任务异常时自动发送通知（邮件、Slack等） | 中 |

### 2.2 详细功能说明

#### 2.2.1 实时状态看板
**功能要求：**
- 显示当前运行中的任务数量（RUNNING状态）
- 展示今日任务执行成功率（SUCCESS/总执行数）
- 显示平均任务执行耗时（最近24小时）
- 关键数据源可用性状态
- 系统资源使用情况（CPU、内存、磁盘）

**交互要求：**
- 数据每5秒自动刷新
- 点击指标可跳转到详细页面
- 异常状态用红色高亮显示

#### 2.2.2 任务执行列表
**功能要求：**
- 表格形式展示所有任务的执行记录
- 支持按任务名称、状态、时间范围筛选
- 支持按执行时间、耗时排序
- 每页显示20条记录，支持分页
- 显示任务基本信息：ID、名称、类型、状态、进度、开始时间、结束时间、耗时

**状态显示：**
- `PENDING`：灰色标签，表示待执行
- `RUNNING`：蓝色标签，显示进度条（0-100%）
- `SUCCESS`：绿色标签，显示耗时
- `FAILED`：红色标签，显示错误信息
- `CANCELLED`：灰色标签，显示取消原因

#### 2.2.3 详细日志视图
**功能要求：**
- 支持实时日志流显示（WebSocket推送）
- 日志级别分类：INFO、WARNING、ERROR、DEBUG
- 支持关键词搜索和高亮
- 可折叠/展开长日志内容
- 支持日志下载（TXT格式）
- 显示日志时间戳、级别、来源、消息内容

**技术实现：**
- 前端使用`vue-use-webSocket`接收实时日志
- 后端通过WebSocket服务推送日志更新
- 日志格式标准化：`[时间戳] [级别] [模块] - 消息内容`

#### 2.2.4 执行结果汇总
**功能要求：**
- 统计图表：成功/失败任务数量对比
- 趋势分析：任务执行耗时变化趋势
- 问题分布：失败原因类型分布
- 数据质量评分：基于采集数据的完整性、准确性
- 优化建议：基于历史数据提供改进建议

**可视化要求：**
- 使用ECharts或Chart.js实现动态图表
- 图表支持交互：悬停显示详情、点击筛选
- 响应式设计，适配不同屏幕尺寸

## 技术架构

### 3.1 总体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                          前端界面层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ 状态看板    │  │ 任务列表    │  │ 日志视图    │           │
│  │ Vue组件     │  │ Vue组件     │  │ Vue组件     │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP API + WebSocket
┌───────────────────────────▼─────────────────────────────────────┐
│                         API网关层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ 任务监控API │  │ 日志推送API │  │ 统计查询API │           │
│  │ FastAPI     │  │ FastAPI     │  │ FastAPI     │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└───────────────────────────┬─────────────────────────────────────┘
                            │ 业务逻辑调用
┌───────────────────────────▼─────────────────────────────────────┐
│                        业务服务层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │任务监控服务 │  │日志记录服务 │  │统计分析服务 │           │
│  │TaskMonitor-│  │EnhancedLog-  │  │StatsAnaly-  │           │
│  │Service     │  │gingService   │  │sisService   │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└───────────────────────────┬─────────────────────────────────────┘
                            │ 数据访问
┌───────────────────────────▼─────────────────────────────────────┐
│                        数据持久层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ 任务执行表  │  │ 任务日志表  │  │ 监控指标表  │           │
│  │CrawlerTask- │  │CrawlerTask- │  │CrawlerMetric│           │
│  │Execution    │  │Log          │  │             │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 技术栈选择

#### 前端技术栈
- **框架**：Vue 3 + Composition API + TypeScript
- **UI组件库**：Element Plus
- **状态管理**：Pinia
- **路由管理**：Vue Router 4
- **HTTP客户端**：Axios
- **WebSocket**：原生WebSocket API + `vue-use-webSocket`
- **图表库**：ECharts 5
- **构建工具**：Vite 4

#### 后端技术栈
- **框架**：FastAPI + Python 3.11
- **数据库ORM**：SQLAlchemy 2.0 + Alembic
- **WebSocket支持**：FastAPI WebSocket endpoints
- **缓存**：Redis 7（用于实时状态缓存）
- **任务队列**：Celery + Redis（可选，用于异步处理）
- **API文档**：Swagger UI（自动生成）

#### 数据库技术栈
- **主数据库**：SQLite 3（开发环境）/ PostgreSQL 15（生产环境）
- **缓存数据库**：Redis 7
- **监控数据存储**：时序数据库（可选，Prometheus）

### 3.3 关键设计原则

#### 3.3.1 实时性原则
- WebSocket连接保持活跃，服务器主动推送状态更新
- 状态更新延迟不超过3秒
- 客户端自动重连机制，网络异常时恢复连接

#### 3.3.2 可扩展性原则
- 模块化设计，各功能模块独立可扩展
- 支持插件式架构，可快速添加新的监控指标
- 水平扩展支持，可通过负载均衡分散压力

#### 3.3.3 可靠性原则
- 关键数据持久化，防止数据丢失
- 异常处理机制，系统局部故障不影响整体运行
- 监控系统自监控，确保监控系统自身健康

## 数据库设计

### 4.1 数据模型ER图

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  CrawlerTask    │1─────○│TaskExecution    │○─────1│  TaskLog        │
│                 │       │                 │       │                 │
│  - id           │       │  - id           │       │  - id           │
│  - name         │       │  - task_id      │       │  - execution_id │
│  - type         │       │  - status       │       │  - log_level    │
│  - description  │       │  - progress     │       │  - message      │
│  - config       │       │  - started_at   │       │  - details      │
│  - created_at   │       │  - ended_at     │       │  - created_at   │
│  - updated_at   │       │  - duration     │       │                 │
└─────────────────┘       └─────────────────┘       └─────────────────┘
         │                         │
         │ 1                     ○ │ 1
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│  DataSource     │       │  TaskMetric     │
│                 │       │                 │
│  - id           │       │  - id           │
│  - name         │       │  - execution_id │
│  - url          │       │  - metric_type  │
│  - category     │       │  - metric_value │
│  - status       │       │  - recorded_at  │
│  - last_check   │       │                 │
└─────────────────┘       └─────────────────┘
```

### 4.2 核心表结构设计

#### 4.2.1 任务执行表 (task_executions)
```sql
CREATE TABLE task_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'RUNNING', 'SUCCESS', 'FAILED', 'CANCELLED')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration INTEGER, -- 单位：秒
    error_message TEXT,
    error_details JSON,
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (task_id) REFERENCES crawler_tasks(id) ON DELETE CASCADE,
    INDEX idx_task_executions_status (status),
    INDEX idx_task_executions_started_at (started_at),
    INDEX idx_task_executions_task_id (task_id)
);
```

#### 4.2.2 任务日志表 (task_logs)
```sql
CREATE TABLE task_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER NOT NULL,
    log_level VARCHAR(10) NOT NULL CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    message TEXT NOT NULL,
    details JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (execution_id) REFERENCES task_executions(id) ON DELETE CASCADE,
    INDEX idx_task_logs_execution_id (execution_id),
    INDEX idx_task_logs_level (log_level),
    INDEX idx_task_logs_timestamp (timestamp)
);
```

#### 4.2.3 任务监控指标表 (task_metrics)
```sql
CREATE TABLE task_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(20),
    tags JSON,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (execution_id) REFERENCES task_executions(id) ON DELETE CASCADE,
    INDEX idx_task_metrics_execution_id (execution_id),
    INDEX idx_task_metrics_type (metric_type),
    INDEX idx_task_metrics_recorded_at (recorded_at)
);
```

### 4.3 数据分区策略

#### 4.3.1 按时间分区
- 任务日志表按月分区：`task_logs_2026_01`, `task_logs_2026_02`
- 任务执行表按周分区：`task_executions_2026_w01`, `task_executions_2026_w02`

#### 4.3.2 数据归档策略
- 超过3个月的详细日志迁移到归档存储
- 超过1年的执行记录汇总后删除明细
- 实时监控数据保留7天，历史数据压缩存储

## API设计

### 5.1 API概览

| 类别 | 端点 | 方法 | 描述 |
|------|------|------|------|
| 任务执行 | `/api/v1/task-monitor/executions` | GET | 获取任务执行列表 |
| 任务执行 | `/api/v1/task-monitor/executions/{id}` | GET | 获取单个执行详情 |
| 任务执行 | `/api/v1/task-monitor/executions/{id}/cancel` | POST | 取消正在执行的任务 |
| 任务日志 | `/api/v1/task-monitor/executions/{id}/logs` | GET | 获取任务执行日志 |
| 任务日志 | `/api/v1/task-monitor/executions/{id}/logs/stream` | WebSocket | 实时日志流 |
| 任务统计 | `/api/v1/task-monitor/statistics/daily` | GET | 获取每日统计 |
| 任务统计 | `/api/v1/task-monitor/statistics/top-issues` | GET | 获取主要问题排行 |
| 实时状态 | `/api/v1/task-monitor/realtime/overview` | GET | 获取实时概览 |
| 实时状态 | `/api/v1/task-monitor/realtime/metrics` | WebSocket | 实时指标推送 |

### 5.2 详细接口规范

#### 5.2.1 获取任务执行列表
**端点：** `GET /api/v1/task-monitor/executions`

**请求参数：**
```json
{
  "page": 1,
  "page_size": 20,
  "status": ["RUNNING", "FAILED"],
  "task_id": 123,
  "start_date": "2026-02-01",
  "end_date": "2026-02-04",
  "sort_by": "started_at",
  "sort_order": "desc"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 456,
        "task_id": 123,
        "task_name": "500彩票网赛程采集",
        "status": "RUNNING",
        "progress": 65,
        "started_at": "2026-02-04T10:30:00Z",
        "ended_at": null,
        "duration": 120,
        "error_message": null,
        "records_processed": 1250,
        "records_failed": 5
      }
    ],
    "total": 150,
    "page": 1,
    "page_size": 20
  }
}
```

#### 5.2.2 WebSocket实时日志流
**端点：** `ws://localhost:8000/api/v1/task-monitor/executions/{id}/logs/stream`

**连接建立：**
```javascript
const ws = new WebSocket(`ws://localhost:8000/api/v1/task-monitor/executions/456/logs/stream`);

ws.onmessage = (event) => {
  const logEntry = JSON.parse(event.data);
  console.log(`[${logEntry.timestamp}] [${logEntry.level}] ${logEntry.message}`);
};
```

**推送消息格式：**
```json
{
  "type": "log_entry",
  "data": {
    "id": 7890,
    "execution_id": 456,
    "log_level": "INFO",
    "message": "已成功获取第5页数据，共50条记录",
    "details": {"page": 5, "records": 50},
    "timestamp": "2026-02-04T10:35:12Z"
  }
}
```

### 5.3 错误码定义

| 错误码 | 描述 | HTTP状态码 |
|--------|------|------------|
| TM4001 | 参数验证失败 | 400 |
| TM4002 | 任务执行ID不存在 | 404 |
| TM4003 | 任务已结束，无法取消 | 409 |
| TM5001 | 内部服务器错误 | 500 |
| TM5002 | 数据库连接失败 | 500 |
| TM5003 | WebSocket连接异常 | 500 |

## 前端实现

### 6.1 组件结构

```
src/views/admin/task-monitor/
├── TaskExecutionMonitor.vue     # 主页面容器
├── components/
│   ├── RealtimeDashboard.vue    # 实时状态看板
│   ├── ExecutionList.vue        # 任务执行列表
│   ├── LogViewer.vue           # 详细日志视图
│   ├── StatisticsPanel.vue     # 统计图表面板
│   └── ProgressTracker.vue     # 实时进度监控
└── stores/
    └── taskMonitorStore.js     # Pinia状态管理
```

### 6.2 核心组件实现

#### 6.2.1 TaskExecutionMonitor.vue（主页面）
```vue
<template>
  <div class="task-execution-monitor">
    <el-container>
      <!-- 顶部状态看板 -->
      <el-header height="auto">
        <RealtimeDashboard :metrics="dashboardMetrics" />
      </el-header>
      
      <!-- 主要内容区 -->
      <el-main>
        <el-row :gutter="20">
          <!-- 左侧任务列表 -->
          <el-col :span="16">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>任务执行列表</span>
                  <el-button type="primary" @click="refreshList">刷新</el-button>
                </div>
              </template>
              <ExecutionList 
                :executions="executions"
                :loading="loading"
                @view-details="handleViewDetails"
                @cancel-execution="handleCancelExecution"
              />
            </el-card>
          </el-col>
          
          <!-- 右侧统计面板 -->
          <el-col :span="8">
            <StatisticsPanel :stats="statistics" />
          </el-col>
        </el-row>
        
        <!-- 日志查看器抽屉 -->
        <el-drawer 
          v-model="logDrawerVisible"
          title="任务执行日志"
          size="60%"
          :destroy-on-close="true"
        >
          <LogViewer 
            v-if="logDrawerVisible"
            :execution-id="selectedExecutionId"
            :websocket-connected="websocketConnected"
          />
        </el-drawer>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useTaskMonitorStore } from '@/stores/taskMonitorStore'
import RealtimeDashboard from './components/RealtimeDashboard.vue'
import ExecutionList from './components/ExecutionList.vue'
import LogViewer from './components/LogViewer.vue'
import StatisticsPanel from './components/StatisticsPanel.vue'

const store = useTaskMonitorStore()
const executions = ref([])
const loading = ref(false)
const logDrawerVisible = ref(false)
const selectedExecutionId = ref(null)
const websocketConnected = ref(false)

// 初始化数据
onMounted(async () => {
  await refreshList()
  store.connectWebSocket() // 连接WebSocket
})

// 清理资源
onUnmounted(() => {
  store.disconnectWebSocket()
})

// 刷新任务列表
const refreshList = async () => {
  loading.value = true
  try {
    executions.value = await store.fetchExecutions({
      page: 1,
      page_size: 20,
      status: ['RUNNING', 'PENDING', 'FAILED']
    })
  } finally {
    loading.value = false
  }
}

// 查看任务详情
const handleViewDetails = (executionId) => {
  selectedExecutionId.value = executionId
  logDrawerVisible.value = true
}

// 取消任务执行
const handleCancelExecution = async (executionId) => {
  await store.cancelExecution(executionId)
  await refreshList()
}
</script>
```

#### 6.2.2 Pinia状态管理 (taskMonitorStore.js)
```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import taskMonitorApi from '@/api/taskMonitorApi'

export const useTaskMonitorStore = defineStore('taskMonitor', () => {
  // 状态定义
  const executions = ref([])
  const totalCount = ref(0)
  const currentPage = ref(1)
  const websocket = ref(null)
  const connected = ref(false)
  
  // Getter计算属性
  const runningTasks = computed(() => 
    executions.value.filter(task => task.status === 'RUNNING')
  )
  
  const successRate = computed(() => {
    const successful = executions.value.filter(task => task.status === 'SUCCESS').length
    const total = executions.value.length
    return total > 0 ? (successful / total * 100).toFixed(2) : 0
  })
  
  // Actions
  const fetchExecutions = async (params = {}) => {
    const response = await taskMonitorApi.getExecutions(params)
    executions.value = response.data.items
    totalCount.value = response.data.total
    currentPage.value = response.data.page
    return executions.value
  }
  
  const cancelExecution = async (executionId) => {
    await taskMonitorApi.cancelExecution(executionId)
    // 更新本地状态
    const index = executions.value.findIndex(exec => exec.id === executionId)
    if (index !== -1) {
      executions.value[index].status = 'CANCELLED'
    }
  }
  
  // WebSocket管理
  const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/api/v1/task-monitor/realtime/metrics`
    
    websocket.value = new WebSocket(wsUrl)
    
    websocket.value.onopen = () => {
      connected.value = true
      console.log('WebSocket连接已建立')
    }
    
    websocket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      // 处理实时数据更新
      handleRealtimeUpdate(data)
    }
    
    websocket.value.onclose = () => {
      connected.value = false
      console.log('WebSocket连接已关闭')
      // 尝试重连
      setTimeout(connectWebSocket, 5000)
    }
  }
  
  const disconnectWebSocket = () => {
    if (websocket.value) {
      websocket.value.close()
      websocket.value = null
    }
  }
  
  const handleRealtimeUpdate = (data) => {
    // 根据数据类型更新对应状态
    switch (data.type) {
      case 'task_progress':
        updateTaskProgress(data.task_id, data.progress)
        break
      case 'task_status':
        updateTaskStatus(data.task_id, data.status)
        break
      case 'metric_update':
        updateMetrics(data.metrics)
        break
    }
  }
  
  return {
    executions,
    totalCount,
    runningTasks,
    successRate,
    connected,
    fetchExecutions,
    cancelExecution,
    connectWebSocket,
    disconnectWebSocket
  }
})
```

### 6.3 路由配置

在 `frontend/src/router/index.js` 中添加路由：

```javascript
{
  path: '/admin/task-monitor',
  name: 'TaskExecutionMonitor',
  component: () => import('@/views/admin/task-monitor/TaskExecutionMonitor.vue'),
  meta: {
    title: '任务执行监控',
    icon: 'monitor',
    roles: ['admin', 'manager'],
    requiresAuth: true
  }
}
```

## 后端实现

### 7.1 服务层设计

#### 7.1.1 任务监控服务 (TaskMonitorService)
```python
# backend/services/task_monitor_service.py
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import json
import asyncio

from backend.models.crawler_task import CrawlerTask, CrawlerTaskLog
from backend.models.task_execution import TaskExecution, TaskLog, TaskMetric
from backend.schemas.task_monitor import (
    ExecutionCreate, ExecutionUpdate, 
    LogEntryCreate, MetricRecordCreate
)

class TaskMonitorService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_execution(self, task_id: int, execution_data: ExecutionCreate) -> TaskExecution:
        """创建新的任务执行记录"""
        execution = TaskExecution(
            task_id=task_id,
            status=execution_data.status or 'PENDING',
            progress=execution_data.progress or 0,
            started_at=execution_data.started_at or datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        
        return execution
    
    def update_execution_status(self, execution_id: int, status: str, progress: int = None) -> TaskExecution:
        """更新任务执行状态"""
        execution = self.db.query(TaskExecution).filter(TaskExecution.id == execution_id).first()
        if not execution:
            raise ValueError(f"执行记录 {execution_id} 不存在")
        
        execution.status = status
        execution.updated_at = datetime.utcnow()
        
        if progress is not None:
            execution.progress = progress
        
        if status in ['SUCCESS', 'FAILED', 'CANCELLED']:
            execution.ended_at = datetime.utcnow()
            if execution.started_at:
                execution.duration = (execution.ended_at - execution.started_at).total_seconds()
        
        self.db.commit()
        self.db.refresh(execution)
        
        # 触发状态变更事件
        self._publish_status_change(execution)
        
        return execution
    
    def add_task_log(self, execution_id: int, log_entry: LogEntryCreate) -> TaskLog:
        """添加任务执行日志"""
        task_log = TaskLog(
            execution_id=execution_id,
            log_level=log_entry.log_level,
            message=log_entry.message,
            details=json.dumps(log_entry.details) if log_entry.details else None,
            timestamp=log_entry.timestamp or datetime.utcnow()
        )
        
        self.db.add(task_log)
        self.db.commit()
        self.db.refresh(task_log)
        
        # 触发日志推送事件
        self._publish_log_entry(task_log)
        
        return task_log
    
    def record_metric(self, execution_id: int, metric_data: MetricRecordCreate) -> TaskMetric:
        """记录任务执行指标"""
        metric = TaskMetric(
            execution_id=execution_id,
            metric_type=metric_data.metric_type,
            metric_value=metric_data.metric_value,
            metric_unit=metric_data.metric_unit,
            tags=json.dumps(metric_data.tags) if metric_data.tags else None,
            recorded_at=metric_data.recorded_at or datetime.utcnow()
        )
        
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        
        return metric
    
    def get_execution_list(
        self, 
        page: int = 1, 
        page_size: int = 20,
        status: List[str] = None,
        task_id: int = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict:
        """获取任务执行列表"""
        query = self.db.query(TaskExecution)
        
        # 应用筛选条件
        if status:
            query = query.filter(TaskExecution.status.in_(status))
        
        if task_id:
            query = query.filter(TaskExecution.task_id == task_id)
        
        if start_date:
            query = query.filter(TaskExecution.started_at >= start_date)
        
        if end_date:
            query = query.filter(TaskExecution.started_at <= end_date)
        
        # 计算总数
        total = query.count()
        
        # 应用排序和分页
        executions = query.order_by(desc(TaskExecution.started_at)) \
                         .offset((page - 1) * page_size) \
                         .limit(page_size) \
                         .all()
        
        return {
            "items": executions,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    def get_realtime_overview(self) -> Dict:
        """获取实时概览数据"""
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 当前运行任务数
        running_count = self.db.query(func.count(TaskExecution.id)) \
                              .filter(TaskExecution.status == 'RUNNING') \
                              .scalar() or 0
        
        # 今日任务统计
        today_stats = self.db.query(
            func.count(TaskExecution.id).label('total'),
            func.sum(case([(TaskExecution.status == 'SUCCESS', 1)], else_=0)).label('success'),
            func.avg(TaskExecution.duration).label('avg_duration')
        ).filter(TaskExecution.started_at >= today_start) \
         .first()
        
        # 最近1小时错误率
        recent_errors = self.db.query(func.count(TaskExecution.id)) \
                              .filter(TaskExecution.status == 'FAILED') \
                              .filter(TaskExecution.started_at >= one_hour_ago) \
                              .scalar() or 0
        
        recent_total = self.db.query(func.count(TaskExecution.id)) \
                             .filter(TaskExecution.started_at >= one_hour_ago) \
                             .scalar() or 0
        
        error_rate = (recent_errors / recent_total * 100) if recent_total > 0 else 0
        
        return {
            "running_tasks": running_count,
            "today_total": today_stats.total or 0,
            "today_success": today_stats.success or 0,
            "success_rate": (today_stats.success / today_stats.total * 100) if today_stats.total > 0 else 100,
            "avg_duration": today_stats.avg_duration or 0,
            "hourly_error_rate": error_rate
        }
    
    def _publish_status_change(self, execution: TaskExecution):
        """发布状态变更事件（用于WebSocket推送）"""
        # 实际实现中会通过消息队列或事件总线发送
        pass
    
    def _publish_log_entry(self, task_log: TaskLog):
        """发布日志条目事件（用于WebSocket推送）"""
        # 实际实现中会通过消息队列或事件总线发送
        pass
```

### 7.2 WebSocket服务实现

```python
# backend/api/v1/task_monitor_ws.py
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json
import asyncio

from backend.database_utils import get_db
from backend.services.task_monitor_service import TaskMonitorService

class TaskMonitorWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, execution_id: int, websocket: WebSocket):
        await websocket.accept()
        if execution_id not in self.active_connections:
            self.active_connections[execution_id] = []
        self.active_connections[execution_id].append(websocket)
    
    def disconnect(self, execution_id: int, websocket: WebSocket):
        if execution_id in self.active_connections:
            self.active_connections[execution_id].remove(websocket)
            if not self.active_connections[execution_id]:
                del self.active_connections[execution_id]
    
    async def broadcast_to_execution(self, execution_id: int, message: dict):
        if execution_id in self.active_connections:
            for connection in self.active_connections[execution_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = TaskMonitorWebSocketManager()

# WebSocket端点
@router.websocket("/executions/{execution_id}/logs/stream")
async def websocket_log_stream(
    websocket: WebSocket, 
    execution_id: int,
    db: Session = Depends(get_db)
):
    """实时日志流WebSocket端点"""
    await manager.connect(execution_id, websocket)
    
    try:
        # 发送历史日志
        monitor_service = TaskMonitorService(db)
        logs = monitor_service.get_execution_logs(execution_id, limit=100)
        
        for log in logs:
            await websocket.send_json({
                "type": "log_entry",
                "data": {
                    "id": log.id,
                    "log_level": log.log_level,
                    "message": log.message,
                    "timestamp": log.timestamp.isoformat(),
                    "details": json.loads(log.details) if log.details else None
                }
            })
        
        # 保持连接，接收客户端消息
        while True:
            data = await websocket.receive_text()
            # 处理客户端请求（如过滤日志级别等）
            
    except WebSocketDisconnect:
        manager.disconnect(execution_id, websocket)
```

## 测试策略

### 8.1 单元测试

#### 8.1.1 服务层测试
```python
# tests/unit/services/test_task_monitor_service.py
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from backend.services.task_monitor_service import TaskMonitorService
from backend.models.task_execution import TaskExecution

def test_create_execution():
    """测试创建任务执行记录"""
    mock_db = Mock()
    service = TaskMonitorService(mock_db)
    
    execution_data = {
        "task_id": 1,
        "status": "PENDING",
        "progress": 0
    }
    
    with patch.object(mock_db, 'add') as mock_add:
        result = service.create_execution(1, execution_data)
        
        assert result.task_id == 1
        assert result.status == "PENDING"
        mock_add.assert_called_once()

def test_update_execution_status():
    """测试更新任务执行状态"""
    mock_db = Mock()
    mock_execution = TaskExecution(
        id=1,
        task_id=1,
        status="RUNNING",
        started_at=datetime.utcnow()
    )
    
    mock_db.query.return_value.filter.return_value.first.return_value = mock_execution
    
    service = TaskMonitorService(mock_db)
    result = service.update_execution_status(1, "SUCCESS", progress=100)
    
    assert result.status == "SUCCESS"
    assert result.progress == 100
    assert result.ended_at is not None
    assert result.duration > 0
```

### 8.2 集成测试

#### 8.2.1 API集成测试
```python
# tests/integration/api/test_task_monitor_api.py
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

def test_get_execution_list(client: TestClient, auth_token: str):
    """测试获取任务执行列表API"""
    response = client.get(
        "/api/v1/task-monitor/executions",
        headers={"Authorization": f"Bearer {auth_token}"},
        params={
            "page": 1,
            "page_size": 10,
            "status": ["RUNNING", "SUCCESS"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data
    assert "items" in data["data"]
    assert "total" in data["data"]

def test_cancel_execution(client: TestClient, auth_token: str, execution_id: int):
    """测试取消任务执行API"""
    response = client.post(
        f"/api/v1/task-monitor/executions/{execution_id}/cancel",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
```

### 8.3 端到端测试

#### 8.3.1 前端E2E测试
```javascript
// tests/e2e/task-monitor.spec.js
describe('任务执行监控页面', () => {
  beforeEach(async () => {
    await page.goto('http://localhost:3000/admin/task-monitor')
  })
  
  test('应显示实时状态看板', async () => {
    await expect(page).toHaveSelector('.realtime-dashboard')
    await expect(page).toHaveTextContent('运行中任务')
  })
  
  test('应显示任务执行列表', async () => {
    await expect(page).toHaveSelector('.execution-list-table')
    const rows = await page.$$('.el-table__row')
    expect(rows.length).toBeGreaterThan(0)
  })
  
  test('点击日志按钮应打开日志抽屉', async () => {
    const logButton = await page.$('.view-log-btn')
    await logButton.click()
    
    await expect(page).toHaveSelector('.el-drawer')
    await expect(page).toHaveTextContent('任务执行日志')
  })
})
```

## 部署指南

### 9.1 环境要求

#### 9.1.1 软件要求
- **Python**: 3.11+
- **Node.js**: 18+
- **数据库**: SQLite 3.35+ (开发), PostgreSQL 15+ (生产)
- **Redis**: 7.0+ (用于WebSocket和缓存)
- **Nginx**: 1.20+ (生产环境反向代理)

#### 9.1.2 硬件要求
| 环境 | CPU | 内存 | 存储 |
|------|-----|------|------|
| 开发 | 2核 | 4GB | 20GB |
| 测试 | 4核 | 8GB | 50GB |
| 生产 | 8核 | 16GB | 200GB+ |

### 9.2 部署步骤

#### 9.2.1 后端部署
```bash
# 1. 安装依赖
cd backend
pip install -r requirements.txt

# 2. 数据库迁移
alembic upgrade head

# 3. 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 9.2.2 前端部署
```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 构建生产版本
npm run build

# 3. 启动服务
npm run preview
```

#### 9.2.3 Docker部署
```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 9.3 配置管理

#### 9.3.1 环境变量配置
```bash
# .env.production
DATABASE_URL=postgresql://user:password@localhost:5432/sport_lottery
REDIS_URL=redis://localhost:6379/0
WEB_SOCKET_PORT=8001
LOG_LEVEL=INFO
```

#### 9.3.2 Nginx配置
```nginx
# nginx/task-monitor.conf
server {
    listen 80;
    server_name task-monitor.example.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

## 运维监控

### 10.1 系统监控指标

#### 10.1.1 应用层指标
- **任务执行成功率**: `task_execution_success_rate`
- **平均执行耗时**: `task_avg_duration_seconds`
- **实时连接数**: `websocket_active_connections`
- **API响应时间**: `api_response_time_ms`

#### 10.1.2 基础设施指标
- **CPU使用率**: `system_cpu_usage_percent`
- **内存使用量**: `system_memory_usage_bytes`
- **数据库连接数**: `db_connections_count`
- **磁盘空间**: `disk_usage_percent`

### 10.2 告警规则配置

#### 10.2.1 关键告警规则
```yaml
alert_rules:
  - name: "任务执行失败率过高"
    metric: "task_execution_success_rate"
    condition: "< 90"
    duration: "5m"
    severity: "critical"
    
  - name: "WebSocket连接异常"
    metric: "websocket_active_connections"
    condition: "== 0"
    duration: "1m"
    severity: "warning"
    
  - name: "API响应时间过长"
    metric: "api_response_time_ms"
    condition: "> 5000"
    duration: "3m"
    severity: "warning"
```

### 10.3 日志管理

#### 10.3.1 日志级别配置
```python
# logging_config.py
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/task-monitor/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file"]
    }
}
```

## 附录

### A.1 术语表

| 术语 | 定义 |
|------|------|
| 任务执行 | 一次具体的爬虫任务运行实例 |
| 执行状态 | 任务执行的当前状态（PENDING/RUNNING等） |
| 进度 | 任务执行完成的百分比（0-100） |
| 日志条目 | 任务执行过程中产生的日志记录 |
| 监控指标 | 用于衡量任务执行性能的量化指标 |

### A.2 常见问题解答

**Q1: 任务状态长时间显示为RUNNING但进度不更新**
A: 可能原因：1) 爬虫任务卡死；2) 日志记录服务异常。建议检查任务进程状态和日志服务连接。

**Q2: WebSocket连接频繁断开**
A: 可能原因：1) 网络不稳定；2) 服务器资源不足。建议检查网络连接和服务器负载。

**Q3: 实时数据更新延迟较大**
A: 可能原因：1) 数据库查询性能问题；2) WebSocket消息堆积。建议优化数据库索引和调整推送频率。

### A.3 性能优化建议

1. **数据库优化**
   - 为频繁查询的字段添加索引
   - 对大表进行分区处理
   - 定期清理历史数据

2. **前端优化**
   - 使用虚拟滚动处理大量数据
   - 实现组件懒加载
   - 优化WebSocket消息处理逻辑

3. **后端优化**
   - 使用连接池管理数据库连接
   - 实现缓存机制减少数据库查询
   - 异步处理非关键业务逻辑

---

**文档版本**: 1.0  
**最后更新**: 2026-02-04  
**作者**: 系统开发团队  
**审核状态**: 待审核