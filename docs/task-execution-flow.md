```
task-execution-flow.md
# 任务执行全流程文档

本文档详细描述了爬虫任务从创建、启动到完成的完整执行流程，包括网络层、数据层和渲染层的交互细节。

## 1. 任务执行流程概述

当用户在任务控制台创建并启动一个爬虫任务时，系统会经历以下主要阶段：

1. **任务创建**：用户填写任务表单并提交
2. **任务启动**：用户点击"启动"按钮触发任务执行
3. **任务执行**：系统执行爬虫逻辑，抓取、清洗和存储数据
4. **状态监控**：系统实时更新任务状态和进度
5. **结果验证**：用户可查看任务结果和日志

## 2. 网络层分析

### 2.1 任务创建过程

当用户提交新建任务表单时：

```javascript
// frontend/src/api/crawlerTask.js
export function createTask(data) {
  return request({
    url: '/api/admin/crawler/tasks',
    method: 'post',
    data
  })
}
```

- **请求URL**: `POST /api/admin/crawler/tasks`
- **请求头**: 包含认证令牌(如JWT)
- **请求体**: 包含任务名称、类型、数据源ID、配置等JSON数据

后端处理流程：

1. 适配器接收请求：`/api/admin/crawler/tasks`
2. 适配器转发到实际的创建任务函数
3. 服务端验证数据并创建任务记录
4. 返回任务ID和其他基本信息

### 2.2 任务启动与停止过程

当用户点击"启动/停止"按钮时：

```javascript
// frontend/src/views/admin/crawler/TaskConsole.vue
const handleToggleTask = async (task) => {
  try {
    // 设置加载状态
    task.loadingTrigger = true;

    if (task.status === 'RUNNING') {
      // 如果任务正在运行，则停止任务
      await stopTask(task.id);
      ElMessage.success('任务停止成功');
      
      // 更新任务状态
      task.status = 'STOPPED';
    } else {
      // 如果任务不在运行，则启动任务
      await triggerTask(task.id);
      ElMessage.success('任务启动成功');
      
      // 更新任务状态，设置开始时间为当前时间
      task.status = 'RUNNING';
      task.started_at = new Date().toISOString();
    }
    
    // 重新加载任务列表以获取最新状态
    loadTasks();
    loadStatistics();
  } catch (error) {
    console.error(task.status === 'RUNNING' ? '停止任务失败:' : '启动任务失败:', error);
    ElMessage.error(task.status === 'RUNNING' ? '停止任务失败' : '启动任务失败');
  } finally {
    // 清除加载状态
    task.loadingTrigger = false;
  }
};
```

- **启动请求URL**: `POST /api/admin/crawler/tasks/{id}/trigger`
- **停止请求URL**: `POST /api/admin/crawler/tasks/{id}/stop`
- **请求体**: 通常为空，因为只需要任务ID

后端处理流程：

1. 接收触发或停止任务请求
2. 更新任务状态为"RUNNING"或"STOPPED"
3. 将任务添加到调度队列或从运行列表中移除
4. 返回操作结果

### 2.3 状态监控机制

前端通过轮询或WebSocket获取任务状态：

```javascript
// frontend/src/views/admin/crawler/TaskConsole.vue
const loadTasks = async () => {
  try {
    loading.value = true
    const response = await listTasks({
      page: pagination.page,
      size: pagination.size,
      ...filters
    })
    // 更新任务列表
  } finally {
    loading.value = false
  }
}
```

## 3. 数据层分析

### 3.1 任务数据模型

```python
# backend/models/crawler_tasks.py
class CrawlerTask(Base):
    __tablename__ = 'crawler_tasks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    source_id = Column(Integer, ForeignKey('data_sources.id'), nullable=False)
    task_type = Column(String(50), nullable=False)
    cron_expression = Column(String(50))
    is_active = Column(Boolean, default=True)
    status = Column(String(50), default='PENDING')
    last_run_time = Column(DateTime)
    next_run_time = Column(DateTime)
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    progress = Column(Integer, default=0)  # 进度字段
    config = Column(Text, default='{}')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 3.2 任务启动/停止处理

```python
# backend/services/task_scheduler_service.py
def trigger_task(self, task_id: int, triggered_by: int) -> Dict[str, Any]:
    # 查找任务
    task = self.db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()
    if not task:
        return {
            "success": False,
            "message": "任务不存在",
            "task_id": task_id
        }
    
    # 更新任务状态为运行中
    task.status = "RUNNING"
    task.last_run_time = datetime.utcnow()
    task.run_count = task.run_count + 1
    self.db.commit()
    
    # 记录任务开始执行的日志
    log_entry = CrawlerTaskLog(
        task_id=task.id,
        source_id=task.source_id,
        status="RUNNING",
        started_at=datetime.utcnow(),
        records_processed=0,
        records_success=0,
        records_failed=0,
        error_message=None
    )
    self.db.add(log_entry)
    self.db.commit()
    
    # 在新线程中执行任务，不阻塞API响应
    def execute_task():
        # 任务执行逻辑
        pass
    
    thread = threading.Thread(target=execute_task)
    thread.start()
    
    # 记录线程信息以便后续停止任务
    self._running_tasks[task_id] = thread

    return {
        "success": True,
        "message": "任务已触发执行",
        "task_id": task_id
    }

def stop_task(self, task_id: int) -> Dict[str, Any]:
    # 检查任务是否存在
    task = self.db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()
    if not task:
        return {
            "success": False,
            "message": "任务不存在",
            "task_id": task_id
        }
    
    # 检查任务是否正在运行
    if task.status != "RUNNING":
        return {
            "success": False,
            "message": "任务未在运行中，无法停止",
            "task_id": task_id
        }
    
    # 尝试停止任务线程
    thread = self._running_tasks.get(task_id)
    if thread:
        # 注意：Python的threading模块没有直接停止线程的方法
        # 这里只是从运行任务列表中移除
        del self._running_tasks[task_id]
    
    # 更新任务状态为已停止
    task.status = "STOPPED"
    task.updated_at = datetime.utcnow()
    self.db.commit()
    
    # 记录停止任务的日志
    log_entry = CrawlerTaskLog(
        task_id=task.id,
        source_id=task.source_id,
        status="STOPPED",
        started_at=datetime.utcnow(),
        records_processed=0,
        records_success=0,
        records_failed=0,
        error_message="任务被用户手动停止"
    )
    self.db.add(log_entry)
    self.db.commit()
    
    return {
        "success": True,
        "message": "任务已停止",
        "task_id": task_id
    }
```

### 3.3 数据抓取与存储流程

1. **任务调度**:
   ```python
   # backend/services/task_scheduler_service.py
   def execute_task(self, task_id):
       try:
           # 更新任务状态为RUNNING
           self.update_task_status(task_id, 'RUNNING')
           
           # 获取任务配置
           task = self.get_task(task_id)
           
           # 执行爬虫逻辑
           crawler = self.crawler_factory.create_crawler(task.task_type)
           results = crawler.crawl(task.config)
           
           # 存储抓取结果
           self.data_service.save_results(task_id, results)
           
           # 更新任务状态为SUCCESS
           self.update_task_status(task_id, 'SUCCESS', progress=100)
           
       except Exception as e:
           # 处理异常，更新状态为FAILED
           self.update_task_status(task_id, 'FAILED', error=str(e))
   ```

2. **数据存储**:
   - 抓取的数据通常存储在专门的数据表中，如`lottery_results`或`sports_data`
   - 每个任务类型可能有对应的数据模型
   - 例如彩票数据可能存储在:
     ```python
     class LotteryResult(Base):
         __tablename__ = 'lottery_results'
         
         id = Column(Integer, primary_key=True)
         task_id = Column(Integer, ForeignKey('crawler_tasks.id'))
         draw_number = Column(String(50))
         draw_date = Column(DateTime)
         numbers = Column(String(100))
         created_at = Column(DateTime, default=datetime.utcnow)
     ```

### 3.4 任务执行日志

```python
# backend/services/logging_service.py
def log_task_event(task_id, level, message, details=None):
    # 创建日志记录
    log = TaskLog(
        task_id=task_id,
        level=level,
        message=message,
        details=json.dumps(details) if details else None,
        created_at=datetime.utcnow()
    )
    db.add(log)
    db.commit()
```

## 4. 渲染层分析

### 4.1 任务控制台UI结构

```vue
<!-- frontend/src/views/admin/crawler/TaskConsole.vue -->
<template>
  <!-- 操作栏 -->
  <div class="operation-bar">
    <el-button type="primary" @click="showCreateDialog = true">
      <el-icon><Plus /></el-icon>新建任务
    </el-button>
    <!-- ... -->
  </div>

  <!-- 筛选栏 -->
  <div class="filter-section">
    <el-card>
      <el-form :model="filters" inline>
        <!-- 筛选条件 -->
      </el-form>
    </el-card>
  </div>

  <!-- 任务列表 -->
  <div class="table-section">
    <el-table :data="tasks" v-loading="loading">
      <!-- 任务列定义 -->
      <el-table-column prop="progress" label="进度" width="120">
        <template #default="scope">
          <el-progress :percentage="scope.row.progress || 0" :stroke-width="6" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="scope">
          <el-button 
            type="primary" 
            size="small" 
            @click="handleToggleTask(scope.row)"
            :loading="scope.row.loadingTrigger">
            {{ scope.row.status === 'RUNNING' ? '停止' : '启动' }}
          </el-button>
          <el-button 
            type="primary" 
            size="small" 
            @click="viewLogs(scope.row)"
            :disabled="scope.row.status !== 'RUNNING'">
            日志
          </el-button>
          <el-button 
            type="warning" 
            size="small" 
            @click="editTask(scope.row)"
            :disabled="['RUNNING', 'CANCELLED'].includes(scope.row.status)">
            编辑
          </el-button>
          <el-button 
            type="danger" 
            size="small" 
            @click="deleteTask(scope.row)"
            :disabled="scope.row.status === 'RUNNING'">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>

  <!-- 任务日志对话框 -->
  <el-dialog title="任务日志" v-model="showLogsDialog">
    <div class="log-container">
      <div v-for="(log, index) in taskLogs" :key="index" :class="`log-item log-${log.level}`">
        [{{ formatDate(log.created_at) }}] [{{ log.level.toUpperCase() }}] {{ log.message }}
        <div v-if="log.details" class="log-details">详情: {{ log.details }}</div>
      </div>
    </div>
  </el-dialog>
</template>
```

### 4.2 任务执行状态可视化

1. **状态标签**:
   ```vue
   <el-table-column prop="status" label="状态" width="100">
     <template #default="scope">
       <el-tag :type="getStatusColor(scope.row.status)">
         {{ getStatusName(scope.row.status) }}
       </el-tag>
     </template>
   </el-table-column>
   
   <script>
   const getStatusColor = (status) => {
     switch(status) {
       case 'PENDING': return 'info'
       case 'RUNNING': return 'warning'
       case 'STOPPED': return 'info'
       case 'SUCCESS': return 'success'
       case 'FAILED': return 'danger'
       case 'CANCELLED': return 'info'
       default: return 'primary'
     }
   }
   
   const getStatusName = (status) => {
     const names = {
       'PENDING': '待执行',
       'RUNNING': '运行中',
       'STOPPED': '已停止',
       'SUCCESS': '已完成',
       'FAILED': '失败',
       'CANCELLED': '已取消'
     }
     return names[status] || status
   }
   </script>
   ```

2. **进度条展示**:
   ```vue
   <el-progress :percentage="scope.row.progress || 0" :stroke-width="6" />
   ```

3. **日志详情展示**:
   ```vue
   <div class="log-container">
     <div v-for="(log, index) in taskLogs" :key="index" :class="`log-item log-${log.level}`">
       [{{ formatDate(log.created_at) }}] [{{ log.level.toUpperCase() }}] {{ log.message }}
       <div v-if="log.details" class="log-details">详情: {{ log.details }}</div>
     </div>
   </div>
   ```

## 5. 任务执行详细流程

### 5.1 任务执行日志节点

当您启动一个任务后，日志中通常会包含以下关键节点：

1. **任务触发**:
   ```
   [2026-02-05 13:30:00] [INFO] 任务已触发执行
   ```

2. **初始化阶段**:
   ```
   [2026-02-05 13:30:01] [INFO] 开始执行任务: 26010101
   [2026-02-05 13:30:02] [INFO] 初始化爬虫配置
   [2026-02-05 13:30:03] [INFO] 连接数据源: DS041
   ```

3. **数据抓取阶段**:
   ```
   [2026-02-05 13:30:05] [INFO] 开始抓取数据...
   [2026-02-05 13:30:10] [INFO] 已获取页面列表: 10页
   [2026-02-05 13:30:15] [INFO] 正在解析第1/10页数据
   [2026-02-05 13:30:20] [INFO] 已解析100条记录
   [2026-02-05 13:30:25] [INFO] 进度: 25%
   ```

4. **数据处理阶段**:
   ```
   [2026-02-05 13:30:30] [INFO] 开始清洗和转换数据
   [2026-02-05 13:30:35] [INFO] 数据清洗完成，有效记录: 95条
   [2026-02-05 13:30:40] [INFO] 进度: 75%
   ```

5. **数据存储阶段**:
   ```
   [2026-02-05 13:30:45] [INFO] 开始存储数据到数据库
   [2026-02-05 13:30:50] [INFO] 已存储95条记录到lottery_results表
   [2026-02-05 13:30:55] [INFO] 进度: 100%
   ```

6. **任务完成**:
   ```
   [2026-02-05 13:31:00] [INFO] 任务执行完成
   [2026-02-05 13:31:01] [SUCCESS] 任务成功完成，共处理95条记录
   ```

### 5.2 各层协同工作流程

1. **用户操作层**:
   - 用户点击"新建任务"按钮，填写表单并提交
   - 前端将任务数据通过API发送到后端
   - 用户点击"启动"按钮时，如果任务正在运行则停止任务，否则启动任务

2. **网络通信层**:
   - 前端通过Axios发送HTTP请求到后端API
   - 后端API接收请求，进行验证和处理
   - 后端返回JSON响应，包含操作结果和数据

3. **业务逻辑层**:
   - 任务调度服务将任务添加到执行队列或从运行列表中移除
   - 爬虫服务根据任务类型创建相应的爬虫实例
   - 爬虫执行数据抓取、清洗和存储操作

4. **数据存储层**:
   - 任务状态和元数据存储在[crawler_tasks](file://c:\Users\11581\Downloads\sport-lottery-sweeper\backend\tasks\crawler_tasks.py#L0-L0)表
   - 抓取的实际数据存储在业务数据表(如`lottery_results`)
   - 执行日志存储在`task_logs`表

5. **UI展示层**:
   - 任务列表显示任务状态、进度等信息
   - 启动按钮根据任务状态显示"启动"或"停止"
   - 进度条可视化展示任务执行进度
   - 日志对话框展示详细执行过程和关键节点

## 6. 验证结果

基于您描述的场景，当您:
1. 在http://localhost:3000/admin/data-source/task-console新建任务
2. 点击"启动"按钮

**预期结果**:
- 爬虫应该能够正常抓取数据
- 数据会存储到相应的数据库表中(如lottery_results)
- 任务状态会从"PENDING"变为"RUNNING"，再次点击变为"STOPPED"
- 启动按钮会根据任务状态显示"启动"或"停止"
- 日志中会记录上述提到的关键节点信息

您可以通过以下方式验证:
1. 查看任务状态是否变为"运行中"或"已停止"
2. 启动按钮文本是否根据状态改变（"启动"/"停止"）
3. 点击"日志"按钮查看详细执行过程
4. 直接查询数据库确认数据是否已存储

如果一切正常，您应该能在数据库中看到新抓取的数据，并且任务日志中会显示完整的执行流程和关键节点信息。

希望这个详细的解释对您有所帮助！如果您需要更具体的某个环节的说明，请随时告知。
```