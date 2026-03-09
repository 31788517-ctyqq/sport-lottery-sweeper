import request from '@/utils/request'

export function saveConfig(data) {
  return request({
    url: '/multi-strategy/config',
    method: 'post',
    data
  })
}

export function getConfig(params) {
  return request({
    url: '/multi-strategy/config',
    method: 'get',
    params
  })
}

export function executeMultiStrategy(data) {
  return request({
    url: '/multi-strategy/execute',
    method: 'post',
    data
  })
}

export default {
  saveConfig,
  getConfig,
  executeMultiStrategy
}