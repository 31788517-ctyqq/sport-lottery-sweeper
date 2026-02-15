/**
 * SP管理API
 */

import request from '@/utils/request'

// ==================== 数据源管理API ====================
// 获取数据源列表
export function getDataSources(params) {
  return request({
    url: '/api/admin/sources',
    method: 'get',
    params
  })
}

// 获取单个数据源
export function getDataSourceById(id) {
  return request({
    url: `/api/admin/sources/${id}`,
    method: 'get'
  })
}

// 创建数据源
export function createDataSource(data) {
  return request({
    url: '/api/admin/sources',
    method: 'post',
    data
  })
}

// 更新数据源
export function updateDataSource(id, data) {
  return request({
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

// 测试数据源连接
export function testDataSource(id) {
  return request({
    url: `/api/admin/sources/${id}/test`,
    method: 'post'
  })
}

// 获取API类型数据源
export function getApiDataSources(params) {
  return request({
    url: '/api/admin/sources/api',
    method: 'get',
    params
  })
}

// 获取文件类型数据源
export function getFileDataSources(params) {
  return request({
    url: '/api/admin/sources/file',
    method: 'get',
    params
  })
}

// ==================== 比赛信息管理API ====================
// 获取比赛列表
export function getMatches(params) {
  return request({
    url: '/api/sp-management/matches',
    method: 'get',
    params
  })
}

// 获取单个比赛
export function getMatchById(id) {
  return request({
    url: `/api/sp-management/matches/${id}`,
    method: 'get'
  })
}

// 创建比赛
export function createMatch(data) {
  return request({
    url: '/api/sp-management/matches',
    method: 'post',
    data
  })
}

// 更新比赛
export function updateMatch(id, data) {
  return request({
    url: `/api/sp-management/matches/${id}`,
    method: 'put',
    data
  })
}

// 删除比赛
export function deleteMatch(id) {
  return request({
    url: `/api/sp-management/matches/${id}`,
    method: 'delete'
  })
}

// 获取比赛SP值历史
export function getMatchSPHistory(matchId) {
  return request({
    url: `/api/sp-management/matches/${matchId}/sp-history`,
    method: 'get'
  })
}

// 获取SP值走势图数据
export function getSPChartData(matchId, companyId) {
  const params = companyId ? { company_id: companyId } : {}
  return request({
    url: `/api/sp-management/matches/${matchId}/sp-chart`,
    method: 'get',
    params
  })
}

// ==================== 赔率公司管理API ====================
// 获取赔率公司列表
export function getOddsCompanies(params) {
  return request({
    url: '/api/sp-management/companies',
    method: 'get',
    params
  })
}

// 获取所有赔率公司
export function getAllOddsCompanies() {
  return request({
    url: '/api/sp-management/companies/all',
    method: 'get'
  })
}

// 获取单个赔率公司
export function getOddsCompanyById(id) {
  return request({
    url: `/api/sp-management/companies/${id}`,
    method: 'get'
  })
}

// 创建赔率公司
export function createOddsCompany(data) {
  return request({
    url: '/api/sp-management/companies',
    method: 'post',
    data
  })
}

// 更新赔率公司
export function updateOddsCompany(id, data) {
  return request({
    url: `/api/sp-management/companies/${id}`,
    method: 'put',
    data
  })
}

// ==================== SP值管理API ====================
// 获取SP值记录
export function getSPRecords(params) {
  return request({
    url: '/api/sp-management/sp-records',
    method: 'get',
    params
  })
}

// 录入SP值
export function createSPRecord(data) {
  return request({
    url: '/api/sp-management/sp-records',
    method: 'post',
    data
  })
}

// 修改SP值
export function updateSPRecord(id, data, reason) {
  const params = reason ? { reason } : {}
  return request({
    url: `/api/sp-management/sp-records/${id}`,
    method: 'put',
    data,
    params
  })
}

// 获取SP值修改日志
export function getSPModificationLogs(recordId) {
  return request({
    url: `/api/sp-management/sp-records/${recordId}/modifications`,
    method: 'get'
  })
}

// 删除SP值记录
export function deleteSPRecord(id) {
  return request({
    url: `/api/sp-management/sp-records/${id}`,
    method: 'delete'
  })
}

// ==================== 文件导入API ====================
// 导入比赛数据
export function importMatchesCSV(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/api/sp-management/matches/import/csv',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 导入SP值数据
export function importSPDataCSV(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/api/sp-management/sp-records/import/csv',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// ==================== 统计分析API ====================
// SP值分布统计
export function getSPDistributionAnalysis(params) {
  return request({
    url: '/api/sp-management/analysis/distribution',
    method: 'get',
    params
  })
}

// SP值变动分析
export function getSPVolatilityAnalysis(params) {
  return request({
    url: '/api/sp-management/analysis/volatility',
    method: 'get',
    params
  })
}

// 赔率公司对比分析
export function getCompanyComparisonAnalysis(matchIds) {
  return request({
    url: '/api/sp-management/analysis/company-comparison',
    method: 'get',
    params: { match_ids: matchIds }
  })
}