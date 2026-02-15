/**
 * 后台用户管理API
 * 用于管理具有后台权限的运营人员和管理员
 */
import request from '../client'

// 开发环境模拟数据
const mockBackendUsers = [
  { id: 1, username: 'admin_zhang', email: 'zhang@company.com', real_name: '张管理员', phone: '13800000001', role: 'super_admin', status: 'active', department: '技术部', position: '技术总监', two_factor_enabled: true, last_login_at: '2024-01-20T10:30:00Z', login_allowed_ips: ['192.168.1.0/24'], remarks: '系统超级管理员' },
  { id: 2, username: 'admin_li', email: 'li@company.com', real_name: '李管理员', phone: '13800000002', role: 'admin', status: 'active', department: '运营部', position: '运营总监', two_factor_enabled: true, last_login_at: '2024-01-20T09:15:00Z', login_allowed_ips: [], remarks: '运营管理' },
  { id: 3, username: 'mod_wang', email: 'wang@company.com', real_name: '王审核', phone: '13800000003', role: 'moderator', status: 'active', department: '内容部', position: '内容主管', two_factor_enabled: false, last_login_at: '2024-01-20T08:45:00Z', login_allowed_ips: [], remarks: '内容审核管理' },
  { id: 4, username: 'audit_chen', email: 'chen@company.com', real_name: '陈审计', phone: '13800000004', role: 'auditor', status: 'active', department: '审计部', position: '审计专员', two_factor_enabled: true, last_login_at: '2024-01-19T18:20:00Z', login_allowed_ips: ['10.0.0.0/8'], remarks: '系统审计' },
  { id: 5, username: 'ops_liu', email: 'liu@company.com', real_name: '刘运营', phone: '13800000005', role: 'operator', status: 'active', department: '运营部', position: '运营专员', two_factor_enabled: false, last_login_at: '2024-01-20T11:00:00Z', login_allowed_ips: [], remarks: '日常运营' },
  { id: 6, username: 'admin_zhao', email: 'zhao@company.com', real_name: '赵管理员', phone: '13800000006', role: 'admin', status: 'inactive', department: '技术部', position: '技术经理', two_factor_enabled: false, last_login_at: '2024-01-18T15:30:00Z', login_allowed_ips: [], remarks: '暂未激活' },
  { id: 7, username: 'mod_qian', email: 'qian@company.com', real_name: '钱审核', phone: '13800000007', role: 'moderator', status: 'suspended', department: '内容部', position: '内容专员', two_factor_enabled: false, last_login_at: '2024-01-17T14:20:00Z', login_allowed_ips: [], remarks: '暂停使用' },
  { id: 8, username: 'ops_feng', email: 'feng@company.com', real_name: '冯运营', phone: '13800000008', role: 'operator', status: 'locked', department: '运营部', position: '运营助理', two_factor_enabled: false, last_login_at: '2024-01-16T12:10:00Z', login_allowed_ips: [], remarks: '账户锁定' },
  { id: 9, username: 'audit_huang', email: 'huang@company.com', real_name: '黄审计', phone: '13800000009', role: 'auditor', status: 'active', department: '审计部', position: '高级审计师', two_factor_enabled: true, last_login_at: '2024-01-20T07:50:00Z', login_allowed_ips: ['172.16.0.0/12'], remarks: '高级审计' },
  { id: 10, username: 'admin_wu', email: 'wu@company.com', real_name: '吴管理员', phone: '13800000010', role: 'admin', status: 'active', department: '客服部', position: '客服主管', two_factor_enabled: true, last_login_at: '2024-01-20T10:05:00Z', login_allowed_ips: [], remarks: '客服管理' },
  { id: 11, username: 'ops_zhou', email: 'zhou@company.com', real_name: '周运营', phone: '13800000011', role: 'operator', status: 'active', department: '运营部', position: '数据分析师', two_factor_enabled: false, last_login_at: '2024-01-19T16:40:00Z', login_allowed_ips: [], remarks: '数据分析' },
  { id: 12, username: 'mod_xu', email: 'xu@company.com', real_name: '徐审核', phone: '13800000012', role: 'moderator', status: 'active', department: '内容部', position: '新媒体运营', two_factor_enabled: false, last_login_at: '2024-01-20T09:30:00Z', login_allowed_ips: [], remarks: '新媒体内容' },
  { id: 13, username: 'audit_sun', email: 'sun@company.com', real_name: '孙审计', phone: '13800000013', role: 'auditor', status: 'inactive', department: '审计部', position: '审计助理', two_factor_enabled: false, last_login_at: '2024-01-15T11:25:00Z', login_allowed_ips: [], remarks: '培训中' },
  { id: 14, username: 'ops_ma', email: 'ma@company.com', real_name: '马运营', phone: '13800000014', role: 'operator', status: 'active', department: '运营部', position: '活动策划', two_factor_enabled: false, last_login_at: '2024-01-20T08:15:00Z', login_allowed_ips: [], remarks: '活动策划执行' },
  { id: 15, username: 'admin_zheng', email: 'zheng@company.com', real_name: '郑管理员', phone: '13800000015', role: 'super_admin', status: 'active', department: '技术部', position: 'CTO', two_factor_enabled: true, last_login_at: '2024-01-20T09:00:00Z', login_allowed_ips: ['203.0.113.0/24'], remarks: '技术负责人' }
]

/**
 * 获取后台用户列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getBackendUsers(params) {
  // 开发环境返回模拟数据
  if (import.meta.env.DEV) {
    return Promise.resolve({
      data: {
        items: mockBackendUsers,
        total: mockBackendUsers.length,
        pages: 1
      }
    })
  }
  
  return request({
    url: '/api/admin/users/',
    method: 'get',
    params
  })
}

/**
 * 获取后台用户详情
 * @param {Number} userId - 用户ID
 * @returns {Promise}
 */
export function getBackendUserDetail(userId) {
  // 开发环境返回模拟数据
  if (import.meta.env.DEV) {
    const user = mockBackendUsers.find(u => u.id === userId)
    return Promise.resolve({ data: user || {} })
  }
  
  return request({
    url: `/api/admin/users/${userId}`,
    method: 'get'
  })
}

/**
 * 创建后台用户
 * @param {Object} data - 用户数据
 * @returns {Promise}
 */
export function createBackendUser(data) {
  return request({
    url: '/api/admin-users',
    method: 'post',
    data
  })
}

/**
 * 更新后台用户信息
 * @param {Number} userId - 用户ID
 * @param {Object} data - 用户数据
 * @returns {Promise}
 */
export function updateBackendUser(userId, data) {
  return request({
    url: `/api/admin-users/${userId}`,
    method: 'put',
    data
  })
}

/**
 * 更新后台用户状态
 * @param {Number} userId - 用户ID
 * @param {String} status - 新状态
 * @returns {Promise}
 */
export function updateBackendUserStatus(userId, status) {
  return request({
    url: `/api/admin-users/${userId}/status`,
    method: 'put',
    data: { status }
  })
}

/**
 * 修改后台用户密码（用户自己操作）
 * @param {Number} userId - 用户ID
 * @param {Object} data - 密码数据
 * @returns {Promise}
 */
export function changeBackendUserPassword(userId, data) {
  return request({
    url: `/api/admin-users/${userId}/change-password`,
    method: 'post',
    data
  })
}

/**
 * 重置后台用户密码（管理员操作）
 * @param {Number} userId - 用户ID
 * @param {Object} data - 密码数据
 * @returns {Promise}
 */
export function resetBackendUserPassword(userId, data) {
  return request({
    url: `/api/admin-users/${userId}/reset-password`,
    method: 'post',
    data
  })
}

/**
 * 删除后台用户
 * @param {Number} userId - 用户ID
 * @returns {Promise}
 */
export function deleteBackendUser(userId) {
  return request({
    url: `/api/admin-users/${userId}`,
    method: 'delete'
  })
}

/**
 * 获取后台用户统计信息
 * @returns {Promise}
 */
export function getBackendUserStats() {
  // 开发环境返回模拟统计数据
  if (import.meta.env.DEV) {
    const stats = {
      total_users: mockBackendUsers.length,
      active_users: mockBackendUsers.filter(u => u.status === 'active').length,
      locked_users: mockBackendUsers.filter(u => u.status === 'locked').length,
      two_factor_enabled_count: mockBackendUsers.filter(u => u.two_factor_enabled).length
    }
    return Promise.resolve({ data: stats })
  }
  
  return request({
    url: '/api/admin/users/stats',
    method: 'get'
  })
}

/**
 * 获取后台用户操作日志
 * @param {Number} userId - 用户ID
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getBackendUserOperationLogs(userId, params) {
  // 开发环境返回模拟日志数据
  if (import.meta.env.DEV) {
    const mockLogs = Array.from({ length: 10 }, (_, i) => ({
      id: i + 1,
      action: ['create', 'update', 'delete'][i % 3],
      resource_type: ['admin_user', 'match', 'intelligence'][i % 3],
      resource_name: `资源${i + 1}`,
      created_at: new Date(Date.now() - i * 3600000).toISOString(),
      ip_address: `192.168.1.${100 + i}`,
      status_code: 200
    }))
    
    const start = (params.page - 1) * params.size
    const end = start + params.size
    const items = mockLogs.slice(start, end)
    
    return Promise.resolve({
      data: {
        items,
        total: mockLogs.length,
        pages: Math.ceil(mockLogs.length / params.size)
      }
    })
  }
  
  return request({
    url: `/api/admin/users/${userId}/operation-logs`,
    method: 'get',
    params
  })
}

/**
 * 获取后台用户登录日志
 * @param {Number} userId - 用户ID
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getBackendUserLoginLogs(userId, params) {
  // 开发环境返回模拟登录日志
  if (import.meta.env.DEV) {
    const mockLogs = Array.from({ length: 8 }, (_, i) => ({
      id: i + 1,
      created_at: new Date(Date.now() - i * 7200000).toISOString(),
      ip_address: `10.0.0.${i + 1}`,
      user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      success: i % 4 !== 0
    }))
    
    const start = (params.page - 1) * params.size
    const end = start + params.size
    const items = mockLogs.slice(start, end)
    
    return Promise.resolve({
      data: {
        items,
        total: mockLogs.length,
        pages: Math.ceil(mockLogs.length / params.size)
      }
    })
  }
  
  return request({
    url: `/api/admin/users/${userId}/login-logs`,
    method: 'get',
    params
  })
}

export default {
  getBackendUsers,
  getBackendUserDetail,
  createBackendUser,
  updateBackendUser,
  updateBackendUserStatus,
  changeBackendUserPassword,
  resetBackendUserPassword,
  deleteBackendUser,
  getBackendUserStats,
  getBackendUserOperationLogs,
  getBackendUserLoginLogs
}
