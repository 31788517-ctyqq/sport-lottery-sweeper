import request from '@/utils/request'

// 系统状态和配置API
// 获取系统状态
export function getSystemStatus() {
  return request({
    url: '/api/admin/system/status',
    method: 'get'
  })
}

// 获取系统统计信息
export function getSystemStats() {
  return request({
    url: '/api/admin/system/stats',
    method: 'get'
  })
}

// 获取系统配置
export function getSystemConfig() {
  return request({
    url: '/api/admin/system/config',
    method: 'get'
  })
}

// 清理系统缓存
export function clearSystemCache() {
  return request({
    url: '/api/admin/system/clear-cache',
    method: 'post'
  })
}

// 备份管理API
// 创建数据库备份
export function createDatabaseBackup() {
  return request({
    url: '/api/admin/system/backup/database',
    method: 'post'
  })
}

// 创建文件备份
export function createFileBackup() {
  return request({
    url: '/api/admin/system/backup/files',
    method: 'post'
  })
}

// 获取备份历史记录
export function getBackupHistory() {
  return request({
    url: '/api/admin/system/backup/history',
    method: 'get'
  })
}

// 恢复备份
export function restoreBackup(backupId) {
  return request({
    url: `/api/admin/system/backup/${backupId}/restore`,
    method: 'post'
  })
}

// 删除备份
export function deleteBackup(backupId) {
  return request({
    url: `/api/admin/system/backup/${backupId}`,
    method: 'delete'
  })
}

// API管理
// 获取API端点列表
export function getAPIEndpoints() {
  return request({
    url: '/api/admin/system/api/endpoints',
    method: 'get'
  })
}

// 测试API端点
export function testAPIEndpoint(path, method) {
  return request({
    url: '/api/admin/system/api/test',
    method: 'post',
    data: { path, method }
  })
}

// 获取API访问统计
export function getAPIAccessStats() {
  return request({
    url: '/api/admin/system/api/stats',
    method: 'get'
  })
}

// 更新API访问控制
export function updateAPIAccess(data) {
  return request({
    url: '/api/admin/system/api/access-control',
    method: 'put',
    data
  })
}

// 系统日志API
// 获取系统日志
export function getSystemLogs(params) {
  return request({
    url: '/api/admin/system/logs',
    method: 'get',
    params
  })
}

// 清理系统日志
export function clearSystemLogs() {
  return request({
    url: '/api/admin/system/logs/clear',
    method: 'post'
  })
}

// 系统维护API
// 执行健康检查
export function performHealthCheck() {
  return request({
    url: '/api/admin/system/health-check',
    method: 'post'
  })
}

// 重启服务
export function restartService() {
  return request({
    url: '/api/admin/system/restart',
    method: 'post'
  })
}

// 重载配置
export function reloadConfig() {
  return request({
    url: '/api/admin/system/reload-config',
    method: 'post'
  })
}
