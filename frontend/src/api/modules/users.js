import http from '@/utils/http'
import { API_ENDPOINTS } from '@/config/api'

/**
 * 用户管理相关API
 */

// 获取用户列表
export const getUserList = (params) => {
  return http.get(API_ENDPOINTS.USERS.LIST, { params })
}

// 获取用户详情
export const getUserDetail = (id) => {
  return http.get(`/api/v1/admin/users/${id}`)
}

// 创建用户
export const createUser = (data) => {
  return http.post('/admin/users', data)
}

// 更新用户信息 - 修正路径为管理员用户更新API
export const updateUser = (id, data) => {
  return http.put(`/api/v1/admin/users/${id}`, data)
}

// 删除用户
export const deleteUser = (id) => {
  return http.delete(`/admin/users/${id}`)
}

// 批量删除用户
export const batchDeleteUsers = (ids) => {
  return http.delete('/admin/users/batch', { data: { ids } })
}

// 更新用户状态
export const updateUserStatus = (id, status) => {
  return http.patch(`/admin/users/${id}/status`, { status })
}

// 重置用户密码
export const resetUserPassword = (id, data) => {
  return http.post(`/admin/users/${id}/reset-password`, data)
}

// 获取用户角色
export const getUserRoles = (id) => {
  return http.get(`/admin/users/${id}/roles`)
}

// 分配用户角色
export const assignUserRoles = (id, roleIds) => {
  return http.post(`/admin/users/${id}/roles`, { roleIds })
}

// 批量分配角色
export const batchAssignRoles = (data) => {
  return http.post('/admin/users/batch-assign-roles', data)
}

// 获取用户部门
export const getUserDepartments = (id) => {
  return http.get(`/admin/users/${id}/departments`)
}

// 导入用户
export const importUsers = (file) => {
  return http.upload('/admin/users/import', file)
}

// 导出用户
export const exportUsers = (params) => {
  return http.download('/admin/users/export', params, 'users.xlsx')
}

// 获取用户统计信息
export const getUserStats = () => {
  return http.get('/admin/users/stats')
}

// 解锁用户账户
export const unlockUser = (id) => {
  return http.post(`/admin/users/${id}/unlock`)
}

// 获取用户登录历史
export const getUserLoginHistory = (id, params) => {
  return http.get(`/admin/users/${id}/login-history`, { params })
}

// 别名导出，以匹配组件中的导入
export const getUsers = getUserList
export const getCurrentUser = (id) => {
  return http.get(`/api/v1/admin/users/${id}`)
}
export const updateCurrentUser = (id, data) => {
  return http.put(`/api/v1/admin/users/${id}`, data)
}
export const disableUsers = updateUserStatus
export const enableUsers = updateUserStatus
export const searchUsers = getUserList