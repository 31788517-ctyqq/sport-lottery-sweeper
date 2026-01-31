import request from '@/utils/request'

// 获取数据源列表
export function getSources(params) {
  return request({
    url: '/api/admin/v1/sources',
    method: 'get',
    params
  })
}

// 获取单个数据源详情
export function getSource(id) {
  return request({
    url: `/api/admin/v1/sources/${id}`,
    method: 'get'
  })
}

// 创建数据源
export function createSource(data) {
  return request({
    url: '/api/admin/v1/sources',
    method: 'post',
    data
  })
}

// 更新数据源
export function updateSource(id, data) {
  return request({
    url: `/api/admin/v1/sources/${id}`,
    method: 'put',
    data
  })
}

// 删除数据源
export function deleteSource(id) {
  return request({
    url: `/api/admin/v1/sources/${id}`,
    method: 'delete'
  })
}

// 批量删除数据源
export function batchDeleteSources(ids) {
  return request({
    url: '/api/admin/v1/sources/batch',
    method: 'delete',
    data: { ids }
  })
}

// 健康检查
export function healthCheck(id) {
  return request({
    url: `/api/admin/crawler/sources/${id}/health`,
    method: 'get'
  })
}

// 批量健康检查
export function batchHealthCheck(ids) {
  return request({
    url: '/api/admin/crawler/sources/batch/health',
    method: 'post',
    data: { ids }
  })
}

// 更新数据源状态
export function updateStatus(id, data) {
  return request({
    url: `/api/admin/v1/sources/${id}/status`,
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

// 获取数据源分类选项
export function getSourceCategories() {
  return request({
    url: '/api/admin/crawler/sources/categories',
    method: 'get'
  })
}