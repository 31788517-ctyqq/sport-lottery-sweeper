import request from '@/utils/request'

// 获取数据列表
export function getDataList(params) {
  return request({
    url: '/api/v1/admin/data',
    method: 'get',
    params
  })
}

// 新增数据
export function createData(data) {
  return request({
    url: '/api/v1/admin/data',
    method: 'post',
    data
  })
}

// 删除数据
export function deleteData(id) {
  return request({
    url: `/api/v1/admin/data/${id}`,
    method: 'delete'
  })
}

// 导出数据
export function exportData(params) {
  return request({
    url: '/api/v1/admin/data/export',
    method: 'post',
    data: params
  })
}

// 获取数据源选项（用于筛选下拉）
export function getDataSourceOptions(params) {
  return request({
    url: '/api/v1/admin/sources',
    method: 'get',
    params
  })
}
