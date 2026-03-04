

爬虫管理模块任务控制台页面，并按照以下布局设计生成页面：

1、在系统架构参考其布局和代码
2、页面布局在左边栏爬虫管理新子模块页面，对应在整个页面的在右边页面区域；
3、功能和布局设计以代码里面的为主；
4、在不和项目系统发生冲突的基础上计量去设计。
5.扫描系统中有相同的数据库表可以参考这个完善；
6.这个页面包含以下部分：任务设计、任务任务管理界面

以下是包含部分的页面代码布局参考：
1.任务设计
1.1任务模型设计
# models/task.py
class TaskType(Enum):
    SCHEDULE_CRAWL = "schedule_crawl"      # 赛程采集
    ODDS_CRAWL = "odds_crawl"              # 赔率采集
    RESULT_CRAWL = "result_crawl"          # 结果采集
    STATS_CRAWL = "stats_crawl"            # 统计采集
    DATA_CLEAN = "data_clean"              # 数据清洗
    DATA_MERGE = "data_merge"              # 数据合并

class TaskStatus(Enum):
    PENDING = "pending"        # 等待中
    RUNNING = "running"        # 运行中
    SUCCESS = "success"        # 成功
    FAILED = "failed"          # 失败
    PAUSED = "paused"          # 暂停
    CANCELLED = "cancelled"    # 取消

class CrawlTask(Base):
    __tablename__ = "crawl_tasks"
    
    id = Column(UUID, primary_key=True)
    name = Column(String(200), nullable=False)          # 任务名称
    task_type = Column(Enum(TaskType), nullable=False)  # 任务类型
    
    # 关联配置
    source_id = Column(UUID, ForeignKey('data_sources.id'))
    parser_config_id = Column(UUID, ForeignKey('parser_configs.id'))
    
    # 调度配置
    schedule_type = Column(String(20), default="cron")  # cron, interval, manual
    schedule_config = Column(JSON, default=dict)        # 调度配置
    next_run_time = Column(DateTime)                    # 下次执行时间
    
    # 采集配置（足球专项）
    crawl_config = Column(JSON, default={
        "leagues": [],           # 指定联赛
        "date_range": 7,         # 日期范围（天）
        "odds_type": "all",      # 赔率类型
        "include_stats": True,   # 包含统计
        "retry_policy": {        # 重试策略
            "max_retries": 3,
            "retry_delay": 60
        }
    })
    
    # 执行状态
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    current_progress = Column(Integer, default=0)      # 当前进度
    total_items = Column(Integer, default=0)           # 总项目数
    last_run_time = Column(DateTime)                   # 最后执行时间
    last_success_time = Column(DateTime)               # 最后成功时间
    
    # 执行结果
    execution_stats = Column(JSON, default={
        "total_runs": 0,
        "success_runs": 0,
        "total_items_crawled": 0,
        "avg_duration": 0
    })
    
    # 错误信息
    last_error = Column(Text)
    error_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



1.2任务调度引擎

# services/task_scheduler.py
class TaskScheduler:
    """任务调度引擎"""
    
    def __init__(self):
        self.celery_app = Celery('football_crawler')
        self.celery_app.config_from_object('celery_config')
        
    async def create_task(self, task_config: TaskCreate):
        """创建新任务"""
        task = CrawlTask(**task_config.dict())
        db.add(task)
        db.commit()
        
        # 根据调度类型创建定时任务
        if task.schedule_type == "cron":
            self._create_cron_task(task)
        elif task.schedule_type == "interval":
            self._create_interval_task(task)
        
        # 发送通知
        await notification_service.send_task_created(task)
        
        return task
    
    def _create_cron_task(self, task: CrawlTask):
        """创建Cron定时任务"""
        cron_config = task.schedule_config
        
        @self.celery_app.task
        def execute_crawl_task(task_id):
            return self._execute_task(task_id)
        
        # 使用Celery Beat调度
        schedule_entry = {
            'task': 'execute_crawl_task',
            'schedule': crontab(**cron_config),
            'args': (str(task.id),),
            'options': {'queue': 'crawl_tasks'}
        }
        
        # 添加到调度器
        self.celery_app.conf.beat_schedule.update({
            f'task_{task.id}': schedule_entry
        })
    
    async def _execute_task(self, task_id: UUID):
        """执行采集任务"""
        task = db.query(CrawlTask).filter(CrawlTask.id == task_id).first()
        if not task:
            return
        
        # 更新任务状态
        task.status = TaskStatus.RUNNING
        task.last_run_time = datetime.utcnow()
        db.commit()
        
        try:
            # 根据任务类型执行不同的采集逻辑
            if task.task_type == TaskType.SCHEDULE_CRAWL:
                result = await self._crawl_schedule(task)
            elif task.task_type == TaskType.ODDS_CRAWL:
                result = await self._crawl_odds(task)
            elif task.task_type == TaskType.RESULT_CRAWL:
                result = await self._crawl_results(task)
            
            # 更新任务结果
            task.status = TaskStatus.SUCCESS
            task.last_success_time = datetime.utcnow()
            task.execution_stats['success_runs'] += 1
            task.execution_stats['total_items_crawled'] += result.total_items
            
            # 记录执行统计
            self._record_execution_metrics(task, result)
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.last_error = str(e)
            task.error_count += 1
            
            # 根据重试策略决定是否重试
            if task.error_count <= task.crawl_config.get('retry_policy', {}).get('max_retries', 3):
                await self._schedule_retry(task)
            else:
                await notification_service.send_task_failed(task, str(e))
        
        finally:
            task.execution_stats['total_runs'] += 1
            db.commit()
    
    async def _crawl_schedule(self, task: CrawlTask) -> CrawlResult:
        """执行赛程采集"""
        source = task.source
        config = task.crawl_config
        
        # 构建采集参数
        params = {
            'leagues': config.get('leagues', []),
            'days_ahead': config.get('date_range', 7),
            'include_odds': config.get('include_odds', False)
        }
        
        # 使用相应的采集器
        if source.type == SourceType.WEB:
            crawler = WebScheduleCrawler(source, task.parser_config)
        elif source.type == SourceType.API:
            crawler = APIScheduleCrawler(source, task.parser_config)
        
        # 执行采集
        result = await crawler.crawl(**params)
        
        # 数据验证和存储
        validator = ScheduleValidator(result.data)
        if validator.validate():
            storage_service.save_schedules(result.data)
        
        return result
2.前端任务管理界面

<!-- components/TaskConsole.vue -->
<template>
  <div class="task-console">
    <!-- 控制面板 -->
    <div class="control-panel">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="运行中任务" :value="runningCount" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="今日完成" :value="todayCompleted" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="成功率" :value="successRate" suffix="%" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="待处理" :value="pendingCount" />
        </el-col>
      </el-row>
    </div>
    
    <!-- 任务操作区 -->
    <div class="task-operations">
      <el-button type="primary" @click="handleCreateTask">
        <el-icon><Plus /></el-icon>新建任务
      </el-button>
      <el-button @click="handleStartSelected" :disabled="selectedTasks.length === 0">
        <el-icon><VideoPlay /></el-icon>开始
      </el-button>
      <el-button @click="handlePauseSelected" :disabled="selectedTasks.length === 0">
        <el-icon><VideoPause /></el-icon>暂停
      </el-button>
      <el-button @click="handleStopSelected" :disabled="selectedTasks.length === 0">
        <el-icon><CloseBold /></el-icon>停止
      </el-button>
      <el-button type="danger" @click="handleDeleteSelected" :disabled="selectedTasks.length === 0">
        <el-icon><Delete /></el-icon>删除
      </el-button>
    </div>
    
    <!-- 任务列表 -->
    <el-table 
      :data="tasks" 
      v-loading="loading"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="50" />
      <el-table-column prop="name" label="任务名称" width="250">
        <template #default="{row}">
          <div class="task-name">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ formatStatus(row.status) }}
            </el-tag>
            <span>{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="task_type" label="类型" width="120">
        <template #default="{row}">
          <el-tag :type="getTaskTypeColor(row.task_type)">
            {{ formatTaskType(row.task_type) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column label="进度" width="200">
        <template #default="{row}">
          <div v-if="row.status === 'running'">
            <el-progress 
              :percentage="row.current_progress" 
              :text-inside="true"
              :stroke-width="20"
            />
            <div class="progress-detail">
              {{ row.current_progress }}/{{ row.total_items }}
            </div>
          </div>
          <div v-else>--</div>
        </template>
      </el-table-column>
      
      <el-table-column prop="next_run_time" label="下次执行" width="180">
        <template #default="{row}">
          {{ formatTime(row.next_run_time) }}
        </template>
      </el-table-column>
      
      <el-table-column prop="last_run_time" label="最后执行" width="180">
        <template #default="{row}">
          {{ formatTime(row.last_run_time) }}
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{row}">
          <el-button-group>
            <el-button 
              size="small" 
              @click="handleStartTask(row)"
              :disabled="row.status === 'running' || row.status === 'success'"
            >
              开始
            </el-button>
            <el-button 
              size="small" 
              @click="handlePauseTask(row)"
              :disabled="row.status !== 'running'"
            >
              暂停
            </el-button>
            <el-button 
              size="small" 
              @click="handleStopTask(row)"
              :disabled="row.status !== 'running'"
            >
              停止
            </el-button>
            <el-button size="small" @click="handleViewLogs(row)">
              日志
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <el-pagination v-model:current-page="currentPage" ... />
    
    <!-- 实时日志面板 -->
    <el-drawer v-model="logDrawerVisible" title="任务执行日志" size="50%">
      <TaskLogViewer :task-id="currentTaskId" />
    </el-drawer>
    
    <!-- 任务创建对话框 -->
    <TaskCreateDialog 
      v-model="createDialogVisible"
      @success="handleTaskCreated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useWebSocket } from '@vueuse/core'
import TaskLogViewer from './TaskLogViewer.vue'
import TaskCreateDialog from './TaskCreateDialog.vue'

// WebSocket实时更新
const { data: wsData } = useWebSocket('ws://localhost:8000/ws/tasks')

// 监听任务状态更新
watch(wsData, (newData) => {
  if (newData.type === 'task_update') {
    const index = tasks.value.findIndex(t => t.id === newData.task_id)
    if (index !== -1) {
      tasks.value[index] = { ...tasks.value[index], ...newData.data }
    }
  }
})

// 任务控制函数
const handleStartTask = async (task) => {
  try {
    await api.post(`/tasks/${task.id}/start`)
    ElMessage.success('任务已开始')
  } catch (error) {
    ElMessage.error('启动任务失败')
  }
}

const handleViewLogs = (task) => {
  currentTaskId.value = task.id
  logDrawerVisible.value = true
}
</script>
    


    