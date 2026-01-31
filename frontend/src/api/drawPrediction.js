/**
 * 平局预测管理API
 */
import request from '@/utils/request'

// 获取平局预测特征列表
export function getDrawFeatures(params) {
  return request({
    url: '/v1/draw-prediction/features',
    method: 'get',
    params
  })
}

// 创建平局预测特征
export function createDrawFeature(data) {
  return request({
    url: '/v1/draw-prediction/features',
    method: 'post',
    data
  })
}

// 更新平局预测特征
export function updateDrawFeature(id, data) {
  return request({
    url: `/v1/draw-prediction/features/${id}`,
    method: 'put',
    data
  })
}

// 删除平局预测特征
export function deleteDrawFeature(id) {
  return request({
    url: `/v1/draw-prediction/features/${id}`,
    method: 'delete'
  })
}

// 获取训练任务列表
export function getTrainingJobs(params) {
  return request({
    url: '/v1/draw-prediction/training-jobs',
    method: 'get',
    params
  })
}

// 创建训练任务
export function createTrainingJob(data) {
  return request({
    url: '/v1/draw-prediction/training-jobs',
    method: 'post',
    data
  })
}

// 获取训练任务日志
export function getTrainingJobLogs(jobId) {
  return request({
    url: `/v1/draw-prediction/training-jobs/${jobId}/logs`,
    method: 'get'
  })
}

// 更新训练任务状态
export function updateTrainingJobStatus(jobId, data) {
  return request({
    url: `/v1/draw-prediction/training-jobs/${jobId}/status`,
    method: 'put',
    data
  })
}

// 获取模型版本列表
export function getModelVersions(params) {
  return request({
    url: '/v1/draw-prediction/models',
    method: 'get',
    params
  })
}

// 部署模型版本
export function deployModelVersion(modelId) {
  return request({
    url: `/v1/draw-prediction/models/${modelId}/deploy`,
    method: 'post'
  })
}

// 回滚模型版本
export function rollbackModelVersion(modelId) {
  return request({
    url: `/v1/draw-prediction/models/${modelId}/rollback`,
    method: 'post'
  })
}

// 获取预测结果列表
export function getPredictions(params) {
  return request({
    url: '/v1/draw-prediction/predictions',
    method: 'get',
    params
  })
}