import request from '@/utils/request'

// 获取IP池列表
export function getIpPoolList(params) {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/ip-pools',  // 由后端路由定义决定
    method: 'get',
    params
  })
}

// 获取IP详情
export function getIpById(id) {
  return request({
    // 修正：使用实际API路径
    url: `/api/admin/ip-pools/${id}`,  // 由后端路由定义决定
    method: 'get'
  })
}

// 创建IP
export function createIp(data) {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/ip-pools',  // 由后端路由定义决定
    method: 'post',
    data
  })
}

// 更新IP
export function updateIp(id, data) {
  return request({
    // 修正：使用实际API路径
    url: `/api/admin/ip-pools/${id}`,  // 由后端路由定义决定
    method: 'put',
    data
  })
}

// 删除IP
export function deleteIp(id) {
  return request({
    // 修正：使用实际API路径
    url: `/api/admin/ip-pools/${id}`,  // 由后端路由定义决定
    method: 'delete'
  })
}

// 批量删除IP
export function batchDeleteIps(data) {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/ip-pools/batch/delete',  // 批量删除
    method: 'post',
    data
  })
}

// 测试IP
export function testIp(id) {
  return request({
    // 修正：使用实际API路径
    url: `/api/admin/ip-pools/${id}/test-connection`,  // 由后端适配器提供
    method: 'post'
  })
}

// 批量测试IP
export function batchTestIps(data) {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/ip-pools/batch/test',  // 批量测试
    method: 'post',
    data
  })
}

// 获取IP统计
export function getIpStats() {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/ip-pools/stats',  // 由后端路由定义决定
    method: 'get'
  })
}

// 导出IP池
export function exportIpPool() {
  return request({
    // 修正：使用实际API路径
    url: '/api/admin/ip-pools/export',
    method: 'get',
    responseType: 'blob'
  })
}
