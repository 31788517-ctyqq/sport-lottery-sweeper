import request from '@/utils/request'

// 获取数据源列表
export function getSources(params) {
  // 只传递后端支持的参数，并确保类型正确
  const filteredParams = {
    page: params.page || 1,
    size: params.size || 20,
    // 传递分类参数（后端现在支持category参数）
    type: params.type || undefined,
    category: params.category || undefined,
    // 将前端的search映射到后端的search
    search: params.search || params.name || undefined,
    // status参数需要特殊处理，只在有有效值时传递，且确保是布尔类型
    status: (params.status === true || params.status === false) ? params.status : undefined,
    // 源ID参数
    source_id: params.sourceId || undefined
  }
  
  return request({
    url: '/api/v1/admin/sources',
    method: 'get',
    params: filteredParams
  })
}

// 获取单个数据源详情
export function getSource(id) {
  return request({
    url: `/api/v1/admin/sources/${id}`,
    method: 'get'
  })
}

// 创建数据源
export function createSource(data) {
  return request({
    url: '/api/v1/admin/sources',
    method: 'post',
    data
  })
}

// 更新数据源
export function updateSource(id, data) {
  return request({
    url: `/api/v1/admin/sources/${id}`,
    method: 'put',
    data
  })
}

// 删除数据源
export function deleteSource(id) {
  return request({
    url: `/api/v1/admin/sources/${id}`,
    method: 'delete'
  })
}

// 批量删除数据源
export function batchDeleteSources(ids) {
  return request({
    url: '/api/v1/admin/sources/batch',
    method: 'delete',
    data: { ids }
  })
}

// 健康检查
export function healthCheck(id) {
  return request({
    url: `/api/v1/admin/sources/${id}/health`,
    method: 'get'
  })
}

// 批量健康检查
export function batchHealthCheck(ids) {
  return request({
    url: '/api/v1/admin/sources/batch/health',
    method: 'post',
    data: { ids }
  })
}

// 更新数据源状态
export function updateStatus(id, data) {
  return request({
    url: `/api/v1/admin/sources/${id}/status`,
    method: 'put',
    data
  })
}

// 批量启用数据源
export function batchEnableSource(ids) {
  return request({
    url: '/api/v1/admin/sources/batch/enable',
    method: 'put',
    data: { ids }
  })
}

// 批量停用数据源
export function batchDisableSource(ids) {
  return request({
    url: '/api/v1/admin/sources/batch/disable',
    method: 'put',
    data: { ids }
  })
}

// 批量测试数据源
export function batchTestSources(ids) {
  return request({
    url: '/api/v1/admin/sources/batch/test',
    method: 'post',
    data: { ids }
  })
}

// 导出数据源报告
export function exportSourceReport(params) {
  return request({
    url: '/api/v1/admin/sources/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

// 获取数据源分类选项
export function getSourceCategories() {
  return request({
    url: '/api/v1/admin/sources/categories',
    method: 'get'
  })
}