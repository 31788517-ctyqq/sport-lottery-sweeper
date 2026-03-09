<template>
  <div class="page-container">
    <el-card class="box-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>风控与熔断监控</span>
          <div class="header-actions">
            <el-button @click="handleRefresh">刷新</el-button>
            <el-button type="warning" :loading="alertLoading" @click="handleGenerateAlert">生成告警说明</el-button>
          </div>
        </div>
      </template>

      <div class="state-panel">
        <div class="state-item">
          <div class="label">当前状态</div>
          <el-tag :type="stateTagType" size="large">{{ state.state || 'RUN' }}</el-tag>
        </div>
        <div class="state-item">
          <div class="label">手动覆写</div>
          <el-tag :type="Number(state.manual_override) === 1 ? 'warning' : 'info'">{{ Number(state.manual_override) === 1 ? '是' : '否' }}</el-tag>
        </div>
        <div class="state-item">
          <div class="label">更新时间</div>
          <div class="value">{{ formatDate(state.updated_at) }}</div>
        </div>
      </div>

      <div class="metric-grid" v-loading="metricsLoading">
        <div class="metric-card">
          <div class="label">ROI(7d)</div>
          <div class="value">{{ formatPercent(metrics.roi_7d) }}</div>
        </div>
        <div class="metric-card">
          <div class="label">最大回撤</div>
          <div class="value">{{ formatPercent(metrics.max_drawdown) }}</div>
        </div>
        <div class="metric-card">
          <div class="label">CLV(50)</div>
          <div class="value">{{ formatPercent(metrics.clv_50) }}</div>
        </div>
        <div class="metric-card">
          <div class="label">胜率</div>
          <div class="value">{{ formatPercent(metrics.win_rate) }}</div>
        </div>
        <div class="metric-card">
          <div class="label">结算样本</div>
          <div class="value">{{ metrics.settled_count || 0 }}</div>
        </div>
      </div>

      <el-form :model="form" inline class="action-form">
        <el-form-item label="操作人">
          <el-input v-model="form.operator" placeholder="admin" style="width: 180px" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.note" placeholder="输入风控备注" style="width: 320px" />
        </el-form-item>
        <el-form-item>
          <el-button type="danger" :loading="loading" @click="handleManualStop">手动 STOP</el-button>
          <el-button type="success" :loading="loading" @click="handleManualRelease">手动 RELEASE</el-button>
        </el-form-item>
      </el-form>

      <el-card shadow="never" class="reason-card">
        <template #header><span>风控原因(JSON)</span></template>
        <pre class="reason-json">{{ prettyReason }}</pre>
      </el-card>

      <el-card shadow="never" class="reason-card">
        <template #header><span>AI 告警说明</span></template>
        <div class="alert-title">{{ alertSummary.title || '-' }}</div>
        <div class="alert-summary">{{ alertSummary.summary || '-' }}</div>
        <ul class="action-list">
          <li v-for="item in alertSummary.actions" :key="item">{{ item }}</li>
        </ul>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useKillSwitch } from '@/composables/useKillSwitch'

const {
  loading,
  metricsLoading,
  alertLoading,
  state,
  metrics,
  alertSummary,
  refreshAll,
  manualStop,
  manualRelease,
  generateAlertSummary
} = useKillSwitch()

const form = reactive({
  operator: 'admin',
  note: ''
})

const stateTagType = computed(() => {
  const s = String(state.value?.state || 'RUN').toUpperCase()
  if (s === 'STOP') return 'danger'
  if (s === 'WARN') return 'warning'
  return 'success'
})

const prettyReason = computed(() => {
  try {
    return JSON.stringify(state.value?.reason || {}, null, 2)
  } catch (_e) {
    return String(state.value?.reason || '-')
  }
})

const formatDate = (v) => {
  if (!v) return '-'
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return String(v)
  return d.toLocaleString()
}

const toNumber = (v) => {
  const n = Number(v)
  return Number.isFinite(n) ? n : null
}

const formatPercent = (v) => {
  const n = toNumber(v)
  if (n == null) return '-'
  return `${(n * 100).toFixed(2)}%`
}

const normalizedOperator = () => String(form.operator || '').trim() || 'admin'

const handleRefresh = async () => {
  try {
    await refreshAll()
  } catch (err) {
    console.error('刷新风控状态失败:', err)
    ElMessage.error('刷新失败，请稍后重试')
  }
}

const handleManualStop = async () => {
  try {
    await manualStop({ operator: normalizedOperator(), note: form.note })
    ElMessage.success('已切换为 STOP')
  } catch (err) {
    console.error('手动STOP失败:', err)
    ElMessage.error('手动STOP失败')
  }
}

const handleManualRelease = async () => {
  try {
    await manualRelease({ operator: normalizedOperator(), note: form.note })
    ElMessage.success('已释放为 RUN')
  } catch (err) {
    console.error('手动RELEASE失败:', err)
    ElMessage.error('手动RELEASE失败')
  }
}

const handleGenerateAlert = async () => {
  try {
    await generateAlertSummary()
  } catch (err) {
    console.error('生成告警说明失败:', err)
    ElMessage.error('生成告警说明失败')
  }
}

onMounted(async () => {
  await handleRefresh()
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-actions { display: flex; gap: 8px; }
.state-panel { display: grid; grid-template-columns: repeat(3, minmax(120px, 1fr)); gap: 10px; margin-bottom: 14px; }
.state-item { border: 1px solid #ebeef5; border-radius: 6px; padding: 10px; }
.label { color: #909399; font-size: 12px; margin-bottom: 6px; }
.value { font-weight: 600; color: #303133; }
.metric-grid { display: grid; grid-template-columns: repeat(5, minmax(120px, 1fr)); gap: 10px; margin-bottom: 14px; }
.metric-card { border: 1px solid #ebeef5; border-radius: 6px; padding: 10px; }
.action-form { margin: 12px 0; }
.reason-card { margin-top: 12px; }
.reason-json { margin: 0; max-height: 240px; overflow: auto; background: #f7f8fa; padding: 10px; border-radius: 6px; }
.alert-title { font-weight: 700; margin-bottom: 6px; }
.alert-summary { color: #303133; margin-bottom: 8px; }
.action-list { margin: 0; padding-left: 20px; }
</style>
