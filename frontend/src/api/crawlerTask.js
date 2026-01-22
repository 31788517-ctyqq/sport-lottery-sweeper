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

// 立即触发任务
export function triggerTask(id) {
  return request({
    url: `/api/admin/crawler/tasks/${id}/trigger`,
    method: 'post'
  })
}

// 获取任务执行日志
export function getLogs(id, params) {
  return request({
    url: `/api/admin/crawler/tasks/${id}/logs`,
    method: 'get',
    params
  })
}

// 获取Cron表达式说明
export function getCronHelp() {
  return request({
    url: '/api/admin/crawler/tasks/cron-help',
    method: 'get'
  })
}