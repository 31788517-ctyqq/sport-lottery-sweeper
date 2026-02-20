import request from '@/utils/request'

const BASE = '/api/v1/admin/intelligence/collection'

export const getCollectionSources = () => request.get(`${BASE}/sources`)

export const getTimeWindowSettings = () => request.get(`${BASE}/settings/time-window`)

export const updateTimeWindowSettings = (data) =>
  request.put(`${BASE}/settings/time-window`, data)

export const getNetworkSettings = () => request.get(`${BASE}/settings/network`)

export const updateNetworkSettings = (data) =>
  request.put(`${BASE}/settings/network`, data)

export const getSourceRules = () => request.get(`${BASE}/settings/source-rules`)

export const updateSourceRules = (data) =>
  request.put(`${BASE}/settings/source-rules`, data)

export const getQualityThresholds = () => request.get(`${BASE}/settings/quality-thresholds`)

export const updateQualityThresholds = (data) =>
  request.put(`${BASE}/settings/quality-thresholds`, data)

export const getAliasDictionary = () => request.get(`${BASE}/settings/alias-dictionary`)

export const updateAliasDictionary = (data) =>
  request.put(`${BASE}/settings/alias-dictionary`, data)

export const getJczqMatches = (params) => request.get(`${BASE}/matches`, { params })

export const getCollectionGraphOverview = (params, options = {}) =>
  request.get(`${BASE}/graph/overview`, {
    params,
    timeout: options.timeout || 60000
  })

export const createCollectionTask = (data, options = {}) =>
  request.post(`${BASE}/tasks`, data, {
    timeout: options.timeout || 180000
  })

export const createCollectionSchedule = (data) => request.post(`${BASE}/schedules`, data)

export const getCollectionTasks = (params, options = {}) => {
  const config = {
    params,
    timeout: options.timeout || 60000
  }
  if (options.silentError) config.suppressErrorMessage = true
  return request.get(`${BASE}/tasks`, config)
}

export const getCollectionTask = (taskId, options = {}) => {
  const params = { ...(options.params || {}) }
  if (options.lightweight) params.lightweight = true
  const config = {
    timeout: options.timeout || 60000,
    params
  }
  if (options.silentError) config.suppressErrorMessage = true
  return request.get(`${BASE}/tasks/${taskId}`, config)
}

export const getCollectionTaskSubtasks = (taskId, params = {}, options = {}) =>
  request.get(`${BASE}/tasks/${taskId}/subtasks`, {
    params,
    timeout: options.timeout || 60000
  })

export const retryCollectionTask = (taskId, payloadOrOptions = null, options = {}) => {
  let payload = null
  let config = options || {}
  if (
    payloadOrOptions &&
    typeof payloadOrOptions === 'object' &&
    ('timeout' in payloadOrOptions || 'headers' in payloadOrOptions || 'params' in payloadOrOptions) &&
    !('match_ids' in payloadOrOptions) &&
    !('sources' in payloadOrOptions) &&
    !('intel_types' in payloadOrOptions)
  ) {
    config = payloadOrOptions
  } else {
    payload = payloadOrOptions
  }
  return request.post(`${BASE}/tasks/${taskId}/retry`, payload, {
    timeout: config.timeout || 180000
  })
}

export const cancelCollectionTask = (taskId) => request.post(`${BASE}/tasks/${taskId}/cancel`)

export const getCollectionTaskLogs = (taskId, params = {}) =>
  request.get(`${BASE}/tasks/${taskId}/logs`, { params })

export const getMatchCollectionItems = (matchId, params) =>
  request.get(`${BASE}/matches/${matchId}/items`, { params })

export const debugMatchCandidates = (data, options = {}) =>
  request.post(`${BASE}/debug/match-candidates`, data, {
    timeout: options.timeout || 90000
  })

export const debugReplay = (data, options = {}) =>
  request.post(`${BASE}/debug/replay`, data, {
    timeout: options.timeout || 90000
  })

export const getSourceHealth = (params = {}) =>
  request.get(`${BASE}/sources/health`, { params })

export const getPushPreview = (matchId, data) =>
  request.post(`${BASE}/matches/${matchId}/push-preview`, data)

export const createPushTask = (data) => request.post(`${BASE}/push/tasks`, data)

export const getMySubscription = () => request.get(`${BASE}/subscriptions/me`)

export const updateMySubscription = (data) => request.put(`${BASE}/subscriptions/me`, data)

export const getDingTalkBindings = () => request.get(`${BASE}/channels/dingtalk/bindings`)

export const createDingTalkBinding = (data) =>
  request.post(`${BASE}/channels/dingtalk/bindings`, data)

export const updateDingTalkBinding = (id, data) =>
  request.put(`${BASE}/channels/dingtalk/bindings/${id}`, data)

export const deleteDingTalkBinding = (id) =>
  request.delete(`${BASE}/channels/dingtalk/bindings/${id}`)

export const testDingTalkBinding = (id) =>
  request.post(`${BASE}/channels/dingtalk/bindings/${id}/test`)
