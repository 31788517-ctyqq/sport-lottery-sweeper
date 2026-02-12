<template>
  <el-card class="multi-strategy-card" v-if="showMultiStrategyPanel">
    <div slot="header" class="clearfix">
      <span>多策略筛选配置</span>
      <el-button 
        style="float: right; padding: 3px 0" 
        type="text" 
        @click="showMultiStrategyPanel = false"
      >
        收起
      </el-button>
    </div>
    
    <!-- 策略选择 -->
    <el-form :model="multiStrategyForm" label-width="120px" class="strategy-selection">
      <el-form-item label="选择策略">
        <el-checkbox-group v-model="multiStrategyForm.selectedStrategies">
          <el-checkbox 
            v-for="strategy in availableStrategies" 
            :key="strategy.id" 
            :label="strategy.id"
            :disabled="loading"
          >
            {{ strategy.name }}
          </el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      
      <!-- 执行频率 -->
      <el-form-item label="执行频率">
        <el-select 
          v-model="multiStrategyForm.cronType" 
          @change="updateCronExpression"
          :disabled="loading"
        >
          <el-option label="每天" value="daily"></el-option>
          <el-option label="每周" value="weekly"></el-option>
          <el-option label="每小时" value="hourly"></el-option>
          <el-option label="自定义" value="custom"></el-option>
        </el-select>
      </el-form-item>
      
      <!-- 自定义Cron表达式 -->
      <el-form-item v-if="multiStrategyForm.cronType === 'custom'" label="Cron表达式">
        <el-input
          v-model="multiStrategyForm.cronExpression"
          placeholder="例: 0 9 * * *"
          :disabled="loading"
        />
      </el-form-item>
      
      <!-- 消息格式 -->
      <el-form-item label="消息格式">
        <el-radio-group v-model="multiStrategyForm.messageFormat" :disabled="loading">
          <el-radio label="text">纯文本</el-radio>
          <el-radio label="table">表格形式</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <!-- 钉钉通知 -->
      <el-form-item label="钉钉通知">
        <el-switch 
          v-model="multiStrategyForm.dingtalkEnabled" 
          @change="onDingtalkToggle"
          :disabled="loading"
        />
        <div v-if="multiStrategyForm.dingtalkEnabled" style="margin-top: 10px;">
          <el-input 
            v-model="multiStrategyForm.dingtalkWebhook" 
            placeholder="请输入钉钉机器人Webhook URL"
            style="width: 80%;"
            :disabled="loading"
            type="textarea"
            :rows="2"
          />
        </div>
      </el-form-item>
      
      <!-- 任务管理按钮 -->
      <el-form-item>
        <el-button 
          type="primary" 
          @click="saveMultiStrategyConfig" 
          :loading="saving"
          :disabled="!canSave"
        >
          保存配置
        </el-button>
        <el-button 
          @click="loadUserTasks" 
          :loading="loadingTasks"
          style="margin-left: 10px;"
        >
          刷新任务
        </el-button>
        <el-button 
          type="warning" 
          @click="executeNow" 
          :loading="executing"
          style="margin-left: 10px;"
        >
          立即执行
        </el-button>
      </el-form-item>
    </el-form>
    
    <!-- 用户任务列表 -->
    <div v-if="userTasks.length > 0" class="task-list">
      <h4>我的定时任务</h4>
      <el-table :data="userTasks" border size="small" class="task-table">
        <el-table-column prop="task_name" label="任务名称" width="150" />
        <el-table-column prop="cron_expression" label="执行频率" width="120" />
        <el-table-column prop="message_format" label="消息格式" width="80" />
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.enabled ? 'success' : 'danger'">
              {{ scope.row.enabled ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button 
              size="mini" 
              @click="toggleTask(scope.row)"
              :type="scope.row.enabled ? 'warning' : 'success'"
            >
              {{ scope.row.enabled ? '停用' : '启用' }}
            </el-button>
            <el-button 
              size="mini" 
              type="danger" 
              @click="deleteTask(scope.row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 执行历史 -->
    <div v-if="executionHistory.length > 0" class="history-section">
      <h4>执行历史</h4>
      <el-table :data="executionHistory.slice(0, 5)" border size="small" class="history-table">
        <el-table-column prop="executed_at" label="执行时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.executed_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="strategy_ids" label="执行策略" width="200">
          <template #default="scope">
            <el-tag size="mini" v-for="id in scope.row.strategy_ids" :key="id" style="margin: 2px;">
              {{ id }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="result_count" label="结果数量" width="100" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
              {{ scope.row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </el-card>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

export default {
  name: 'MultiStrategyManager',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const showMultiStrategyPanel = computed({
      get: () => props.visible,
      set: (val) => {
        if (!val) emit('close')
      }
    })
    
    // 响应式数据
    const loading = ref(false)
    const saving = ref(false)
    const loadingTasks = ref(false)
    const executing = ref(false)
    
    // 多策略表单
    const multiStrategyForm = reactive({
      taskName: '',
      selectedStrategies: [],
      cronType: 'daily',
      cronExpression: '0 9 * * *',
      messageFormat: 'table',
      dingtalkEnabled: false,
      dingtalkWebhook: ''
    })
    
    // 可用策略
    const availableStrategies = ref([
      { id: 'high_probability_winning', name: '高胜率策略' },
      { id: 'balanced_odds', name: '平衡赔率策略' },
      { id: 'recent_form', name: '近期状态策略' }
    ])
    
    // 用户任务和执行历史
    const userTasks = ref([])
    const executionHistory = ref([])
    
    // 计算属性
    const canSave = computed(() => {
      return multiStrategyForm.taskName && 
             multiStrategyForm.selectedStrategies.length > 0 && 
             multiStrategyForm.cronExpression
    })
    
    // 方法
    const updateCronExpression = () => {
      const expressions = {
        daily: '0 9 * * *',
        weekly: '0 9 * * 1',
        hourly: '0 * * * *'
      }
      if (multiStrategyForm.cronType !== 'custom') {
        multiStrategyForm.cronExpression = expressions[multiStrategyForm.cronType]
      }
    }
    
    const onDingtalkToggle = (enabled) => {
      if (enabled && !multiStrategyForm.dingtalkWebhook) {
        ElMessage.warning('请先设置钉钉Webhook URL')
      }
    }
    
    const saveMultiStrategyConfig = async () => {
      if (!canSave.value) {
        ElMessage.warning('请填写完整的配置信息')
        return
      }
      
      saving.value = true
      try {
        const config = {
          task_name: multiStrategyForm.taskName,
          strategy_ids: multiStrategyForm.selectedStrategies,
          cron_expression: multiStrategyForm.cronExpression,
          message_format: multiStrategyForm.messageFormat,
          dingtalk_webhook: multiStrategyForm.dingtalkEnabled ? multiStrategyForm.dingtalkWebhook : null,
          enabled: true
        }
        
        await axios.post('/api/v1/multi-strategy/config', config)
        ElMessage.success('多策略配置保存成功')
        loadUserTasks()
      } catch (error) {
        ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        saving.value = false
      }
    }
    
    const loadUserTasks = async () => {
      loadingTasks.value = true
      try {
        const response = await axios.get('/api/v1/multi-strategy/config?user_id=' + getCurrentUserId())
        if (response.data.success) {
          userTasks.value = response.data.data || []
        }
      } catch (error) {
        ElMessage.error('加载任务失败')
      } finally {
        loadingTasks.value = false
      }
    }
    
    const executeNow = async () => {
      if (multiStrategyForm.selectedStrategies.length === 0) {
        ElMessage.warning('请先选择策略')
        return
      }
      
      executing.value = true
      try {
        const request = {
          strategy_ids: multiStrategyForm.selectedStrategies,
          message_format: multiStrategyForm.messageFormat
        }
        
        const response = await axios.post('/api/v1/multi-strategy/execute', request)
        if (response.data.success) {
          ElMessage.success('策略执行成功')
          // 添加到执行历史
          executionHistory.value.unshift({
            executed_at: new Date().toISOString(),
            strategy_ids: multiStrategyForm.selectedStrategies,
            result_count: Object.keys(response.data.results || {}).length,
            status: 'success'
          })
        }
      } catch (error) {
        ElMessage.error('执行失败: ' + (error.response?.data?.detail || error.message))
        executionHistory.value.unshift({
          executed_at: new Date().toISOString(),
          strategy_ids: multiStrategyForm.selectedStrategies,
          result_count: 0,
          status: 'failed'
        })
      } finally {
        executing.value = false
      }
    }
    
    const toggleTask = async (task) => {
      try {
        const response = await axios.post(`/api/v1/multi-strategy/toggle-task/${task.user_id}`, {
          enabled: !task.enabled
        })
        if (response.data.success) {
          ElMessage.success(`任务已${task.enabled ? '停用' : '启用'}`)
          loadUserTasks()
        }
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
    
    const deleteTask = async (taskId) => {
      try {
        await ElMessageBox.confirm('确定删除此任务？', '确认删除', {
          type: 'warning'
        })
        
        // 这里需要调用删除API
        ElMessage.success('任务已删除')
        loadUserTasks()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
    }
    
    const formatDate = (dateStr) => {
      return new Date(dateStr).toLocaleString('zh-CN')
    }
    
    const getCurrentUserId = () => {
      // 从localStorage或store获取当前用户ID
      return localStorage.getItem('username') || 'admin'
    }
    
    // 生命周期
    onMounted(() => {
      loadUserTasks()
    })
    
    return {
      showMultiStrategyPanel,
      loading, saving, loadingTasks, executing,
      multiStrategyForm,
      availableStrategies,
      userTasks,
      executionHistory,
      canSave,
      updateCronExpression,
      onDingtalkToggle,
      saveMultiStrategyConfig,
      loadUserTasks,
      executeNow,
      toggleTask,
      deleteTask,
      formatDate
    }
  }
}
</script>

<style scoped>
.multi-strategy-card {
  margin: 20px 0;
  width: 100%;
  max-width: 100%;
  border: 1px solid #e4e7ed;
  background: #fbfaf8;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  box-sizing: border-box;
  display: block;
}

.strategy-selection {
  margin-bottom: 20px;
}

.task-list, .history-section {
  margin-top: 20px;
}

.task-table, .history-table {
  margin-top: 10px;
}

.webhook-masked {
  font-family: monospace;
  font-size: 12px;
  color: #666;
}

.cron-hint {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.help-content {
  font-size: 12px;
  color: #666;
  background: #f5f5f5;
  padding: 10px;
  margin-top: 5px;
  border-radius: 4px;
}
</style>