/**
 * LLM供应商管理API
 */
import request from '@/utils/request'

/**
 * 获取LLM供应商列表
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export function getLLMProviders(params = {}) {
  // 使用相对路径确保通过Vite代理，添加尾部斜杠避免重定向
  return request({
    url: '/api/llm-providers/',
    method: 'get',
    params
  })
}

/**
 * 获取LLM供应商数量
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export function getLLMProvidersCount(params = {}) {
  // 使用相对路径确保通过Vite代理  
  return request({
    url: '/api/llm-providers/count',
    method: 'get',
    params
  })
}

/**
 * 获取LLM供应商详情
 * @param {number} providerId - 供应商ID
 * @returns {Promise} API响应
 */
export function getLLMProvider(providerId) {
  return request({
    url: `/api/llm-providers/${providerId}`,
    method: 'get'
  })
}

/**
 * 创建LLM供应商
 * @param {Object} data - 供应商数据
 * @returns {Promise} API响应
 */
export function createLLMProvider(data) {
  return request({
    url: '/api/llm-providers/',
    method: 'post',
    data
  })
}

/**
 * 更新LLM供应商
 * @param {number} providerId - 供应商ID
 * @param {Object} data - 更新数据
 * @returns {Promise} API响应
 */
export function updateLLMProvider(providerId, data) {
  return request({
    url: `/api/llm-providers/${providerId}`,
    method: 'put',
    data
  })
}

/**
 * 删除LLM供应商
 * @param {number} providerId - 供应商ID
 * @returns {Promise} API响应
 */
export function deleteLLMProvider(providerId) {
  return request({
    url: `/api/llm-providers/${providerId}`,
    method: 'delete'
  })
}

/**
 * 启用LLM供应商
 * @param {number} providerId - 供应商ID
 * @returns {Promise} API响应
 */
export function enableLLMProvider(providerId) {
  return request({
    url: `/api/llm-providers/${providerId}/enable`,
    method: 'post'
  })
}

/**
 * 禁用LLM供应商
 * @param {number} providerId - 供应商ID
 * @returns {Promise} API响应
 */
export function disableLLMProvider(providerId) {
  return request({
    url: `/api/llm-providers/${providerId}/disable`,
    method: 'post'
  })
}

/**
 * 测试LLM供应商连接
 * @param {number} providerId - 供应商ID
 * @param {Object} testData - 测试数据
 * @returns {Promise} API响应
 */
export function testLLMProviderConnection(providerId, testData = {}) {
  return request({
    url: `/api/llm-providers/${providerId}/test`,
    method: 'post',
    data: testData
  })
}

/**
 * 获取LLM供应商统计概览
 * @returns {Promise} API响应
 */
export function getLLMProvidersStats() {
  return request({
    url: '/api/llm-providers/stats/overview',
    method: 'get'
  })
}

/**
 * 获取可用的LLM供应商列表
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export function getAvailableLLMProviders(params = {}) {
  return request({
    url: '/api/llm-providers/available/list',
    method: 'get',
    params
  })
}

/**
 * 批量更新LLM供应商状态
 * @param {Object} data - 批量操作数据
 * @returns {Promise} API响应
 */
export function batchUpdateLLMProvidersStatus(data) {
  return request({
    url: '/api/llm-providers/batch/update-status',
    method: 'post',
    data
  })
}

/**
 * 增加LLM供应商使用成本
 * @param {number} providerId - 供应商ID
 * @param {number} costCents - 成本（分）
 * @returns {Promise} API响应
 */
export function incrementLLMProviderCost(providerId, costCents) {
  return request({
    url: `/api/llm-providers/${providerId}/increment-cost`,
    method: 'post',
    data: { cost_cents: costCents }
  })
}