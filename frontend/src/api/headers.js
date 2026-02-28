import request from '@/utils/request'

// 获取请求头列表
export function getHeadersList(params) {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/headers',
    method: 'get',
    params
  })
}

// 获取请求头详情
export function getHeaderById(id) {
  return request({
    // 修正：使用实际API路径
    url: `/api/admin/headers/${id}`,
    method: 'get'
  })
}

// 创建请求头
export function createHeader(data) {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/headers',
    method: 'post',
    data
  })
}

// 更新请求头
export function updateHeader(id, data) {
  return request({
    // 修正：使用实际API路径
    url: `/api/admin/headers/${id}`,
    method: 'put',
    data
  })
}

// 删除请求头
export function deleteHeader(id) {
  return request({
    // 修正：使用实际API路径
    url: `/api/admin/headers/${id}`,
    method: 'delete'
  })
}

// 批量删除请求头
export function batchDeleteHeaders(data) {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/headers/batch',
    method: 'post',
    data
  })
}

// 测试请求头
export function testHeader(id) {
  return request({
    // 修正：使用实际API路径
    url: `/api/admin/headers/${id}/test`,
    method: 'post'
  })
}

// 批量测试请求头
export function batchTestHeaders(data) {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/headers/batch/test',
    method: 'post',
    data
  })
}

// 获取请求头统计
export function getHeaderStats() {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/headers/stats',
    method: 'get'
  })
}

// 导出请求头
export function exportHeaders() {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/headers/export',
    method: 'get'
  })
}

// 导入请求头
export function importHeaders(data) {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/headers/import',
    method: 'post',
    data
  })
}
// ������ͷ������Դ
export function bindHeadersToDataSource(data) {
  return request({
    url: '/api/admin/headers/bind/data-source',
    method: 'post',
    data
  })
}

// ������ͷ������
export function bindHeadersToTask(data) {
  return request({
    url: '/api/admin/headers/bind/task',
    method: 'post',
    data
  })
}

// ��ѯ�󶨹�ϵ
export function getHeaderBindings(params) {
  return request({
    url: '/api/admin/headers/bindings',
    method: 'get',
    params
  })
}

// �������Դ��
export function unbindHeadersFromDataSource(data) {
  return request({
    url: '/api/admin/headers/bind/data-source/remove',
    method: 'post',
    data
  })
}

// ��������
export function unbindHeadersFromTask(data) {
  return request({
    url: '/api/admin/headers/bind/task/remove',
    method: 'post',
    data
  })
}

export function autoBindHeadersToDataSource(data) {
  return request({
    url: '/api/admin/headers/auto-bind/data-source',
    method: 'post',
    data
  })
}
