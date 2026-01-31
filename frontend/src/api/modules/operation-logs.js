import http from '@/utils/http'
import { API_ENDPOINTS } from '@/config/api'

/**
 * 操作日志相关API
 */

// 获取操作日志列表
export const getOperationLogs = (params) => {
  return http.get(API_ENDPOINTS.OPERATION_LOGS.LIST, { params })
}

// 获取日志详情
export const getLogDetail = (id) => {
  return http.get(`${API_ENDPOINTS.OPERATION_LOGS.LIST}/${id}`)
}

// 删除日志
export const deleteLog = (id) => {
  return http.delete(`${API_ENDPOINTS.OPERATION_LOGS.LIST}/${id}`)
}

// 批量删除日志
export const batchDeleteLogs = (ids) => {
  return http.delete(`${API_ENDPOINTS.OPERATION_LOGS.LIST}/batch`, { data: { ids } })
}

// 清空日志
export const clearLogs = (beforeDate) => {
  return http.delete(`${API_ENDPOINTS.OPERATION_LOGS.LIST}/clear`, { params: { beforeDate } })
}

// 获取日志统计信息
export const getLogStats = (params) => {
  return http.get(API_ENDPOINTS.OPERATION_LOGS.STATISTICS, { params })
}

// 导出日志
export const exportLogs = (params) => {
  return http.get(API_ENDPOINTS.OPERATION_LOGS.EXPORT, { params, responseType: 'blob' })
}

// 获取操作模块列表 - 这个端点可能不存在，暂时注释掉
// export const getOperationModules = () => {
//   return http.get('/api/v1/admin/operation-logs/modules')
// }

// 获取操作类型列表 - 这个端点可能不存在，暂时注释掉  
// export const getOperationActions = () => {
//   return http.get('/api/v1/admin/operation-logs/actions')
// }

// 获取用户操作统计 - 这个端点可能不存在，暂时注释掉
// export const getUserOperationStats = (userId, params) => {
//   return http.get(`/api/v1/admin/users/${userId}/operation-stats`, { params })
// }

// 获取热门操作排行 - 这个端点可能不存在，暂时注释掉
// export const getPopularOperations = (params) => {
//   return http.get('/api/v1/admin/operation-logs/popular', { params })
// }

// 获取异常操作记录 - 这个端点可能不存在，暂时注释掉
// export const getErrorOperations = (params) => {
//   return http.get('/api/v1/admin/operation-logs/errors', { params })
// }

// 获取登录统计 - 这个端点可能不存在，暂时注释掉
// export const getLoginStats = (params) => {
//   return http.get('/api/v1/admin/operation-logs/login-stats', { params })
// }

// 实时监控日志 - 这个端点可能不存在，暂时注释掉
// export const getRealtimeLogs = (params) => {
//   return http.get('/api/v1/admin/operation-logs/realtime', { params })
// }

// 获取日志趋势数据 - 这个端点可能不存在，暂时注释掉
// export const getLogTrends = (params) => {
//   return http.get('/api/v1/admin/operation-logs/trends', { params })
// }

// 归档日志 - 这个端点可能不存在，暂时注释掉
// export const archiveLogs = (beforeDate) => {
//   return http.post('/api/v1/admin/operation-logs/archive', null, { params: { beforeDate } })
// }

// 下载日志文件 - 这个端点可能不存在，暂时注释掉
// export const downloadLogFile = (logFile) => {
//   return http.get(`/api/v1/admin/operation-logs/download/${logFile}`, { responseType: 'blob' })
// }

// 别名导出，以匹配组件中的导入
export const deleteOperationLog = deleteLog
export const exportOperationLogs = exportLogs
export const cleanupOperationLogs = clearLogs