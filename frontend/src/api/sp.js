// frontend/src/api/sp.js
import request from '@/utils/request'

// ==================== 数据源管理 ====================
export function getDataSourceList(params) {
  return request({
    url: '/admin/sp/data-sources',
    method: 'get',
    params
  })
}

export function createDataSource(data) {
  return request({
    url: '/admin/sp/data-sources',
    method: 'post',
    data
  })
}

export function updateDataSource(id, data) {
  return request({
    url: `/admin/sp/data-sources/${id}`,
    method: 'put',
    data
  })
}

export function deleteDataSource(id) {
  return request({
    url: `/admin/sp/data-sources/${id}`,
    method: 'delete'
  })
}

export function testDataSourceConnection(id) {
  return request({
    url: `/admin/sp/data-sources/${id}/test`,
    method: 'post'
  })
}

// ==================== 比赛信息管理 ====================
export function getMatchList(params) {
  return request({
    url: '/admin/sp/matches',
    method: 'get',
    params
  })
}

export function createMatch(data) {
  return request({
    url: '/admin/sp/matches',
    method: 'post',
    data
  })
}

export function updateMatch(id, data) {
  return request({
    url: `/admin/sp/matches/${id}`,
    method: 'put',
    data
  })
}

export function deleteMatch(id) {
  return request({
    url: `/admin/sp/matches/${id}`,
    method: 'delete'
  })
}

// 批量导入比赛（CSV）
export function batchImportMatches(formData) {
  // 后端路径：/matches/import/csv，注册到 /admin/sp 前缀
  return request({
    url: '/admin/sp/matches/import/csv',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取某场比赛的 SP 历史记录
export function getMatchSPHistory(matchId, params) {
  return request({
    url: `/admin/sp/matches/${matchId}/sp-history`,
    method: 'get',
    params
  })
}

// 获取某场比赛的 SP 记录（别名，用于兼容 MatchManagement.vue 组件）
export function getMatchSPRecords(matchId, params) {
  return request({
    url: `/admin/sp/matches/${matchId}/sp-history`,
    method: 'get',
    params
  })
}

// ==================== SP值管理 ====================
export function getSPRecordList(params) {
  return request({
    url: '/admin/sp/records',
    method: 'get',
    params
  })
}

export function createSPRecord(data) {
  return request({
    url: '/admin/sp/records',
    method: 'post',
    data
  })
}

export function updateSPRecord(id, data) {
  return request({
    url: `/admin/sp/records/${id}`,
    method: 'put',
    data
  })
}

export function deleteSPRecord(id) {
  return request({
    url: `/admin/sp/records/${id}`,
    method: 'delete'
  })
}

// SP 走势图表数据
export function getSPRecordTrend(matchId, params) {
  // 后端路径：/matches/{match_id}/sp-chart
  return request({
    url: `/admin/sp/matches/${matchId}/sp-chart`,
    method: 'get',
    params
  })
}

// ==================== 数据分析与洞察 ====================
export function getSPDistributionAnalysis(params) {
  return request({
    url: '/admin/sp/analysis/distribution',
    method: 'get',
    params
  })
}

// 变动分析（波动率）
export function getSPMovementAnalysis(params) {
  return request({
    url: '/admin/sp/analysis/volatility',
    method: 'get',
    params
  })
}

// 公司对比分析
export function getCompanyComparisonAnalysis(params) {
  return request({
    url: '/admin/sp/analysis/company-comparison',
    method: 'get',
    params
  })
}

// SP值与赛果关联分析（后端暂未实现）
export function getSPResultCorrelationAnalysis(params) {
  // TODO: 后端暂无此接口，需后续补充
  return request({
    url: '/admin/sp/analysis/correlation',
    method: 'get',
    params
  })
}