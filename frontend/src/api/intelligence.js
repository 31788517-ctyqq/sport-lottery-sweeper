import request from '@/utils/request'

// 获取智能分析记录列表
export function getIntelligenceList(params) {
  return request({
    url: '/api/admin/intelligence',
    method: 'get',
    params
  })
}

// 新增分析记录
export function createIntelligence(data) {
  return request({
    url: '/api/admin/intelligence',
    method: 'post',
    data
  })
}

// 删除分析记录
export function deleteIntelligence(id) {
  return request({
    url: `/api/admin/intelligence/${id}`,
    method: 'delete'
  })
}
