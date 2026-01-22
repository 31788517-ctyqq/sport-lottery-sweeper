import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/login',
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
  // 后端未实现获取用户信息接口，返回模拟数据
  console.warn('Get user info endpoint not implemented in backend');
  return Promise.resolve({ id: 1, username: 'admin', role: 'super_admin' });
}

export function logout() {
  // 后端未实现logout接口，返回模拟成功
  console.warn('Logout endpoint not implemented in backend');
  return Promise.resolve({ code: 200, message: 'success' });
}

export function refreshToken() {
  // 后端未实现refresh接口，返回模拟成功
  console.warn('Refresh token endpoint not implemented in backend');
  return Promise.resolve({ code: 200, message: 'success' });
}

export function changePassword(data) {
  // 后端未实现更改密码接口，返回模拟成功
  console.warn('Change password endpoint not implemented in backend');
  return Promise.resolve({ code: 200, message: 'success' });
}