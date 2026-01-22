import request from '@/utils/request'

// 获取爬虫配置列表
export function getConfigs(params) {
  return request({
    url: '/api/admin/crawler/configs',
    method: 'get',
    params
  })
}

// 新增爬虫配置
export function createConfig(data) {
  return request({
    url: '/api/admin/crawler/configs',
    method: 'post',
    data
  })
}

// 更新爬虫配置
export function updateConfig(id, data) {
  return request({
    url: `/api/admin/crawler/configs/${id}`,
    method: 'put',
    data
  })
}

// 删除爬虫配置
export function deleteConfig(id) {
  return request({
    url: `/api/admin/crawler/configs/${id}`,
    method: 'delete'
  })
}
