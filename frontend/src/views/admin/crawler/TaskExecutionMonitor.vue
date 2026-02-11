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
                  <div>
                    <el-button @click="refreshList">刷新</el-button>
                    <el-button type="primary" @click="$router.push('/admin/data-source/task-console')">任务控制台</el-button>
                  </div>
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
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>执行统计</span>
                </div>
              </template>
              <StatisticsPanel :stats="statistics" />
              
              <!-- 任务状态分布 -->
              <el-card style="margin-top: 20px;">
                <template #header>
                  <div class="card-header">
                    <span>任务状态分布</span>
                  </div>
                </template>
                <el-table :data="statusDistribution" style="width: 100%" :show-header="false">
                  <el-table-column prop="status" width="100" />
                  <el-table-column prop="count" />
                </el-table>
              </el-card>
            </el-card>
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
import { ref, onMounted, onUnmounted, computed } from 'vue'
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
const dashboardMetrics = ref({
  runningTasks: 0,
  todayTotal: 0,
  todaySuccess: 0,
  successRate: 0,
  avgDuration: 0,
  hourlyErrorRate: 0
})
const statistics = ref({
  successRate: 0,
  avgExecutionTime: 0,
  failureRate: 0
})

// 计算任务状态分布
const statusDistribution = computed(() => {
  const distribution = {}
  executions.value.forEach(exec => {
    distribution[exec.status] = (distribution[exec.status] || 0) + 1
  })
  
  return Object.entries(distribution).map(([status, count]) => ({
    status,
    count
  }))
})

// 初始化数据
onMounted(async () => {
  await refreshList()
  // 连接WebSocket
  store.connectWebSocket()
  websocketConnected.value = true
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
      status: ['RUNNING', 'PENDING', 'FAILED', 'SUCCESS']
    })
    // 更新统计信息
    updateStatistics()
  } catch (error) {
    console.error('获取任务执行列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 更新统计信息
const updateStatistics = () => {
  const total = executions.value.length
  const successful = executions.value.filter(task => task.status === 'SUCCESS').length
  const failed = executions.value.filter(task => task.status === 'FAILED').length
  const running = executions.value.filter(task => task.status === 'RUNNING').length
  
  statistics.value = {
    successRate: total > 0 ? (successful / total * 100).toFixed(2) : 0,
    failureRate: total > 0 ? (failed / total * 100).toFixed(2) : 0,
    runningTasks: running
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

<style scoped>
.task-execution-monitor {
  padding: 20px;
  height: calc(100vh - 84px);
  overflow: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-header {
  padding: 0;
  margin-bottom: 20px;
}

.el-main {
  padding: 0;
}
</style>