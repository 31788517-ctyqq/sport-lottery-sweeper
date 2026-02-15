import request from '@/utils/request'

// 获取任务列表
export function listTasks(params) {
  return request({
    url: '/api/admin/crawler/tasks',
    method: 'get',
    params
  })
}

// 创建任务
export function createTask(data) {
  return request({
    url: '/api/admin/crawler/tasks',
    method: 'post',
    data
  })
}

// 更新任务
export function updateTask(id, data) {
  return request({
    url: `/api/admin/crawler/tasks/${id}`,
    method: 'put',
    data
  })
}

// 删除任务
export function deleteTask(id) {
  return request({
    url: `/api/admin/crawler/tasks/${id}`,
    method: 'delete'
  })
}

// 触发任务
export function triggerTask(id) {
  return request({
    url: `/api/admin/crawler/tasks/${id}/trigger`,
    method: 'post'
  })
}

// 停止任务
export function stopTask(id) {
  return request({
    // 与后端稳定路由对齐：/api/v1/admin/tasks/{id}/stop
    // 前端经 Vite 代理后使用 /api/admin/tasks/{id}/stop
    url: `/api/admin/tasks/${id}/stop`,
    method: 'post'
  })
}

// 获取任务详情
export function getTask(id) {
  return request({
    url: `/api/admin/crawler/tasks/${id}`,
    method: 'get'
  })
}

// 获取任务日志
export function getTaskLogs(id, params) {
  return request({
    url: `/api/admin/crawler/tasks/${id}/logs`,
    method: 'get',
    params
  })
}

// 获取cron表达式帮助
export function getCronHelp() {
  return request({
    url: '/api/admin/crawler/tasks/cron-help',
    method: 'get'
  })
}

// 批量删除任务
export function batchDeleteTasks(ids) {
  return request({
    url: '/api/admin/crawler/tasks/batch-delete',
    method: 'post',
    data: { ids }
  })
}

// 获取任务统计信息
export function getTaskStatistics() {
  return request({
    url: '/api/admin/crawler/tasks/statistics',
    method: 'get'
  })
}

// 执行500彩票网爬虫任务
export function executeFiveHundredCrawl(days = 3) {
  return request({
    url: '/api/admin/crawler/tasks/execute-five-hundred-crawl',
    method: 'post',
    params: { days }
  })
}

// 创建500彩票网数据源
export function createFiveHundredDataSource() {
  return request({
    url: '/api/admin/sources/five-hundred-create',
    method: 'post'
  })
}

// 获取任务日志（别名）
export function getLogs(id, params) {
  return getTaskLogs(id, params);
}
