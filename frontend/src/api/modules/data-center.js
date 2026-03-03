import request from '@/utils/request'

export function getDataCenterTableData(params) {
  return request({
    url: '/api/v1/admin/data-center/table-data',
    method: 'get',
    params
  })
}

export function exportDataCenterTable(data) {
  return request({
    url: '/api/v1/admin/data-center/table-export',
    method: 'post',
    data
  })
}

export function getDataCenterSourceOptions(params) {
  return request({
    url: '/api/v1/admin/data-center/source-options',
    method: 'get',
    params
  })
}
