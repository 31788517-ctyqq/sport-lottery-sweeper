import request from '@/utils/request'

// 获取系统配置列表
export function getSystemList(params) {
  return request({
    url: '/api/admin/system',
    method: 'get',
    params
  })
}

// 新增系统配置
export function createSystem(data) {
  return request({
    url: '/api/admin/system',
    method: 'post',
    data
  })
}

// 删除系统配置
export function deleteSystem(id) {
  return request({
    url: `/api/admin/system/${id}`,
    method: 'delete'
  })
}
