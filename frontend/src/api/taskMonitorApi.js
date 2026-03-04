// AI_WORKING: coder1 @2026-02-04 - 创建任务监控API模块
import request from '@/utils/request'

// 获取任务执行列表
export function getExecutions(params) {
  return request({
    url: '/api/v1/task-monitor/executions',
    method: 'get',
    params
  })
}

// 获取单个执行详情
export function getExecutionDetail(executionId) {
  return request({
    url: `/api/v1/task-monitor/executions/${executionId}`,
    method: 'get'
  })
}

// 取消正在执行的任务
export function cancelExecution(executionId) {
  return request({
    url: `/api/v1/task-monitor/executions/${executionId}/cancel`,
    method: 'post'
  })
}

// 获取任务执行日志
export function getExecutionLogs(executionId, params) {
  return request({
    url: `/api/v1/task-monitor/executions/${executionId}/logs`,
    method: 'get',
    params
  })
}

// 获取每日统计
export function getDailyStatistics(params) {
  return request({
    url: '/api/v1/task-monitor/statistics/daily',
    method: 'get',
    params
  })
}

// 获取主要问题排行
export function getTopIssues(params) {
  return request({
    url: '/api/v1/task-monitor/statistics/top-issues',
    method: 'get',
    params
  })
}

// 获取实时概览
export function getRealtimeOverview() {
  return request({
    url: '/api/v1/task-monitor/realtime/overview',
    method: 'get'
  })
}

// 兼容前端页面导入的别名
export const fetchExecutions = getExecutions
export const fetchExecutionDetail = getExecutionDetail
export const fetchExecutionLogs = getExecutionLogs

// 默认导出对象，方便导入
export default {
  getExecutions,
  getExecutionDetail,
  cancelExecution,
  getExecutionLogs,
  getDailyStatistics,
  getTopIssues,
  getRealtimeOverview,
  fetchExecutions,
  fetchExecutionDetail,
  fetchExecutionLogs
}

// AI_DONE: coder1 @2026-02-04
