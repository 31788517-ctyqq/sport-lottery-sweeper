/**
 * 前台用户管理API
 * 用于管理使用前台系统的普通用户
 */
import request from '../client'

// 模拟数据 - 当API不可用或开发时使用
const mockUsers = [
  { id: 1, username: 'user001', email: 'user001@example.com', nickname: '张三', user_type: 'normal', status: 'active', created_at: '2024-01-15T10:00:00Z', last_login_at: '2024-01-20T08:30:00Z' },
  { id: 2, username: 'user002', email: 'user002@example.com', nickname: '李四', user_type: 'premium', status: 'active', created_at: '2024-01-14T14:20:00Z', last_login_at: '2024-01-20T09:15:00Z' },
  { id: 3, username: 'user003', email: 'user003@example.com', nickname: '王五', user_type: 'normal', status: 'inactive', created_at: '2024-01-13T09:45:00Z', last_login_at: null },
  { id: 4, username: 'user004', email: 'user004@example.com', nickname: '赵六', user_type: 'analyst', status: 'active', created_at: '2024-01-12T16:30:00Z', last_login_at: '2024-01-19T20:45:00Z' },
  { id: 5, username: 'user005', email: 'user005@example.com', nickname: '钱七', user_type: 'premium', status: 'suspended', created_at: '2024-01-11T11:15:00Z', last_login_at: '2024-01-18T15:20:00Z' },
  { id: 6, username: 'user006', email: 'user006@example.com', nickname: '孙八', user_type: 'normal', status: 'active', created_at: '2024-01-10T13:25:00Z', last_login_at: '2024-01-20T07:50:00Z' },
  { id: 7, username: 'user007', email: 'user007@example.com', nickname: '周九', user_type: 'normal', status: 'banned', created_at: '2024-01-09T08:40:00Z', last_login_at: '2024-01-17T12:30:00Z' },
  { id: 8, username: 'user008', email: 'user008@example.com', nickname: '吴十', user_type: 'premium', status: 'active', created_at: '2024-01-08T15:10:00Z', last_login_at: '2024-01-20T06:25:00Z' },
  { id: 9, username: 'user009', email: 'user009@example.com', nickname: '郑十一', user_type: 'analyst', status: 'active', created_at: '2024-01-07T12:00:00Z', last_login_at: '2024-01-19T18:40:00Z' },
  { id: 10, username: 'user010', email: 'user010@example.com', nickname: '王十二', user_type: 'normal', status: 'active', created_at: '2024-01-06T17:35:00Z', last_login_at: '2024-01-20T05:15:00Z' }
]

const mockStats = {
  total_users: 1250,
  active_users: 980,
  premium_users: 156,
  today_new_users: 23
}

/**
 * 获取前台用户列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getFrontendUsers(params) {
  // 开发环境下使用模拟数据
  if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
    console.log('使用模拟数据 - 前台用户列表')
    
    let filteredUsers = [...mockUsers]
    
    // 简单过滤逻辑
    if (params.search) {
      const search = params.search.toLowerCase()
      filteredUsers = filteredUsers.filter(user => 
        user.username.toLowerCase().includes(search) ||
        user.email.toLowerCase().includes(search) ||
        (user.nickname && user.nickname.toLowerCase().includes(search))
      )
    }
    
    if (params.status) {
      filteredUsers = filteredUsers.filter(user => user.status === params.status)
    }
    
    if (params.user_type) {
      filteredUsers = filteredUsers.filter(user => user.user_type === params.user_type)
    }
    
    // 分页逻辑
    const page = params.page || 1
    const size = params.size || 20
    const startIndex = (page - 1) * size
    const endIndex = startIndex + size
    const paginatedUsers = filteredUsers.slice(startIndex, endIndex)
    
    return Promise.resolve({
      data: {
        items: paginatedUsers,
        total: filteredUsers.length,
        pages: Math.ceil(filteredUsers.length / size),
        page: page,
        size: size
      }
    })
  }
  
  // 生产环境使用真实API
  return request({
    url: '/api/v1/admin/users/',
    method: 'get',
    params
  })
}

/**
 * 获取前台用户详情
 * @param {Number} userId - 用户ID
 * @returns {Promise}
 */
export function getFrontendUserDetail(userId) {
  // 开发环境下使用模拟数据
  if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
    console.log('使用模拟数据 - 前台用户详情:', userId)
    const user = mockUsers.find(u => u.id === parseInt(userId))
    if (user) {
      return Promise.resolve({ data: user })
    }
    return Promise.reject(new Error('用户不存在'))
  }
  
  // 生产环境使用真实API
  return request({
    url: `/api/v1/admin/users/${userId}`,
    method: 'get'
  })
}

/**
 * 更新前台用户信息
 * @param {Number} userId - 用户ID
 * @param {Object} data - 用户数据
 * @returns {Promise}
 */
export function updateFrontendUser(userId, data) {
  // 开发环境下模拟更新
  if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
    console.log('使用模拟数据 - 更新前台用户:', userId, data)
    const index = mockUsers.findIndex(u => u.id === parseInt(userId))
    if (index !== -1) {
      mockUsers[index] = { ...mockUsers[index], ...data }
    }
    return Promise.resolve({ data: { success: true, message: '更新成功' } })
  }
  
  // 生产环境使用真实API
  return request({
    url: `/api/v1/admin/users/${userId}`,
    method: 'put',
    data
  })
}

/**
 * 更新前台用户状态
 * @param {Number} userId - 用户ID
 * @param {String} status - 新状态
 * @returns {Promise}
 */
export function updateFrontendUserStatus(userId, status) {
  // 开发环境下模拟更新状态
  if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
    console.log('使用模拟数据 - 更新前台用户状态:', userId, status)
    const user = mockUsers.find(u => u.id === parseInt(userId))
    if (user) {
      user.status = status
    }
    return Promise.resolve({ data: { success: true, message: '状态更新成功' } })
  }
  
  // 生产环境使用真实API
  return request({
    url: `/api/v1/admin/users/${userId}/status`,
    method: 'put',
    data: { status }
  })
}

/**
 * 删除前台用户
 * @param {Number} userId - 用户ID
 * @returns {Promise}
 */
export function deleteFrontendUser(userId) {
  // 开发环境下模拟删除
  if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
    console.log('使用模拟数据 - 删除前台用户:', userId)
    const index = mockUsers.findIndex(u => u.id === parseInt(userId))
    if (index !== -1) {
      mockUsers.splice(index, 1)
    }
    return Promise.resolve({ data: { success: true, message: '删除成功' } })
  }
  
  // 生产环境使用真实API
  return request({
    url: `/api/v1/admin/users/${userId}`,
    method: 'delete'
  })
}

/**
 * 获取前台用户统计信息
 * @returns {Promise}
 */
export function getFrontendUserStats() {
  // 开发环境下使用模拟数据
  if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
    console.log('使用模拟数据 - 前台用户统计')
    return Promise.resolve({ 
      data: { 
        data: mockStats 
      } 
    })
  }
  
  // 生产环境使用真实API
  return request({
    url: '/api/v1/admin/users/stats',
    method: 'get'
  })
}

/**
 * 批量删除用户
 * @param {Array} userIds - 用户ID数组
 * @returns {Promise}
 */
export function batchDeleteUsers(userIds) {
  // 开发环境下模拟批量删除
  if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
    console.log('使用模拟数据 - 批量删除用户:', userIds)
    userIds.forEach(id => {
      const index = mockUsers.findIndex(u => u.id === parseInt(id))
      if (index !== -1) {
        mockUsers.splice(index, 1)
      }
    })
    return Promise.resolve({ data: { success: true, message: '批量删除成功' } })
  }
  
  // 生产环境使用真实API
  return request({
    url: '/api/v1/admin/users/batch-delete',
    method: 'post',
    data: { user_ids: userIds }
  })
}

/**
 * 批量更新用户状态
 * @param {Array} userIds - 用户ID数组
 * @param {String} status - 新状态
 * @returns {Promise}
 */
export function batchUpdateUserStatus(userIds, status) {
  // 开发环境下模拟批量更新状态
  if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
    console.log('使用模拟数据 - 批量更新用户状态:', userIds, status)
    userIds.forEach(id => {
      const user = mockUsers.find(u => u.id === parseInt(id))
      if (user) {
        user.status = status
      }
    })
    return Promise.resolve({ data: { success: true, message: '批量更新状态成功' } })
  }
  
  // 生产环境使用真实API
  return request({
    url: '/api/v1/admin/users/batch-update-status',
    method: 'post',
    data: { user_ids: userIds, status }
  })
}

export default {
  getFrontendUsers,
  getFrontendUserDetail,
  updateFrontendUser,
  updateFrontendUserStatus,
  deleteFrontendUser,
  getFrontendUserStats,
  batchDeleteUsers,
  batchUpdateUserStatus
}