import request from '@/utils/request'

// 获取数据源列表
export function listSources(params) {
  return request({
    url: '/api/admin/crawler/sources',
    method: 'get',
    params
  })
}

// 健康检查
export function healthCheck(id) {
  return request({
    url: `/api/admin/crawler/sources/${id}/health`,
    method: 'get'
  })
}

// 更新数据源状态
export function updateStatus(id, data) {
  return request({
    url: `/api/admin/crawler/sources/${id}/status`,
    method: 'put',
    data
  })
}

// 批量启用数据源
export function batchEnableSource(ids) {
  return request({
    url: '/api/admin/crawler/sources/batch/enable',
    method: 'put',
    data: { ids }
  })
}

// 批量停用数据源
export function batchDisableSource(ids) {
  return request({
    url: '/api/admin/crawler/sources/batch/disable',
    method: 'put',
    data: { ids }
  })
}

// 批量测试数据源
export function batchTestSources(ids) {
  return request({
    url: '/api/admin/crawler/sources/batch/test',
    method: 'post',
    data: { ids }
  })
}

// 导出数据源报告
export function exportSourceReport(params) {
  return request({
    url: '/api/admin/crawler/sources/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}