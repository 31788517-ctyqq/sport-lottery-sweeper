// 系统监控API
import request from '@/utils/request'

export function getSystemHealth() {
  return request({
    url: '/api/system/monitor/health',
    method: 'get'
  })
}

export function getSystemResources() {
  return request({
    url: '/api/system/monitor/resources',
    method: 'get'
  })
}