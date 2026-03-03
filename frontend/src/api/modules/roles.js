import http from '@/utils/http'

export const ROLE_API_CAPABILITIES = Object.freeze({
  batchDelete: false,
  copyRole: false,
  exportRole: false,
  importRole: false
})

const unsupportedRoleApi = (action) => {
  const error = new Error(`角色接口能力不支持: ${action}`)
  error.code = 'ROLE_API_UNSUPPORTED'
  return Promise.reject(error)
}
/**
 * 角色管理相关API
 */

// 获取角色列表
export const getRoleList = (params) => {
  return http.get('/api/v1/admin/roles/', { params })
}

// 获取角色详情
export const getRoleDetail = (id) => {
  return http.get(`/api/v1/admin/roles/${id}`)
}

// 创建角色
export const createRole = (data) => {
  return http.post('/api/v1/admin/roles/', data)
}

// 更新角色
export const updateRole = (id, data) => {
  return http.put(`/api/v1/admin/roles/${id}`, data)
}

// 删除角色
export const deleteRole = (id) => {
  return http.delete(`/api/v1/admin/roles/${id}`)
}

// 批量删除角色
export const batchDeleteRoles = (ids) => {
  void ids
  return unsupportedRoleApi('batchDeleteRoles')
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
  const payload = Array.isArray(permissionIds)
    ? permissionIds
    : permissionIds?.permissionIds || permissionIds?.permission_ids || permissionIds?.permissions || []
  return http.post(`/api/v1/admin/roles/${id}/permissions`, payload)
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
  void id
  void data
  return unsupportedRoleApi('copyRole')
}

// 获取角色统计信息
export const getRoleStats = () => {
  return http.get('/api/v1/admin/roles/stats')
}

// 导出角色
export const exportRoles = (params) => {
  void params
  return unsupportedRoleApi('exportRoles')
}

// 导入角色
export const importRoles = (file) => {
  void file
  return unsupportedRoleApi('importRoles')
}

// 别名导出，以匹配组件中的导入
export const getRoles = getRoleList
