import http from '@/utils/http'
import { API_ENDPOINTS } from '@/config/api'

const asDataResponse = async (promise) => {
  const result = await promise
  return result && typeof result === 'object' && 'data' in result ? result : { data: result }
}

const compactParams = (obj = {}) =>
  Object.fromEntries(
    Object.entries(obj).filter(([, value]) => value !== '' && value !== undefined && value !== null)
  )

const normalizeListParams = (params = {}) => {
  const hasPage = Number.isFinite(Number(params.page))
  const hasSize = Number.isFinite(Number(params.size))
  const size = hasSize ? Math.max(1, Number(params.size)) : 20
  const page = hasPage ? Math.max(1, Number(params.page)) : 1

  const search = params.search || params.action || params.module
  return compactParams({
    skip: (page - 1) * size,
    limit: size,
    user_id: params.userId,
    search,
    start_date: params.startTime,
    end_date: params.endTime
  })
}

const normalizeLogItem = (item = {}) => {
  const extra = (() => {
    if (!item.extra_data) return {}
    try {
      return typeof item.extra_data === 'string' ? JSON.parse(item.extra_data) : item.extra_data
    } catch {
      return {}
    }
  })()

  const responseStatus = item.response_status || extra.status_code || 200
  return {
    id: item.id,
    createdAt: item.created_at || item.timestamp,
    userRealName: extra.resource_name || '',
    username: extra.resource_name || '',
    module: item.module,
    action: extra.action || '',
    resource: extra.resource_type ? `${extra.resource_type}:${extra.resource_id || '-'}` : extra.resource_id || '-',
    description: item.message || '',
    ipAddress: item.ip_address,
    userAgent: item.user_agent,
    result: responseStatus >= 400 ? 'failed' : 'success',
    raw: item
  }
}

// 获取操作日志列表
export const getOperationLogs = async (params) => {
  const payload = await http.get(API_ENDPOINTS.OPERATION_LOGS.LIST, { params: normalizeListParams(params) })
  const items = Array.isArray(payload?.items) ? payload.items.map(normalizeLogItem) : []
  const total = Number(payload?.total || 0)
  const page = Number(params?.page || 1)
  const size = Number(params?.size || 20)
  return {
    data: {
      items,
      total,
      page,
      size,
      pages: Math.ceil(total / size)
    }
  }
}

// 获取日志详情
export const getLogDetail = (id) => asDataResponse(http.get(`${API_ENDPOINTS.OPERATION_LOGS.LIST}/${id}`))

// 删除日志
export const deleteLog = (id) => asDataResponse(http.delete(`${API_ENDPOINTS.OPERATION_LOGS.LIST}/item/${id}`))

// 批量删除日志
export const batchDeleteLogs = (ids) => asDataResponse(http.delete(`${API_ENDPOINTS.OPERATION_LOGS.LIST}/batch`, { data: { ids } }))

// 清空日志
export const clearLogs = (beforeDateOrParams) => {
  const params =
    typeof beforeDateOrParams === 'object' && beforeDateOrParams !== null
      ? beforeDateOrParams
      : { beforeDate: beforeDateOrParams }
  return asDataResponse(http.delete(`${API_ENDPOINTS.OPERATION_LOGS.LIST}/clear`, { params }))
}

// 获取日志统计信息
export const getLogStats = (params) => asDataResponse(http.get(API_ENDPOINTS.OPERATION_LOGS.STATISTICS, { params }))

// 导出日志
export const exportLogs = (params) => http.get(API_ENDPOINTS.OPERATION_LOGS.EXPORT, {
  params: normalizeListParams(params),
  responseType: 'blob'
})

// 别名导出，以匹配组件中的导入
export const deleteOperationLog = deleteLog
export const exportOperationLogs = exportLogs
export const cleanupOperationLogs = clearLogs
