/**
 * 通用数据管理API模块
 * 提供标准化的数据操作接口
 */

import apiClient from '../index'

/**
 * 获取数据列表
 * @param {string} endpoint - API端点
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getList = async (endpoint, params = {}) => {
  try {
    const response = await apiClient.get(endpoint, { params })
    return response
  } catch (error) {
    console.error(`获取${endpoint}列表失败:`, error)
    throw error
  }
}

/**
 * 获取单个项目
 * @param {string} endpoint - API端点
 * @param {number|string} id - 项目ID
 * @returns {Promise}
 */
export const getItem = async (endpoint, id) => {
  try {
    const response = await apiClient.get(`${endpoint}/${id}`)
    return response
  } catch (error) {
    console.error(`获取${endpoint}项目失败:`, error)
    throw error
  }
}

/**
 * 创建项目
 * @param {string} endpoint - API端点
 * @param {Object} data - 项目数据
 * @returns {Promise}
 */
export const createItem = async (endpoint, data) => {
  try {
    const response = await apiClient.post(endpoint, data)
    return response
  } catch (error) {
    console.error(`创建${endpoint}项目失败:`, error)
    throw error
  }
}

/**
 * 更新项目
 * @param {string} endpoint - API端点
 * @param {number|string} id - 项目ID
 * @param {Object} data - 更新数据
 * @returns {Promise}
 */
export const updateItem = async (endpoint, id, data) => {
  try {
    const response = await apiClient.put(`${endpoint}/${id}`, data)
    return response
  } catch (error) {
    console.error(`更新${endpoint}项目失败:`, error)
    throw error
  }
}

/**
 * 删除项目
 * @param {string} endpoint - API端点
 * @param {number|string} id - 项目ID
 * @returns {Promise}
 */
export const deleteItem = async (endpoint, id) => {
  try {
    const response = await apiClient.delete(`${endpoint}/${id}`)
    return response
  } catch (error) {
    console.error(`删除${endpoint}项目失败:`, error)
    throw error
  }
}

/**
 * 批量删除项目
 * @param {string} endpoint - API端点
 * @param {Array} ids - 项目ID列表
 * @returns {Promise}
 */
export const batchDeleteItems = async (endpoint, ids) => {
  try {
    const response = await apiClient.post(`${endpoint}/batch-delete`, { ids })
    return response
  } catch (error) {
    console.error(`批量删除${endpoint}项目失败:`, error)
    throw error
  }
}

/**
 * 更新多项
 * @param {string} endpoint - API端点
 * @param {Array} items - 项目列表
 * @returns {Promise}
 */
export const updateMultipleItems = async (endpoint, items) => {
  try {
    const response = await apiClient.put(`${endpoint}/batch-update`, { items })
    return response
  } catch (error) {
    console.error(`批量更新${endpoint}项目失败:`, error)
    throw error
  }
}