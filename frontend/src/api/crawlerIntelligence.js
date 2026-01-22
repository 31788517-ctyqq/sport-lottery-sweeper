import request from '@/utils/request'

// 获取数据情报统计
export function getIntelligenceStats(params) {
  return request({
    url: '/api/admin/crawler/intelligence/stats',
    method: 'get',
    params
  })
}

// 获取数据情报列表
export function getIntelligenceData(params) {
  return request({
    url: '/api/admin/crawler/intelligence/data',
    method: 'get',
    params
  })
}

// 导出数据情报
export function exportIntelligenceData(params) {
  return request({
    url: '/api/admin/crawler/intelligence/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

// 兼容前端页面导入的别名
export const getStats = getIntelligenceStats
export const getData = getIntelligenceData
export const exportData = exportIntelligenceData

// 标记数据为无效
export function markAsInvalid(id) {
  return request({
    url: `/api/admin/crawler/intelligence/${id}/mark-invalid`,
    method: 'put'
  })
}

// 重新抓取指定数据
export function recrawlData(id) {
  return request({
    url: `/api/admin/crawler/intelligence/${id}/recrawl`,
    method: 'post'
  })
}

// 批量标记数据
export function batchMarkData(ids, status) {
  return request({
    url: '/api/admin/crawler/intelligence/batch-mark',
    method: 'put',
    data: { ids, status }
  })
}

// 获取趋势分析数据
export function getTrendAnalysis(params) {
  return request({
    url: '/api/admin/crawler/intelligence/trend',
    method: 'get',
    params
  })
}