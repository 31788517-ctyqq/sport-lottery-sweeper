import { ref, onBeforeUnmount } from 'vue'
import { getDrawPredictionTask } from '@/api/drawPrediction'

export function useAsyncTask() {
  const taskId = ref('')
  const status = ref('idle')
  const progress = ref(0)
  const message = ref('')
  const result = ref(null)
  const error = ref('')
  const polling = ref(false)

  let timer = null

  const stopPolling = () => {
    polling.value = false
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }

  const reset = () => {
    stopPolling()
    taskId.value = ''
    status.value = 'idle'
    progress.value = 0
    message.value = ''
    result.value = null
    error.value = ''
  }

  const syncTaskData = (data) => {
    status.value = String(data?.status || 'pending').toLowerCase()
    progress.value = Number(data?.progress || 0)
    message.value = String(data?.message || '')
    result.value = data?.result || null
    error.value = data?.error || ''
  }

  const pollTask = async (id, options = {}) => {
    const intervalMs = Number(options.intervalMs || 1200)
    const maxAttempts = Number(options.maxAttempts || 600)
    const onSuccess = options.onSuccess
    const onFailed = options.onFailed

    let attempts = 0
    polling.value = true
    taskId.value = id

    const loop = async () => {
      if (!polling.value) return
      attempts += 1

      try {
        const data = await getDrawPredictionTask(id)
        syncTaskData(data)

        if (status.value === 'success') {
          stopPolling()
          if (typeof onSuccess === 'function') onSuccess(data)
          return
        }

        if (status.value === 'failed' || status.value === 'cancelled') {
          stopPolling()
          if (typeof onFailed === 'function') onFailed(data)
          return
        }
      } catch (err) {
        stopPolling()
        status.value = 'failed'
        error.value = err?.response?.data?.detail || err?.message || '任务轮询失败'
        if (typeof onFailed === 'function') onFailed({ error: error.value })
        return
      }

      if (attempts >= maxAttempts) {
        stopPolling()
        status.value = 'failed'
        error.value = '任务轮询超时'
        if (typeof onFailed === 'function') onFailed({ error: error.value })
        return
      }

      timer = setTimeout(loop, intervalMs)
    }

    await loop()
  }

  onBeforeUnmount(() => {
    stopPolling()
  })

  return {
    taskId,
    status,
    progress,
    message,
    result,
    error,
    polling,
    pollTask,
    stopPolling,
    reset
  }
}
