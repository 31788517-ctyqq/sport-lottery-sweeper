import { computed, reactive, ref } from 'vue'
import {
  createPaperBets,
  fetchOddsSnapshotsAsync,
  generateSuggestionsAsync,
  getDrawSuggestionMetricsSummary,
  getOddsSnapshots,
  getSuggestionList,
  llmExplain,
  llmReport,
  settlePaperBetsAsync
} from '@/api/drawPrediction'
import { useAsyncTask } from '@/composables/useAsyncTask'

export function useDrawSuggestion() {
  const loading = ref(false)
  const snapshotsLoading = ref(false)
  const metricsLoading = ref(false)
  const submitting = ref(false)

  const suggestions = ref([])
  const suggestionsTotal = ref(0)
  const snapshots = ref([])
  const snapshotsTotal = ref(0)

  const metrics = ref({
    roi_7d: 0,
    max_drawdown: 0,
    win_rate: 0,
    clv_50: 0,
    state: 'RUN',
    settled_count: 0
  })

  const query = reactive({
    date: '',
    decision: '',
    page: 1,
    pageSize: 20
  })

  const snapshotTask = useAsyncTask()
  const generateTask = useAsyncTask()
  const settleTask = useAsyncTask()

  const explanationMap = reactive({})
  const explaining = reactive({})
  const latestReport = ref('')
  const reportLoading = ref(false)

  const stateTagType = computed(() => {
    const state = String(metrics.value?.state || 'RUN').toUpperCase()
    if (state === 'STOP') return 'danger'
    if (state === 'WARN') return 'warning'
    return 'success'
  })

  const refreshSuggestions = async () => {
    loading.value = true
    try {
      const data = await getSuggestionList({
        date_str: query.date || undefined,
        decision: query.decision || undefined,
        page: query.page,
        page_size: query.pageSize
      })
      suggestions.value = Array.isArray(data?.items) ? data.items : []
      suggestionsTotal.value = Number(data?.total || 0)
    } finally {
      loading.value = false
    }
  }

  const refreshSnapshots = async () => {
    snapshotsLoading.value = true
    try {
      const data = await getOddsSnapshots({
        date_str: query.date || undefined,
        page: 1,
        page_size: 20
      })
      snapshots.value = Array.isArray(data?.items) ? data.items : []
      snapshotsTotal.value = Number(data?.total || 0)
    } finally {
      snapshotsLoading.value = false
    }
  }

  const refreshMetrics = async () => {
    metricsLoading.value = true
    try {
      metrics.value = await getDrawSuggestionMetricsSummary({ days: 7 })
    } finally {
      metricsLoading.value = false
    }
  }

  const fetchSnapshots = async () => {
    submitting.value = true
    try {
      const task = await fetchOddsSnapshotsAsync({
        date_str: query.date || undefined,
        source: '500'
      })
      await snapshotTask.pollTask(task.task_id, {
        intervalMs: task.polling_interval_ms || 1200,
        onSuccess: async () => {
          await refreshSnapshots()
        }
      })
    } finally {
      submitting.value = false
    }
  }

  const generateSuggestions = async () => {
    submitting.value = true
    try {
      const task = await generateSuggestionsAsync({
        date: query.date || undefined,
        force: false
      })
      await generateTask.pollTask(task.task_id, {
        intervalMs: task.polling_interval_ms || 1200,
        onSuccess: async () => {
          await Promise.all([refreshSuggestions(), refreshMetrics()])
        }
      })
    } finally {
      submitting.value = false
    }
  }

  const settlePaperBets = async () => {
    submitting.value = true
    try {
      const task = await settlePaperBetsAsync({
        date: query.date || undefined
      })
      await settleTask.pollTask(task.task_id, {
        intervalMs: task.polling_interval_ms || 1200,
        onSuccess: async () => {
          await Promise.all([refreshSuggestions(), refreshMetrics()])
        }
      })
    } finally {
      submitting.value = false
    }
  }

  const batchCreatePaperBets = async (suggestionIds) => {
    if (!Array.isArray(suggestionIds) || suggestionIds.length === 0) return { created_count: 0, ids: [] }
    return createPaperBets({ suggestion_ids: suggestionIds })
  }

  const explainSuggestion = async (suggestionId) => {
    const key = String(suggestionId)
    if (!key) return ''
    if (explanationMap[key]) return explanationMap[key]

    explaining[key] = true
    try {
      const data = await llmExplain({
        suggestion_id: Number(suggestionId),
        style: 'concise',
        language: 'zh-CN',
        prompt_version: 'v1'
      })
      const text = data?.explanation || data?.risk_note || '暂无AI解读'
      explanationMap[key] = text
      return text
    } finally {
      explaining[key] = false
    }
  }

  const generateReport = async (reportType = 'daily') => {
    reportLoading.value = true
    try {
      const today = new Date()
      const yyyy = today.getFullYear()
      const mm = `${today.getMonth() + 1}`.padStart(2, '0')
      const dd = `${today.getDate()}`.padStart(2, '0')
      const data = await llmReport({
        report_type: reportType,
        date: `${yyyy}-${mm}-${dd}`,
        scope: 'draw_suggestion',
        metrics: {
          total_suggestions: suggestionsTotal.value,
          bet_count: suggestions.value.filter((x) => x.decision === 'BET').length,
          win_rate: metrics.value?.win_rate || 0,
          roi: metrics.value?.roi_7d || 0
        },
        prompt_version: 'v1'
      })
      latestReport.value = data?.content_markdown || data?.title || '暂无报告内容'
      return latestReport.value
    } finally {
      reportLoading.value = false
    }
  }

  return {
    loading,
    snapshotsLoading,
    metricsLoading,
    submitting,
    suggestions,
    suggestionsTotal,
    snapshots,
    snapshotsTotal,
    metrics,
    query,
    snapshotTask,
    generateTask,
    settleTask,
    stateTagType,
    explanationMap,
    explaining,
    latestReport,
    reportLoading,
    refreshSuggestions,
    refreshSnapshots,
    refreshMetrics,
    fetchSnapshots,
    generateSuggestions,
    settlePaperBets,
    batchCreatePaperBets,
    explainSuggestion,
    generateReport
  }
}
