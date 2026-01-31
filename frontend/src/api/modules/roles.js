import http from '@/utils/http'
import { API_ENDPOINTS } from '@/config/api'

/**
 * 角色管理相关API
 */

// 获取角色列表
export const getRoleList = (params) => {
  return http.get(API_ENDPOINTS.ROLES.LIST, { params })
}

// 获取角色详情
export const getRoleDetail = (id) => {
  return http.get(`${API_ENDPOINTS.ROLES.UPDATE(id)}`)
}

// 创建角色
export const createRole = (data) => {
  return http.post(API_ENDPOINTS.ROLES.CREATE, data)
}

// 更新角色
export const updateRole = (id, data) => {
  return http.put(API_ENDPOINTS.ROLES.UPDATE(id), data)
}

// 删除角色
export const deleteRole = (id) => {
  return http.delete(API_ENDPOINTS.ROLES.DELETE(id))
}

// 批量删除角色
export const batchDeleteRoles = (ids) => {
  return http.delete('/api/v1/admin/roles/batch', { data: { ids } })
}

// 更新角色状态
export const updateRoleStatus = (id, status) => {
  return http.patch(`/api/v1/admin/roles/${id}/status`, { status })
}

// 获取角色权限
export const getRolePermissions = (id) => {
  return http.get(`/api/v1/admin/roles/${id}/permissions`)
}

// 分配角色权限
export const assignRolePermissions = (id, permissionIds) => {
  return http.post(`/api/v1/admin/roles/${id}/permissions`, { permissionIds })
}

// 获取权限树
export const getPermissionTree = () => {
  return http.get('/api/v1/admin/permissions/tree')
}

// 获取所有权限
export const getAllPermissions = () => {
  return http.get('/api/v1/admin/permissions')
}

// 复制角色
export const copyRole = (id, data) => {
  return http.post(`/api/v1/admin/roles/${id}/copy`, data)
}

// 获取角色统计信息
export const getRoleStats = () => {
  return http.get('/api/v1/admin/roles/stats')
}

// 导出角色
export const exportRoles = (params) => {
  return http.get('/api/v1/admin/roles/export', { params, responseType: 'blob' })
}

// 导入角色
export const importRoles = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return http.post('/api/v1/admin/roles/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 别名导出，以匹配组件中的导入
export const getRoles = getRoleList