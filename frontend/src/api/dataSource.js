import request from '@/utils/request'

// 获取数据源列表
export function listDataSources(params) {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/sources',
    method: 'get',
    params
  })
}

// 创建数据源
export function createDataSource(data) {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/sources',
    method: 'post',
    data
  })
}

// 更新数据源
export function updateDataSource(id, data) {
  return request({
    // 修正：使用实际API路径
    url: `/api/admin/sources/${id}`,
    method: 'put',
    data
  })
}

// 删除数据源
export function deleteDataSource(id) {
  return request({
    url: `/api/admin/sources/${id}`,
    method: 'delete'
  })
}

// 获取数据源详情
export function getDataSource(id) {
  return request({
    url: `/api/admin/sources/${id}`,
    method: 'get'
  })
}

// 测试数据源连接
export function testConnection(id) {
  return request({
    url: `/api/admin/sources/${id}/health`,
    method: 'post'
  })
}

// 获取数据源类型列表
export function getDataSourceTypes() {
  return request({
    url: '/api/admin/sources/types',
    method: 'get'
  })
}