import request from '@/utils/request'

// 获取爬虫系统状态
export function getCrawlerStatus() {
  return request({
    url: '/api/admin/crawler/status',
    method: 'get'
  })
}

// 获取爬虫任务列表
export function getCrawlerTasks(params) {
  return request({
    url: '/api/admin/crawler/tasks',
    method: 'get',
    params
  })
}

// 启动爬虫任务
export function startCrawlerTask(data) {
  return request({
    url: '/api/admin/crawler/tasks/start',
    method: 'post',
    data
  })
}

// 停止爬虫任务
export function stopCrawlerTask(taskId) {
  return request({
    url: `/api/admin/crawler/tasks/${taskId}/stop`,
    method: 'post'
  })
}

// 获取爬虫统计信息
export function getCrawlerStats(params) {
  return request({
    url: '/api/admin/crawler/stats',
    method: 'get',
    params
  })
}

// 获取爬虫日志
export function getCrawlerLogs(params) {
  return request({
    url: '/api/admin/crawler/logs',
    method: 'get',
    params
  })
}

// 清空爬虫队列
export function clearCrawlerQueue() {
  return request({
    url: '/api/admin/crawler/queue/clear',
    method: 'post'
  })
}

// 重新启动爬虫服务
export function restartCrawlerService() {
  return request({
    url: '/api/admin/crawler/restart',
    method: 'post'
  })
}

// 兼容前端页面导入的别名
export const getStatus = getCrawlerStatus
export const getTasks = getCrawlerTasks
export const getStats = getCrawlerStats
export const getLogs = getCrawlerLogs