import request from '@/utils/request'

// 获取爬虫配置列表
export function getConfigs(params) {
  return request({
    url: '/api/admin/v1/crawler-configs',
    method: 'get',
    params
  })
}

// 新增爬虫配置
export function createConfig(data) {
  return request({
    url: '/api/admin/v1/crawler-configs',
    method: 'post',
    data
  })
}

// 更新爬虫配置
export function updateConfig(id, data) {
  return request({
    url: `/api/admin/v1/crawler-configs/${id}`,
    method: 'put',
    data
  })
}

// 删除爬虫配置
export function deleteConfig(id) {
  return request({
    url: `/api/admin/v1/crawler-configs/${id}`,
    method: 'delete'
  })
}

// 获取配置版本历史
export function getConfigVersions(configId) {
  return request({
    url: `/api/admin/v1/crawler-configs/${configId}/versions`,
    method: 'get'
  })
}

// 回滚到指定版本
export function rollbackConfig(configId, version) {
  return request({
    url: `/api/admin/v1/crawler-configs/${configId}/rollback`,
    method: 'post',
    data: { version }
  })
}

// 导出配置
export function exportConfigs(params) {
  return request({
    url: '/api/admin/v1/crawler-configs/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

// 导入配置
export function importConfigs(data) {
  return request({
    url: '/api/admin/v1/crawler-configs/import',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 测试连接
export function testConnection(configId) {
  return request({
    url: `/api/admin/v1/crawler-configs/${configId}/test`,
    method: 'post'
  })
}