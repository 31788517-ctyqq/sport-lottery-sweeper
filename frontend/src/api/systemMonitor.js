// 系统监控API
import request from '@/utils/request'

export function getSystemHealth() {
  return request({
    url: '/api/v1/system/monitor/health',
    method: 'get'
  })
}

export function getSystemResources() {
  return request({
    url: '/api/v1/system/monitor/resources',
    method: 'get'
  })
}