import http from '@/utils/http'

/**
 * 权限管理相关API
 */

// 获取权限列表
export const getPermissionList = (params) => {
  return http.get('/api/v1/admin/permissions/', { params })
}

// 获取权限详情
export const getPermissionDetail = (id) => {
  return http.get(`/api/v1/admin/permissions/${id}`)
}

// 创建权限
export const createPermission = (data) => {
  return http.post('/api/v1/admin/permissions/', data)
}

// 更新权限
export const updatePermission = (id, data) => {
  return http.put(`/api/v1/admin/permissions/${id}`, data)
}

// 删除权限
export const deletePermission = (id) => {
  return http.delete(`/api/v1/admin/permissions/${id}`)
}

// 批量删除权限
export const batchDeletePermissions = (ids) => {
  return http.delete('/api/v1/admin/permissions/batch', { data: { ids } })
}

// 更新权限状态
export const updatePermissionStatus = (id, status) => {
  return http.patch(`/api/v1/admin/permissions/${id}/status`, { status })
}

// 获取权限树
export const getPermissionTree = (params) => {
  return http.get('/api/v1/admin/permissions/tree', { params })
}

// 获取权限分组
export const getPermissionGroups = () => {
  return http.get('/api/v1/admin/permissions/groups')
}

// 根据类型获取权限
export const getPermissionsByType = (type) => {
  return http.get(`/api/v1/admin/permissions/type/${type}`)
}

// 检查权限编码是否存在
export const checkPermissionCode = (code, excludeId) => {
  return http.get('/api/v1/admin/permissions/check-code', { params: { code, excludeId } })
}

// 获取权限统计信息
export const getPermissionStats = () => {
  return http.get('/api/v1/admin/permissions/stats')
}

// 同步权限（从代码自动生成）
export const syncPermissions = () => {
  return http.post('/api/v1/admin/permissions/sync')
}

// 获取用户权限
export const getUserPermissions = (userId) => {
  return http.get(`/api/v1/admin/users/${userId}/permissions`)
}

// 获取角色权限
export const getRolePermissions = (roleId) => {
  return http.get(`/api/v1/admin/roles/${roleId}/permissions`)
}

// 导出权限
export const exportPermissions = (params) => {
  return http.get('/api/v1/admin/permissions/export', { params, responseType: 'blob' })
}

// 别名导出，以匹配组件中的导入
export const getPermissions = getPermissionList
