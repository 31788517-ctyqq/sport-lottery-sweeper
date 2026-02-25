/**
 * 平局预测管理API
 */
import request from '@/utils/request'

// 获取平局预测特征列表
export function getDrawFeatures(params) {
  return request({
    url: '/api/draw-prediction/features',
    method: 'get',
    params
  })
}

// 创建平局预测特征
export function createDrawFeature(data) {
  return request({
    url: '/api/draw-prediction/features',
    method: 'post',
    data
  })
}

// 更新平局预测特征
export function updateDrawFeature(id, data) {
  return request({
    url: `/api/draw-prediction/features/${id}`,
    method: 'put',
    data
  })
}

// 删除平局预测特征
export function deleteDrawFeature(id) {
  return request({
    url: `/api/draw-prediction/features/${id}`,
    method: 'delete'
  })
}

// 获取训练任务列表
export function getTrainingJobs(params) {
  return request({
    url: '/api/draw-prediction/training-jobs',
    method: 'get',
    params
  })
}

// 创建训练任务
export function createTrainingJob(data) {
  return request({
    url: '/api/draw-prediction/training-jobs',
    method: 'post',
    data
  })
}

// 获取训练任务日志
export function getTrainingJobLogs(jobId) {
  return request({
    url: `/api/draw-prediction/training-jobs/${jobId}/logs`,
    method: 'get'
  })
}

// 更新训练任务状态
export function updateTrainingJobStatus(jobId, data) {
  return request({
    url: `/api/draw-prediction/training-jobs/${jobId}/status`,
    method: 'put',
    data
  })
}

// 获取模型版本列表
export function getModelVersions(params) {
  return request({
    url: '/api/draw-prediction/models',
    method: 'get',
    params
  })
}

// 部署模型版本
export function deployModelVersion(modelId) {
  return request({
    url: `/api/draw-prediction/models/${modelId}/deploy`,
    method: 'post'
  })
}

// 回滚模型版本
export function rollbackModelVersion(modelId) {
  return request({
    url: `/api/draw-prediction/models/${modelId}/rollback`,
    method: 'post'
  })
}

// 获取预测结果列表
export function getPredictions(params) {
  return request({
    url: '/api/draw-prediction/predictions',
    method: 'get',
    params
  })
}

// 触发专抓1-1扫盘
export function fetchPoisson11(params) {
  return request({
    url: '/api/draw-prediction/poisson-11/fetch',
    method: 'post',
    params
  })
}

// 获取专抓1-1扫盘列表
export function getPoisson11List(params) {
  return request({
    url: '/api/v1/draw-prediction/poisson-11/list',
    method: 'get',
    params
  })
}

// 获取专抓1-1模型详情
export function getPoisson11Detail(matchId, params) {
  return request({
    url: `/api/v1/draw-prediction/poisson-11/detail/${matchId}`,
    method: 'get',
    params
  })
}

// 获取AI平局预测计算规则
export function getAiDrawRules() {
  return request({
    url: '/api/v1/draw-prediction/ai-draw/rules',
    method: 'get'
  })
}

// 保存AI平局预测计算规则
export function saveAiDrawRules(rules) {
  return request({
    url: '/api/v1/draw-prediction/ai-draw/rules',
    method: 'put',
    data: { rules }
  })
}

// 获取单场优化规则
export function getAiDrawMatchRules(matchId) {
  return request({
    url: `/api/v1/draw-prediction/ai-draw/rules/${matchId}`,
    method: 'get'
  })
}

// 保存单场优化规则
export function saveAiDrawMatchRules(matchId, rules) {
  return request({
    url: `/api/v1/draw-prediction/ai-draw/rules/${matchId}`,
    method: 'put',
    data: { rules }
  })
}

// 获取单场A/B/C/D修正值
export function getAiDrawMatchOverrides(matchId) {
  return request({
    url: `/api/v1/draw-prediction/ai-draw/overrides/${matchId}`,
    method: 'get'
  })
}

// 保存单场A/B/C/D修正值
export function saveAiDrawMatchOverrides(matchId, overrides) {
  return request({
    url: `/api/v1/draw-prediction/ai-draw/overrides/${matchId}`,
    method: 'put',
    data: { overrides }
  })
}

// 触发AI平局预测扫盘
export function fetchAiDraw(params) {
  return request({
    url: '/api/v1/draw-prediction/ai-draw/fetch',
    method: 'post',
    params
  })
}

// 获取AI平局预测扫盘列表
export function getAiDrawList(params) {
  return request({
    url: '/api/v1/draw-prediction/ai-draw/list',
    method: 'get',
    params
  })
}

// 获取AI平局预测模型详情
export function getAiDrawDetail(matchId) {
  return request({
    url: `/api/v1/draw-prediction/ai-draw/detail/${matchId}`,
    method: 'get'
  })
}

// 触发盈球北单赛程导入
export function importYingqiuBdSchedule(params) {
  return request({
    url: '/api/v1/admin/lottery-schedules/import/yingqiu-bd',
    method: 'post',
    params,
    timeout: 120000
  })
}

// 获取北单期号选项
export function getBdIssueOptions(params) {
  return request({
    url: '/api/v1/admin/lottery-schedules/issue-options',
    method: 'get',
    params
  })
}

// 获取北单赛事选项（按日期/期号）
export function getBdLeagueOptions(params) {
  return request({
    url: '/api/v1/admin/lottery-schedules/league-options',
    method: 'get',
    params: {
      schedule_type: 'bd',
      ...(params || {})
    }
  })
}
