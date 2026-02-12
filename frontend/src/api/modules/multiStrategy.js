/**
 * 多策略筛选API模块
 */

import request from '@/utils/request'

/**
 * 获取多策略功能信息
 */
export function getMultiStrategyInfo() {
  return request({
    url: '/api/v1/multi-strategy/',
    method: 'get'
  })
}

/**
 * 获取可用策略列表
 */
export function getAvailableStrategies() {
  return request({
    url: '/api/v1/multi-strategy/strategies',
    method: 'get'
  })
}

/**
 * 执行多策略筛选
 */
export function executeMultiStrategy(data) {
  return request({
    url: '/api/v1/multi-strategy/execute',
    method: 'post',
    data
  })
}

/**
 * 启动/停止定时任务
 */
export function toggleTask(data) {
  return request({
    url: '/api/v1/multi-strategy/toggle-task',
    method: 'post',
    data
  })
}