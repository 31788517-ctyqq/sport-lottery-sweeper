import request from '@/utils/request'

// 获取爬虫系统健康状态
export function getHealthStatus() {
  return request({
    url: '/api/v1/admin/crawler/monitor/health',
    method: 'get'
  })
}

// 获取告警列表
export function getAlerts(params) {
  return request({
    url: '/api/v1/admin/crawler/monitor/alerts',
    method: 'get',
    params
  })
}

// 获取告警历史
export function getAlertHistory() {
  return request({
    url: '/api/v1/admin/crawler/monitor/alerts/history',
    method: 'get'
  })
}

// 确认告警
export function acknowledgeAlert(alertId) {
  return request({
    url: `/api/v1/admin/crawler/monitor/alerts/${alertId}/acknowledge`,
    method: 'put'
  })
}

// 获取系统资源使用情况
export function getResourcesUsage() {
  return request({
    url: '/api/v1/admin/crawler/monitor/resources',
    method: 'get'
  })
}

// 获取监控指标
export function getMetrics() {
  return request({
    url: '/api/v1/admin/crawler/monitor/metrics',
    method: 'get'
  })
}

// 获取成功率趋势
export function getSuccessRateTrends(params) {
  return request({
    url: '/api/v1/admin/crawler/monitor/trends/success-rate',
    method: 'get',
    params
  })
}

// 获取数据量分布统计
export function getDataVolumeStats(params) {
  return request({
    url: '/api/v1/admin/crawler/monitor/stats/data-volume',
    method: 'get',
    params
  })
}

// 获取告警规则
export function getAlertRules() {
  return request({
    url: '/api/v1/admin/crawler/monitor/alert-rules',
    method: 'get'
  })
}

// 创建告警规则
export function createAlertRule(data) {
  return request({
    url: '/api/v1/admin/crawler/monitor/alert-rules',
    method: 'post',
    data
  })
}

// 更新告警规则
export function updateAlertRule(ruleId, data) {
  return request({
    url: `/api/v1/admin/crawler/monitor/alert-rules/${ruleId}`,
    method: 'put',
    data
  })
}

// 删除告警规则
export function deleteAlertRule(ruleId) {
  return request({
    url: `/api/v1/admin/crawler/monitor/alert-rules/${ruleId}`,
    method: 'delete'
  })
}

// 测试告警规则
export function testAlertRule() {
  return request({
    url: '/api/v1/admin/crawler/monitor/alert-rules/test',
    method: 'post'
  })
}

// 获取实时连接信息
export function getRealtimeEndpoint() {
  return request({
    url: '/api/v1/admin/crawler/monitor/realtime/endpoint',
    method: 'get'
  })
}

// 导出监控数据
export function exportMonitorData() {
  return request({
    url: '/api/v1/admin/crawler/monitor/export',
    method: 'get'
  })
}

// 获取实例列表
export function getInstances() {
  return request({
    url: '/api/v1/admin/crawler/monitor/instances',
    method: 'get'
  })
}

// 重启实例
export function restartInstance(instanceId) {
  return request({
    url: `/api/v1/admin/crawler/monitor/instances/${instanceId}/restart`,
    method: 'post'
  })
}

// 获取数据库指标
export function getDatabaseMetrics() {
  return request({
    url: '/api/v1/admin/crawler/monitor/database/metrics',
    method: 'get'
  })
}

// 获取网络状态
export function getNetworkStatus() {
  return request({
    url: '/api/v1/admin/crawler/monitor/network/status',
    method: 'get'
  })
}

// 清理监控数据
export function cleanupMonitorData() {
  return request({
    url: '/api/v1/admin/crawler/monitor/cleanup',
    method: 'post'
  })
}
