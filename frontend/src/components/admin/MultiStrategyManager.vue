<template>
  <el-card v-if="visible" class="multi-strategy-card">
    <template #header>
      <div class="header-row">
        <span class="title">多策略筛选配置</span>
        <el-button type="link" @click="$emit('close')">收起</el-button>
      </div>
    </template>

    <el-form :model="multiStrategyForm" label-width="120px" class="strategy-selection">
      <el-form-item label="任务名称">
        <el-input
          v-model="multiStrategyForm.taskName"
          placeholder="请输入任务名称"
          :disabled="loading || saving"
        />
      </el-form-item>

      <el-form-item label="选择策略">
        <div class="strategy-checkbox-panel">
          <el-checkbox-group v-model="multiStrategyForm.selectedStrategies" :disabled="loading">
            <el-checkbox
              v-for="strategy in availableStrategies"
              :key="strategy.id"
              :label="strategy.id"
            >
              {{ strategy.name }}
            </el-checkbox>
          </el-checkbox-group>
        </div>
      </el-form-item>

      <el-form-item label="执行频率">
        <el-select
          v-model="multiStrategyForm.cronType"
          :disabled="loading"
          @change="updateCronExpression"
        >
          <el-option label="每天" value="daily" />
          <el-option label="每周" value="weekly" />
          <el-option label="每小时" value="hourly" />
          <el-option label="自定义" value="custom" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="multiStrategyForm.cronType === 'custom'" label="Cron表达式">
        <el-input
          v-model="multiStrategyForm.cronExpression"
          placeholder="例如: 0 9 * * *"
          :disabled="loading"
        />
      </el-form-item>

      <el-form-item label="消息格式">
        <el-radio-group v-model="multiStrategyForm.messageFormat" :disabled="loading">
          <el-radio value="text">纯文本</el-radio>
          <el-radio value="table">表格</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="钉钉通知">
        <el-switch
          v-model="multiStrategyForm.dingtalkEnabled"
          :disabled="loading"
          @change="onDingtalkToggle"
        />
        <div v-if="multiStrategyForm.dingtalkEnabled" class="webhook-row">
          <el-input
            v-model="multiStrategyForm.dingtalkWebhook"
            type="textarea"
            :rows="2"
            placeholder="请输入钉钉机器人 Webhook URL"
            :disabled="loading"
          />
        </div>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :loading="saving" :disabled="!canSave" @click="saveMultiStrategyConfig">
          保存配置
        </el-button>
        <el-button :loading="loadingTasks" @click="loadUserTasks">刷新任务</el-button>
        <el-button type="warning" :loading="executing" @click="executeNow">立即执行</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const props = defineProps({
  visible: { type: Boolean, default: false },
  presetStrategies: { type: Array, default: () => [] },
  strategyOptionsSource: { type: Array, default: () => [] }
})

defineEmits(['close'])

const loading = ref(false)
const saving = ref(false)
const loadingTasks = ref(false)
const executing = ref(false)

const multiStrategyForm = reactive({
  taskName: '',
  selectedStrategies: [],
  cronType: 'daily',
  cronExpression: '0 9 * * *',
  messageFormat: 'table',
  dingtalkEnabled: false,
  dingtalkWebhook: ''
})

const availableStrategies = ref([])

const canSave = computed(() => {
  return (
    String(multiStrategyForm.taskName || '').trim().length > 0 &&
    multiStrategyForm.selectedStrategies.length > 0 &&
    String(multiStrategyForm.cronExpression || '').trim().length > 0
  )
})

const unwrapApiResponse = (response) => {
  if (Array.isArray(response)) return { success: true, data: response }
  if (!response || typeof response !== 'object') return { success: false, data: null, message: '响应格式不正确' }
  if (Object.prototype.hasOwnProperty.call(response, 'success')) return response
  if (Object.prototype.hasOwnProperty.call(response, 'data')) return { success: true, data: response.data, message: response.message }
  return { success: true, data: response }
}

const normalizeStrategyName = (item) => {
  if (typeof item === 'string') return item.trim()
  if (item && typeof item === 'object' && item.name) return String(item.name).trim()
  return ''
}

const mergeStrategyOptions = (apiNames = []) => {
  const fromProps = (props.strategyOptionsSource || []).map((name) => String(name || '').trim()).filter(Boolean)
  const fromSelected = multiStrategyForm.selectedStrategies.map((name) => String(name || '').trim()).filter(Boolean)
  const uniqueNames = [...new Set([...apiNames, ...fromProps, ...fromSelected])]
  availableStrategies.value = uniqueNames.map((name) => ({ id: name, name }))
}

const syncSelectedStrategiesToOptions = () => {
  const existed = new Set(availableStrategies.value.map((item) => item.id))
  multiStrategyForm.selectedStrategies
    .map((name) => String(name || '').trim())
    .filter(Boolean)
    .forEach((name) => {
      if (!existed.has(name)) {
        availableStrategies.value.push({ id: name, name })
        existed.add(name)
      }
    })
}

const fetchAvailableStrategies = async () => {
  loading.value = true
  try {
    const raw = await request.get('/api/v1/beidan-filter/strategies')
    const response = unwrapApiResponse(raw)
    const list = Array.isArray(response.data) ? response.data : []
    const names = list.map(normalizeStrategyName).filter(Boolean)
    mergeStrategyOptions(names)
    syncSelectedStrategiesToOptions()
  } catch {
    mergeStrategyOptions([])
    syncSelectedStrategiesToOptions()
  } finally {
    loading.value = false
  }
}

const updateCronExpression = () => {
  const expressions = { daily: '0 9 * * *', weekly: '0 9 * * 1', hourly: '0 * * * *' }
  if (multiStrategyForm.cronType !== 'custom') multiStrategyForm.cronExpression = expressions[multiStrategyForm.cronType]
}

const onDingtalkToggle = (enabled) => {
  if (enabled && !multiStrategyForm.dingtalkWebhook) ElMessage.warning('请先设置钉钉 Webhook URL')
}

const getCurrentUserId = () => {
  const username = localStorage.getItem('username')
  if (username) return username
  const token = localStorage.getItem('access_token') || localStorage.getItem('token')
  if (!token) return 'admin'
  try {
    const payload = token.split('.')[1]
    const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    return decoded.username || decoded.sub || 'admin'
  } catch {
    return 'admin'
  }
}

const saveMultiStrategyConfig = async () => {
  if (!canSave.value) {
    ElMessage.warning('请填写完整配置')
    return
  }
  saving.value = true
  try {
    const raw = await request.post('/api/multi-strategy/config', {
      task_name: multiStrategyForm.taskName.trim(),
      strategy_ids: multiStrategyForm.selectedStrategies,
      cron_expression: multiStrategyForm.cronExpression.trim(),
      message_format: multiStrategyForm.messageFormat,
      user_id: getCurrentUserId(),
      dingtalk_webhook: multiStrategyForm.dingtalkEnabled ? multiStrategyForm.dingtalkWebhook : null,
      enabled: true
    })
    const response = unwrapApiResponse(raw)
    if (response.success) {
      ElMessage.success('多策略配置保存成功')
      return
    }
    ElMessage.error(`保存失败: ${response.message || '未知错误'}`)
  } catch (error) {
    ElMessage.error(`保存失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    saving.value = false
  }
}

const loadUserTasks = async () => {
  loadingTasks.value = true
  try {
    await request.get(`/api/multi-strategy/config?user_id=${getCurrentUserId()}`)
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
    const raw = await request.post('/api/multi-strategy/execute', {
      strategy_ids: multiStrategyForm.selectedStrategies,
      message_format: multiStrategyForm.messageFormat
    })
    const response = unwrapApiResponse(raw)
    if (response.success) {
      ElMessage.success('策略执行成功')
      return
    }
    ElMessage.error(`执行失败: ${response.message || '未知错误'}`)
  } catch (error) {
    ElMessage.error(`执行失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    executing.value = false
  }
}

onMounted(() => {
  if (props.visible) {
    const preset = (props.presetStrategies || []).map((name) => String(name || '').trim()).filter(Boolean)
    if (preset.length > 0) multiStrategyForm.selectedStrategies = [...new Set(preset)]
    fetchAvailableStrategies()
    loadUserTasks()
  }
})

watch(
  () => props.visible,
  (nextVisible) => {
    if (nextVisible) {
      const preset = (props.presetStrategies || []).map((name) => String(name || '').trim()).filter(Boolean)
      if (preset.length > 0) multiStrategyForm.selectedStrategies = [...new Set(preset)]
      fetchAvailableStrategies()
      loadUserTasks()
    }
  }
)

watch(
  () => props.strategyOptionsSource,
  () => {
    mergeStrategyOptions([])
    syncSelectedStrategiesToOptions()
  },
  { deep: true }
)

watch(
  () => props.presetStrategies,
  (next) => {
    const preset = (next || []).map((name) => String(name || '').trim()).filter(Boolean)
    multiStrategyForm.selectedStrategies = [...new Set(preset)]
    mergeStrategyOptions([])
    syncSelectedStrategiesToOptions()
  },
  { deep: true }
)

watch(
  () => multiStrategyForm.selectedStrategies,
  () => {
    syncSelectedStrategiesToOptions()
  },
  { deep: true }
)
</script>

<style scoped>
.multi-strategy-card {
  margin: 20px 0;
  width: 100%;
  border: 1px solid #d6d2cb;
  background: #fbfaf8;
  box-shadow: 0 12px 20px rgba(107, 103, 99, 0.1);
  border-radius: 12px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-weight: 600;
}

.strategy-selection {
  margin-bottom: 16px;
}

.strategy-checkbox-panel {
  width: 100%;
}

.strategy-checkbox-panel :deep(.el-checkbox-group) {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px 12px;
}

.webhook-row {
  margin-top: 10px;
  width: 100%;
}
</style>
