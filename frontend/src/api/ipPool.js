import request from '@/utils/request'

export function getIpPoolList(params) {
  return request({
    url: '/api/admin/ip-pools',
    method: 'get',
    params
  })
}

export function getIpById(id) {
  return request({
    url: `/api/admin/ip-pools/${id}`,
    method: 'get'
  })
}

export function createIp(data) {
  return request({
    url: '/api/admin/ip-pools',
    method: 'post',
    data
  })
}

export function updateIp(id, data) {
  return request({
    url: `/api/admin/ip-pools/${id}`,
    method: 'put',
    data
  })
}

export function deleteIp(id) {
  return request({
    url: `/api/admin/ip-pools/${id}`,
    method: 'delete'
  })
}

export function batchDeleteIps(data) {
  return request({
    url: '/api/admin/ip-pools/batch/delete',
    method: 'post',
    data
  })
}

export function testIp(id) {
  return request({
    url: `/api/admin/ip-pools/${id}/test-connection`,
    method: 'post'
  })
}

export function batchTestIps(data) {
  return request({
    url: '/api/admin/ip-pools/batch/test',
    method: 'post',
    data
  })
}

export function getIpStats() {
  return request({
    url: '/api/admin/ip-pools/stats',
    method: 'get'
  })
}

export function exportIpPool() {
  return request({
    url: '/api/admin/ip-pools/export',
    method: 'get',
    responseType: 'blob'
  })
}

export function getSourceAddresses() {
  return request({
    url: '/api/admin/ip-pools/source-addresses',
    method: 'get'
  })
}

export function addSourceAddress(data) {
  return request({
    url: '/api/admin/ip-pools/source-addresses',
    method: 'post',
    data
  })
}

export function updateSourceAddress(data) {
  return request({
    url: '/api/admin/ip-pools/source-addresses',
    method: 'put',
    data
  })
}

export function deleteSourceAddress(data) {
  return request({
    url: '/api/admin/ip-pools/source-addresses',
    method: 'delete',
    data
  })
}

export function recrawlIps(data = {}) {
  return request({
    url: '/api/admin/ip-pools/recrawl',
    method: 'post',
    data
  })
}
