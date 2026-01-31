import request from '@/utils/request'

// 获取系统健康状态
export function getSystemHealth() {
  return request({
    url: '/api/admin/crawler/monitor/health',
    method: 'get'
  })
}

// 获取告警列表
export function getAlerts(params) {
  return request({
    url: '/api/admin/crawler/monitor/alerts',
    method: 'get',
    params
  })
}

// 获取告警历史
export function getAlertHistory(params) {
  return request({
    url: '/api/admin/crawler/monitor/alerts/history',
    method: 'get',
    params
  })
}

// 确认告警
export function acknowledgeAlert(alertId) {
  return request({
    url: `/api/admin/crawler/monitor/alerts/${alertId}/acknowledge`,
    method: 'put'
  })
}

// 获取系统资源使用情况
export function getSystemResources() {
  return request({
    url: '/api/admin/crawler/monitor/resources',
    method: 'get'
  })
}

// 获取监控指标数据
export function getMetrics(params) {
  return request({
    url: '/api/admin/crawler/monitor/metrics',
    method: 'get',
    params
  })
}

// 获取采集成功率趋势
export function getSuccessRateTrend(params) {
  return request({
    url: '/api/admin/crawler/monitor/trends/success-rate',
    method: 'get',
    params
  })
}

// 获取数据采集量统计
export function getDataVolumeStats(params) {
  return request({
    url: '/api/admin/crawler/monitor/stats/data-volume',
    method: 'get',
    params
  })
}

// 获取告警规则列表
export function getAlertRules() {
  return request({
    url: '/api/admin/crawler/monitor/alert-rules',
    method: 'get'
  })
}

// 创建告警规则
export function createAlertRule(data) {
  return request({
    url: '/api/admin/crawler/monitor/alert-rules',
    method: 'post',
    data
  })
}

// 更新告警规则
export function updateAlertRule(ruleId, data) {
  return request({
    url: `/api/admin/crawler/monitor/alert-rules/${ruleId}`,
    method: 'put',
    data
  })
}

// 删除告警规则
export function deleteAlertRule(ruleId) {
  return request({
    url: `/api/admin/crawler/monitor/alert-rules/${ruleId}`,
    method: 'delete'
  })
}

// 测试告警规则
export function testAlertRule(data) {
  return request({
    url: '/api/admin/crawler/monitor/alert-rules/test',
    method: 'post',
    data
  })
}

// 获取实时监控数据 (WebSocket endpoint info)
export function getRealtimeEndpoint() {
  return request({
    url: '/api/admin/crawler/monitor/realtime/endpoint',
    method: 'get'
  })
}

// 导出监控报告
export function exportMonitorReport(params) {
  return request({
    url: '/api/admin/crawler/monitor/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

// 获取爬虫实例状态
export function getCrawlerInstances() {
  return request({
    url: '/api/admin/crawler/monitor/instances',
    method: 'get'
  })
}

// 重启爬虫实例
export function restartCrawlerInstance(instanceId) {
  return request({
    url: `/api/admin/crawler/monitor/instances/${instanceId}/restart`,
    method: 'post'
  })
}

// 获取数据库性能指标
export function getDatabaseMetrics() {
  return request({
    url: '/api/admin/crawler/monitor/database/metrics',
    method: 'get'
  })
}

// 获取网络连接状态
export function getNetworkStatus() {
  return request({
    url: '/api/admin/crawler/monitor/network/status',
    method: 'get'
  })
}

// 清理监控数据
export function cleanupMonitorData(params) {
  return request({
    url: '/api/admin/crawler/monitor/cleanup',
    method: 'delete',
    params
  })
}