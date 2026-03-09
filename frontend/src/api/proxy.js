import request from '@/utils/request'

// 获取代理列表
export function getProxyList(params) {
  return request({
    url: '/api/admin/proxies',
    method: 'get',
    params
  })
}

// 新增代理
export function addProxy(data) {
  return request({
    url: '/api/admin/proxies',
    method: 'post',
    data
  })
}

// 删除代理
export function deleteProxy(id) {
  return request({
    url: `/api/admin/proxies/${id}`,
    method: 'delete'
  })
}

// 测试代理
export function testProxy(id) {
  return request({
    url: `/api/admin/proxies/${id}/test`,
    method: 'post'
  })
}