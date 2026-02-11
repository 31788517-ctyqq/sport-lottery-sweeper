import request from '@/utils/request'

// 获取爬虫健康状态
export function getHealthStatus() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/health',
    method: 'get'
  })
}

// AI_WORKING: coder1 @2026-02-04T18:40:30 - 修改getAlerts函数以支持params参数
// 获取警报列表
export function getAlerts(params) {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/alerts',
    method: 'get',
    params
  })
}
// AI_DONE: coder1 @2026-02-04T18:40:30

// 获取警报历史
export function getAlertHistory() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/alerts/history',
    method: 'get'
  })
}

// 确认警报
export function acknowledgeAlert(alertId) {
  return request({
    // 修正：使用实际API路径
    url: `/api/v1/admin/crawler/monitor/alerts/${alertId}/acknowledge`,
    method: 'post'
  })
}

// 获取资源使用情况
export function getResourcesUsage() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/resources',
    method: 'get'
  })
}

// 获取指标数据
export function getMetrics() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/metrics',
    method: 'get'
  })
}

// 获取成功率趋势
export function getSuccessRateTrends() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/trends/success-rate',
    method: 'get'
  })
}

// 获取数据量统计
export function getDataVolumeStats() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/stats/data-volume',
    method: 'get'
  })
}

// 获取警报规则
export function getAlertRules() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/alert-rules',
    method: 'get'
  })
}

// 创建警报规则
export function createAlertRule(data) {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/alert-rules',
    method: 'post',
    data
  })
}

// 更新警报规则
export function updateAlertRule(ruleId, data) {
  return request({
    // 修正：使用实际API路径
    url: `/api/v1/admin/crawler/monitor/alert-rules/${ruleId}`,
    method: 'put',
    data
  })
}

// 删除警报规则
export function deleteAlertRule(ruleId) {
  return request({
    // 修正：使用实际API路径
    url: `/api/v1/admin/crawler/monitor/alert-rules/${ruleId}`,
    method: 'delete'
  })
}

// 测试警报规则
export function testAlertRule() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/alert-rules/test',
    method: 'post'
  })
}

// 获取实时连接
export function getRealtimeEndpoint() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/realtime/endpoint',
    method: 'get'
  })
}

// 导出监控数据
export function exportMonitorData() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/export',
    method: 'get'
  })
}

// 获取实例列表
export function getInstances() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/instances',
    method: 'get'
  })
}

// 重启实例
export function restartInstance(instanceId) {
  return request({
    // 修正：使用实际API路径
    url: `/api/v1/admin/crawler/monitor/instances/${instanceId}/restart`,
    method: 'post'
  })
}

// 获取数据库指标
export function getDatabaseMetrics() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/database/metrics',
    method: 'get'
  })
}

// 获取网络状态
export function getNetworkStatus() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/network/status',
    method: 'get'
  })
}

// 清理监控数据
export function cleanupMonitorData() {
  return request({
    // 修正：使用实际API路径
    url: '/api/v1/admin/crawler/monitor/cleanup',
    method: 'post'
  })
}