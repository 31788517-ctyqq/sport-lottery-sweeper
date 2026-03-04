import request from '@/utils/request'

// 获取爬虫智能统计
export function getIntelligenceStats(params) {
  return request({
    // 修正：使用新版API路径
    url: '/api/admin/crawler/intelligence/stats',
    method: 'get',
    params
  })
}

// 获取爬虫智能数据
export function getIntelligenceData(params) {
  return request({
    // 修正：使用新版API路径
    url: '/api/admin/crawler/intelligence/data',
    method: 'get',
    params
  })
}

// 导出爬虫智能数据
export function exportIntelligenceData(params) {
  return request({
    // 修正：使用新版API路径
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
export const markAsInvalid = markInvalid // 保留旧名兼容

// 标记数据为无效
export function markInvalid(id) {
  return request({
    // 修正：使用新版API路径
    url: `/api/admin/crawler/intelligence/${id}/mark-invalid`,
    method: 'post'
  })
}

// 重新抓取指定数据
export function recrawlData(id) {
  return request({
    // 修正：使用新版API路径
    url: `/api/admin/crawler/intelligence/${id}/recrawl`,
    method: 'post'
  })
}

// 批量标记数据
export function batchMarkData(ids, status) {
  return request({
    // 修正：使用新版API路径
    url: '/api/admin/crawler/intelligence/batch-mark',
    method: 'put',
    data: { ids, status }
  })
}

// 获取趋势分析数据
export function getTrendAnalysis(params) {
  return request({
    // 修正：使用新版API路径
    url: '/api/admin/crawler/intelligence/trend',
    method: 'get',
    params
  })
}