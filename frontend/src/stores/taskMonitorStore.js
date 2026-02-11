// AI_WORKING: coder1 @2026-02-04 - 创建任务监控Pinia store
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
    try {
      const response = await taskMonitorApi.getExecutions(params)
      console.log('API Response:', response) // 调试信息
      
      // 检查响应是否符合预期格式 { code: 200, data: {...} }
      if (response && typeof response === 'object') {
        let parsedResponse = response
        
        // 如果响应已经是 { code: 200, data: {...} } 格式，则直接使用
        if (response.code === 200 && response.data) {
          parsedResponse = response
        } else if (response.success === true && response.data) {
          // 如果响应是 { success: true, data: {...} } 格式，转换为预期格式
          parsedResponse = {
            code: 200,
            data: response.data,
            message: response.message || '获取成功'
          }
        } else if (response.items !== undefined && response.total !== undefined) {
          // 如果响应是直接的数据格式，包装为预期格式
          parsedResponse = {
            code: 200,
            data: response,
            message: '获取成功'
          }
        } else {
          throw new Error('API响应格式不符合预期')
        }
        
        executions.value = parsedResponse.data.items || []
        totalCount.value = parsedResponse.data.total || 0
        currentPage.value = parsedResponse.data.page || 1
      } else {
        console.error('获取任务执行列表失败:', response)
        executions.value = []
        totalCount.value = 0
      }
      return executions.value
    } catch (error) {
      console.error('获取任务执行列表时发生错误:', error)
      console.error('错误详情:', error.response || error.message)
      executions.value = []
      totalCount.value = 0
      throw error
    }
  }
  
  const cancelExecution = async (executionId) => {
    try {
      await taskMonitorApi.cancelExecution(executionId)
      // 更新本地状态
      const index = executions.value.findIndex(exec => exec.id === executionId)
      if (index !== -1) {
        executions.value[index].status = 'CANCELLED'
      }
      return true
    } catch (error) {
      console.error('取消任务执行时发生错误:', error)
      throw error
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
  
  const updateTaskProgress = (taskId, progress) => {
    const index = executions.value.findIndex(exec => exec.id === taskId)
    if (index !== -1) {
      executions.value[index].progress = progress
    }
  }
  
  const updateTaskStatus = (taskId, status) => {
    const index = executions.value.findIndex(exec => exec.id === taskId)
    if (index !== -1) {
      executions.value[index].status = status
    }
  }
  
  const updateMetrics = (metrics) => {
    // 这里可以更新实时指标状态
    console.log('收到实时指标更新:', metrics)
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

// AI_DONE: coder1 @2026-02-04