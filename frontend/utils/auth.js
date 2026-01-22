import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/api/v1/auth/login',
    method: 'post',
    data
  })
}

export function register(data) {
  return request({
    url: '/api/v1/auth/register',
    method: 'post',
    data
  })
}

export function getInfo() {
  return request({
    url: '/api/v1/auth/me',
    method: 'get'
  })
}

export function logout() {
  return request({
    url: '/api/v1/auth/logout',
    method: 'post'
  })
}

export function refreshToken() {
  return request({
    url: '/api/v1/auth/refresh',
    method: 'post',
    data: {
      refresh_token: getRefreshToken()
    }
  })
}

export function changePassword(data) {
  return request({
    url: '/api/v1/auth/change-password',
    method: 'put',
    data
  })
}