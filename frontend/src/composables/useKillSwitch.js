import { ref } from 'vue'
import {
  getDrawSuggestionMetricsSummary,
  getKillSwitchState,
  llmAlertSummary,
  manualReleaseKillSwitch,
  manualStopKillSwitch
} from '@/api/drawPrediction'

export function useKillSwitch() {
  const loading = ref(false)
  const stateLoading = ref(false)
  const metricsLoading = ref(false)
  const alertLoading = ref(false)

  const state = ref({
    state: 'RUN',
    reason: null,
    manual_override: 0,
    updated_at: null
  })

  const metrics = ref({
    roi_7d: 0,
    max_drawdown: 0,
    win_rate: 0,
    clv_50: 0,
    rolling_clv_50: 0,
    state: 'RUN',
    settled_count: 0,
    days: 7
  })

  const alertSummary = ref({
    title: '',
    summary: '',
    actions: []
  })

  const refreshState = async () => {
    stateLoading.value = true
    try {
      state.value = await getKillSwitchState()
      return state.value
    } finally {
      stateLoading.value = false
    }
  }

  const refreshMetrics = async () => {
    metricsLoading.value = true
    try {
      metrics.value = await getDrawSuggestionMetricsSummary({ days: 7 })
      return metrics.value
    } finally {
      metricsLoading.value = false
    }
  }

  const refreshAll = async () => {
    loading.value = true
    try {
      await Promise.all([refreshState(), refreshMetrics()])
    } finally {
      loading.value = false
    }
  }

  const manualStop = async ({ operator, note }) => {
    loading.value = true
    try {
      await manualStopKillSwitch({ operator, note })
      await refreshAll()
    } finally {
      loading.value = false
    }
  }

  const manualRelease = async ({ operator, note }) => {
    loading.value = true
    try {
      await manualReleaseKillSwitch({ operator, note })
      await refreshAll()
    } finally {
      loading.value = false
    }
  }

  const generateAlertSummary = async () => {
    alertLoading.value = true
    try {
      const data = await llmAlertSummary({
        state: state.value?.state || metrics.value?.state || 'RUN',
        metrics: {
          roi_7d: metrics.value?.roi_7d || 0,
          max_drawdown: metrics.value?.max_drawdown || 0,
          clv_50: metrics.value?.clv_50 || 0
        },
        prompt_version: 'v1'
      })
      alertSummary.value = {
        title: data?.title || '风控摘要',
        summary: data?.summary || '暂无摘要',
        actions: Array.isArray(data?.actions) ? data.actions : []
      }
      return alertSummary.value
    } finally {
      alertLoading.value = false
    }
  }

  return {
    loading,
    stateLoading,
    metricsLoading,
    alertLoading,
    state,
    metrics,
    alertSummary,
    refreshState,
    refreshMetrics,
    refreshAll,
    manualStop,
    manualRelease,
    generateAlertSummary
  }
}
