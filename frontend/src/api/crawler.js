import request from '@/utils/request'

// 获取爬虫状态
export function getCrawlerStatus() {
  return request({
    // 修正：使用新版API路径
    url: '/api/admin/crawler/status',
    method: 'get'
  })
}

// 获取任务列表
export function getTasks() {
  return request({
    // 修正：使用新版API路径
    url: '/api/admin/crawler/tasks',
    method: 'get'
  })
}

// 开始任务
export function startTask() {
  return request({
    // 修正：使用新版API路径
    url: '/api/admin/crawler/tasks/start',
    method: 'post'
  })
}

// 停止任务
export function stopTask(taskId) {
  return request({
    // 修正：使用新版API路径
    url: `/api/admin/crawler/tasks/${taskId}/stop`,
    method: 'post'
  })
}

// 获取统计数据
export function getStats() {
  return request({
    // 修正：使用新版API路径
    url: '/api/admin/crawler/stats',
    method: 'get'
  })
}

// 获取日志
export function getLogs() {
  return request({
    // 修正：使用新版API路径
    url: '/api/admin/crawler/logs',
    method: 'get'
  })
}

// 清空队列
export function clearQueue() {
  return request({
    // 修正：使用新版API路径
    url: '/api/admin/crawler/queue/clear',
    method: 'post'
  })
}

// 重启爬虫
export function restartCrawler() {
  return request({
    // 修正：使用新版API路径
    url: '/api/admin/crawler/restart',
    method: 'post'
  })
}