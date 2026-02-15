import request from '@/utils/request'

// 获取智能分析记录列表
export function getIntelligenceList(params) {
  return request({
    url: '/api/intelligence',
    method: 'get',
    params
  })
}

// 新增分析记录
export function createIntelligence(data) {
  return request({
    url: '/api/intelligence',
    method: 'post',
    data
  })
}

// 删除分析记录
export function deleteIntelligence(id) {
  return request({
    url: `/api/intelligence/${id}`,
    method: 'delete'
  })
}

// 获取情报统计信息
export function getIntelligenceStats(params) {
  return request({
    url: '/api/intelligence/stats',
    method: 'get',
    params
  })
}

// 更新情报记录
export function updateIntelligence(id, data) {
  return request({
    url: `/api/intelligence/${id}`,
    method: 'put',
    data
  })
}

// 获取情报类型列表
export function getIntelligenceTypes() {
  return request({
    url: '/api/intelligence/types',
    method: 'get'
  })
}

// 获取情报来源列表
export function getIntelligenceSources() {
  return request({
    url: '/api/intelligence/sources',
    method: 'get'
  })
}