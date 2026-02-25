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

// 获取训练任务汇总
export function getTrainingJobsSummary() {
  return request({
    url: '/api/draw-prediction/training-jobs/summary',
    method: 'get'
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

// 获取模型来源追溯信息
export function getModelTrace(modelId) {
  return request({
    url: `/api/draw-prediction/models/${modelId}/trace`,
    method: 'get'
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

// 获取预测汇总
export function getPredictionSummary(params) {
  return request({
    url: '/api/draw-prediction/predictions/summary',
    method: 'get',
    params
  })
}

// 创建再训练草稿
export function createRetrainDraft(data) {
  return request({
    url: '/api/draw-prediction/retrain-drafts',
    method: 'post',
    data
  })
}

// 获取再训练草稿
export function getRetrainDraft(draftId) {
  return request({
    url: `/api/draw-prediction/retrain-drafts/${draftId}`,
    method: 'get'
  })
}

// 提交再训练草稿
export function submitRetrainDraft(draftId) {
  return request({
    url: `/api/draw-prediction/retrain-drafts/${draftId}/submit`,
    method: 'post'
  })
}

// 初始化平局预测模拟数据（保留 data-features 已有数据）
export function bootstrapDrawPredictionMockData() {
  return request({
    url: '/api/draw-prediction/mock/bootstrap',
    method: 'post',
    timeout: 30000
  })
}

// 查询平局预测模拟数据初始化状态
export function getDrawPredictionBootstrapStatus() {
  return request({
    url: '/api/draw-prediction/mock/bootstrap/status',
    method: 'get'
  })
}

// 触发1-1比分预测扫盘
export function fetchPoisson11(params) {
  return request({
    url: '/api/draw-prediction/poisson-11/fetch',
    method: 'post',
    params,
    timeout: 120000
  })
}

// 异步触发1-1比分预测扫盘任务
export function startPoisson11FetchTask(params) {
  return request({
    url: '/api/v1/draw-prediction/poisson-11/fetch-async',
    method: 'post',
    params,
    timeout: 20000
  })
}

// 查询平局预测抓取任务状态
export function getDrawPredictionTask(taskId) {
  return request({
    url: `/api/v1/draw-prediction/tasks/${taskId}`,
    method: 'get',
    timeout: 15000
  })
}

// 获取1-1比分预测扫盘列表
export function getPoisson11List(params) {
  return request({
    url: '/api/v1/draw-prediction/poisson-11/list',
    method: 'get',
    params,
    timeout: 45000
  })
}

// 获取1-1比分预测模型详情
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

// 异步触发AI平局预测扫盘任务
export function startAiDrawFetchTask(params) {
  return request({
    url: '/api/v1/draw-prediction/ai-draw/fetch-async',
    method: 'post',
    params,
    timeout: 20000
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
    params,
    timeout: 60000
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
    },
    timeout: 60000
  })
}
