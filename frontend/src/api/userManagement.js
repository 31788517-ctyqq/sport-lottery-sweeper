/**
 * 用户管理API
 */

import request from '@/utils/request'

// 获取用户列表
export function getUserList(params) {
  return request({
    url: '/api/admin/backend-users',
    method: 'get',
    params
  })
}

// 获取用户详情
export function getUserById(id) {
  return request({
    url: `/api/admin/backend-users/${id}`,
    method: 'get'
  })
}

// 创建用户
export function createUser(data) {
  return request({
    url: '/api/admin/backend-users',
    method: 'post',
    data
  })
}

// 更新用户
export function updateUser(id, data) {
  return request({
    url: `/api/admin/backend-users/${id}`,
    method: 'put',
    data
  })
}

// 删除用户
export function deleteUser(id) {
  return request({
    url: `/api/admin/backend-users/${id}`,
    method: 'delete'
  })
}

// 更新用户状态
export function updateUserStatus(id, status) {
  return request({
    url: `/api/admin/backend-users/${id}/status`,
    method: 'patch',
    data: { status }
  })
}

// 重置用户密码
export function resetUserPassword(id, password) {
  return request({
    url: `/api/admin/backend-users/${id}/reset-password`,
    method: 'post',
    data: { password }
  })
}

// 批量删除用户
export function batchDeleteUsers(ids) {
  return request({
    url: '/api/admin/backend-users/batch-delete',
    method: 'delete',
    data: { ids }
  })
}

// 获取角色列表
export function getRoleList() {
  return request({
    url: '/api/admin/roles',
    method: 'get'
  })
}

// 更新角色权限
export function updateRolePermissions(roleId, permissions) {
  return request({
    url: `/api/admin/roles/${roleId}/permissions`,
    method: 'put',
    data: { permissions }
  })
}

// 获取操作日志
export function getOperationLogs(params) {
  return request({
    url: '/api/admin/operation-logs',
    method: 'get',
    params
  })
}

// 获取部门列表
export function getDepartmentList() {
  return request({
    url: '/api/admin/departments',
    method: 'get'
  })
}

// 创建部门
export function createDepartment(data) {
  return request({
    url: '/api/admin/departments',
    method: 'post',
    data
  })
}

// 更新部门
export function updateDepartment(id, data) {
  return request({
    url: `/api/admin/departments/${id}`,
    method: 'put',
    data
  })
}

// 删除部门
export function deleteDepartment(id) {
  return request({
    url: `/api/admin/departments/${id}`,
    method: 'delete'
  })
}