import http from '@/utils/http'

/**
 * 用户日志相关API
 */

// 获取用户操作日志列表
export const getUserLogs = (params) => {
  return http.get('/api/v1/admin/system/logs/db/user', { params })
}

// 获取用户操作日志总数
export const getUserLogsCount = (params) => {
  return http.get('/api/v1/admin/system/logs/db/user/count', { params })
}

// 获取日志统计信息
export const getUserLogStatistics = (params) => {
  return http.get('/api/v1/admin/logs/db/statistics', { params })
}

// 搜索用户日志
export const searchUserLogs = (params) => {
  return http.get('/api/v1/admin/logs/db/search', { params })
}

// 获取用户安全日志（登录日志）
export const getUserSecurityLogs = (params) => {
  return http.get('/api/v1/admin/logs/db/security', { params })
}

// 获取用户系统日志
export const getUserSystemLogs = (params) => {
  return http.get('/api/v1/admin/logs/db/system', { params })
}

// 获取API调用日志
export const getUserApiLogs = (params) => {
  return http.get('/api/v1/admin/logs/db/api', { params })
}

// 获取单个日志详情
export const getUserLogDetail = (id) => {
  // 这个端点可能需要后端额外实现
  return http.get(`/api/v1/admin/logs/db/user/${id}`)
}

// 导出用户日志
export const exportUserLogs = (params) => {
  return http.get('/api/v1/admin/logs/db/user/export', { 
    params, 
    responseType: 'blob' 
  })
}

// 清理用户日志
export const cleanUserLogs = (params) => {
  return http.delete('/api/v1/admin/logs/db/user/clean', { params })
}

// 获取用户活动统计
export const getUserActivityStats = (userId, params) => {
  // 这个端点可能需要后端额外实现
  return http.get(`/api/v1/admin/users/${userId}/activity-stats`, { params })
}

// 别名导出，方便调用
export const fetchUserLogs = getUserLogs
export const fetchUserLogsCount = getUserLogsCount