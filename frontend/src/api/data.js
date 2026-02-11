import request from '@/utils/request'

// 获取数据列表
export function getDataList(params) {
  return request({
    url: '/api/admin/data',
    method: 'get',
    params
  })
}

// 新增数据
export function createData(data) {
  return request({
    url: '/api/admin/data',
    method: 'post',
    data
  })
}

// 删除数据
export function deleteData(id) {
  return request({
    url: `/api/admin/data/${id}`,
    method: 'delete'
  })
}

// 导出数据
export function exportData(params) {
  return request({
    url: '/api/admin/data/export',
    method: 'post',
    data: params
  })
}
