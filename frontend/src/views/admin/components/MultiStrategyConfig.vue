<template>
  <div class="multi-strategy-config">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span class="title">多策略筛选配置</span>
          <el-button class="button" type="primary" :loading="isRunning" @click="toggleScheduledTask">
            {{ isRunning ? '停止任务' : '启动任务' }}
          </el-button>
        </div>
      </template>

      <el-form :model="form" label-width="120px" class="config-form">
        <el-form-item label="选择策略">
          <el-select
            v-model="form.selectedStrategies"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="请选择要执行的策略"
            style="width: 100%"
          >
            <el-option
              v-for="strategy in availableStrategies"
              :key="strategy.value"
              :label="strategy.label"
              :value="strategy.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="消息格式">
          <el-radio-group v-model="form.messageFormat">
            <el-radio value="table">表格</el-radio>
            <el-radio value="markdown">Markdown</el-radio>
            <el-radio value="text">纯文本</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="执行间隔(分钟)">
          <el-input-number
            v-model="form.intervalMinutes"
            :min="1"
            :max="60"
            controls-position="right"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="executeNow" :loading="executing">
            立即执行
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="execution-results" v-if="executionResult">
        <h4>最近执行结果:</h4>
        <pre class="result-content">{{ executionResult }}</pre>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAvailableStrategies, executeMultiStrategy, toggleTask } from '@/api/modules/multiStrategy'

// 表单数据
const form = reactive({
  selectedStrategies: [],
  messageFormat: 'table',
  intervalMinutes: 5
})

// 状态变量
const isRunning = ref(false)
const executing = ref(false)
const availableStrategies = ref([])
const executionResult = ref(null)

// 获取可用策略列表
const fetchAvailableStrategies = async () => {
  try {
    const response = await getAvailableStrategies()
    if (response.success) {
      availableStrategies.value = response.data.map(strategy => ({
        value: strategy,
        label: getStrategyLabel(strategy)
      }))
    }
  } catch (error) {
    console.error('获取策略列表失败:', error)
    ElMessage.error('获取策略列表失败')
  }
}

// 获取策略标签
const getStrategyLabel = (strategy) => {
  const labels = {
    'high_probability_winning': '高概率胜平负',
    'balanced_odds': '均衡赔率',
    'recent_form': '近期表现'
  }
  return labels[strategy] || strategy
}

// 立即执行
const executeNow = async () => {
  if (!form.selectedStrategies.length) {
    ElMessage.warning('请至少选择一个策略')
    return
  }

  executing.value = true
  try {
    const response = await executeMultiStrategy({
      strategy_ids: form.selectedStrategies,
      message_format: form.messageFormat
    })
    
    if (response.success) {
      ElMessage.success('策略执行成功')
      executionResult.value = response.formatted_message || JSON.stringify(response.results, null, 2)
    } else {
      ElMessage.error(response.message || '执行失败')
    }
  } catch (error) {
    console.error('执行策略失败:', error)
    ElMessage.error('执行失败: ' + error.message)
  } finally {
    executing.value = false
  }
}

// 切换定时任务
const toggleScheduledTask = async () => {
  try {
    const response = await toggleTask({ enabled: !isRunning.value })
    if (response.success) {
      isRunning.value = !isRunning.value
      ElMessage.success(isRunning.value ? '任务已启动' : '任务已停止')
    } else {
      ElMessage.error(response.message || '操作失败')
    }
  } catch (error) {
    console.error('切换任务状态失败:', error)
    ElMessage.error('操作失败: ' + error.message)
  }
}

// 重置表单
const resetForm = () => {
  form.selectedStrategies = []
  form.messageFormat = 'table'
  form.intervalMinutes = 5
  executionResult.value = null
}

// 初始化
onMounted(() => {
  fetchAvailableStrategies()
})
</script>

<style scoped>
.config-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.config-form {
  padding-top: 10px;
}

.execution-results {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.result-content {
  white-space: pre-wrap;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
}
</style>