/**
 * LLM渚涘簲鍟嗙鐞咥PI
 */
import request from '@/utils/request'

/**
 * 鑾峰彇LLM渚涘簲鍟嗗垪琛? * @param {Object} params - 鏌ヨ鍙傛暟
 * @returns {Promise} API鍝嶅簲
 */
export function getLLMProviders(params = {}) {
  // 浣跨敤鐩稿璺緞纭繚閫氳繃Vite浠ｇ悊锛屾坊鍔犲熬閮ㄦ枩鏉犻伩鍏嶉噸瀹氬悜
  return request({
    url: '/api/v1/llm-providers/',
    method: 'get',
    params
  })
}

/**
 * 鑾峰彇LLM渚涘簲鍟嗘暟閲? * @param {Object} params - 鏌ヨ鍙傛暟
 * @returns {Promise} API鍝嶅簲
 */
export function getLLMProvidersCount(params = {}) {
  // 浣跨敤鐩稿璺緞纭繚閫氳繃Vite浠ｇ悊  
  return request({
    url: '/api/v1/llm-providers/count',
    method: 'get',
    params
  })
}

/**
 * 鑾峰彇LLM渚涘簲鍟嗚鎯? * @param {number} providerId - 渚涘簲鍟咺D
 * @returns {Promise} API鍝嶅簲
 */
export function getLLMProvider(providerId) {
  return request({
    url: `/api/v1/llm-providers/${providerId}`,
    method: 'get'
  })
}

/**
 * 鍒涘缓LLM渚涘簲鍟? * @param {Object} data - 渚涘簲鍟嗘暟鎹? * @returns {Promise} API鍝嶅簲
 */
export function createLLMProvider(data) {
  return request({
    url: '/api/v1/llm-providers/',
    method: 'post',
    data
  })
}

/**
 * 鏇存柊LLM渚涘簲鍟? * @param {number} providerId - 渚涘簲鍟咺D
 * @param {Object} data - 鏇存柊鏁版嵁
 * @returns {Promise} API鍝嶅簲
 */
export function updateLLMProvider(providerId, data) {
  return request({
    url: `/api/v1/llm-providers/${providerId}`,
    method: 'put',
    data
  })
}

/**
 * 鍒犻櫎LLM渚涘簲鍟? * @param {number} providerId - 渚涘簲鍟咺D
 * @returns {Promise} API鍝嶅簲
 */
export function deleteLLMProvider(providerId) {
  return request({
    url: `/api/v1/llm-providers/${providerId}`,
    method: 'delete'
  })
}

/**
 * 鍚敤LLM渚涘簲鍟? * @param {number} providerId - 渚涘簲鍟咺D
 * @returns {Promise} API鍝嶅簲
 */
export function enableLLMProvider(providerId) {
  return request({
    url: `/api/v1/llm-providers/${providerId}/enable`,
    method: 'post'
  })
}

/**
 * 绂佺敤LLM渚涘簲鍟? * @param {number} providerId - 渚涘簲鍟咺D
 * @returns {Promise} API鍝嶅簲
 */
export function disableLLMProvider(providerId) {
  return request({
    url: `/api/v1/llm-providers/${providerId}/disable`,
    method: 'post'
  })
}

/**
 * 娴嬭瘯LLM渚涘簲鍟嗚繛鎺? * @param {number} providerId - 渚涘簲鍟咺D
 * @param {Object} testData - 娴嬭瘯鏁版嵁
 * @returns {Promise} API鍝嶅簲
 */
export function testLLMProviderConnection(providerId, testData = {}) {
  return request({
    url: `/api/v1/llm-providers/${providerId}/test`,
    method: 'post',
    data: testData
  })
}

/**
 * 鑾峰彇LLM渚涘簲鍟嗙粺璁℃瑙? * @returns {Promise} API鍝嶅簲
 */
export function getLLMProvidersStats() {
  return request({
    url: '/api/v1/llm-providers/stats/overview',
    method: 'get'
  })
}

/**
 * 鑾峰彇鍙敤鐨凩LM渚涘簲鍟嗗垪琛? * @param {Object} params - 鏌ヨ鍙傛暟
 * @returns {Promise} API鍝嶅簲
 */
export function getAvailableLLMProviders(params = {}) {
  return request({
    url: '/api/v1/llm-providers/available/list',
    method: 'get',
    params
  })
}

/**
 * 鎵归噺鏇存柊LLM渚涘簲鍟嗙姸鎬? * @param {Object} data - 鎵归噺鎿嶄綔鏁版嵁
 * @returns {Promise} API鍝嶅簲
 */
export function batchUpdateLLMProvidersStatus(data) {
  return request({
    url: '/api/v1/llm-providers/batch/update-status',
    method: 'post',
    data
  })
}

/**
 * 澧炲姞LLM渚涘簲鍟嗕娇鐢ㄦ垚鏈? * @param {number} providerId - 渚涘簲鍟咺D
 * @param {number} costCents - 鎴愭湰锛堝垎锛? * @returns {Promise} API鍝嶅簲
 */
export function incrementLLMProviderCost(providerId, costCents) {
  return request({
    url: `/api/v1/llm-providers/${providerId}/increment-cost`,
    method: 'post',
    data: { cost_cents: costCents }
  })
}
