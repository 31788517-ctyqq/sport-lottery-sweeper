import http from '@/utils/http'

/**
 * 用户管理相关 API
 */

const asDataResponse = async (promise) => {
  const result = await promise
  return result && typeof result === 'object' && 'data' in result ? result : { data: result }
}

const compactParams = (obj = {}) => {
  return Object.fromEntries(
    Object.entries(obj).filter(([, value]) => value !== '' && value !== undefined && value !== null)
  )
}

const normalizeListParams = (params = {}) => {
  const hasPage = Number.isFinite(Number(params.page))
  const hasSize = Number.isFinite(Number(params.size))
  const skip = hasPage && hasSize ? (Math.max(1, Number(params.page)) - 1) * Math.max(1, Number(params.size)) : params.skip
  const limit = hasSize ? Math.max(1, Number(params.size)) : params.limit

  return compactParams({
    skip,
    limit,
    search: params.search,
    status: params.status,
    department: params.department || params.departmentName,
    role: params.role || params.roleName
  })
}

export const getUserList = (params) => asDataResponse(http.get('/api/v1/admin/admin-users/', { params: normalizeListParams(params) }))
export const getUserDetail = (id) => asDataResponse(http.get(`/api/v1/admin/admin-users/${id}`))
export const createUser = (data) => asDataResponse(http.post('/api/v1/admin/admin-users/', data))
export const updateUser = (id, data) => asDataResponse(http.put(`/api/v1/admin/admin-users/${id}`, data))
export const deleteUser = (id) => asDataResponse(http.delete(`/api/v1/admin/admin-users/${id}`))
export const batchDeleteUsers = (ids) => asDataResponse(http.delete('/api/v1/admin/admin-users/batch', { data: { ids } }))

export const updateUserStatus = async (id, status) => {
  try {
    return await asDataResponse(http.patch(`/api/v1/admin/admin-users/${id}/status`, { status }))
  } catch (error) {
    return asDataResponse(http.put(`/api/v1/admin/admin-users/${id}/status`, null, { params: { status } }))
  }
}

export const resetUserPassword = (id, data) => asDataResponse(http.post(`/api/v1/admin/admin-users/${id}/reset-password`, data))
export const getUserRoles = (id) => asDataResponse(http.get(`/api/v1/admin/admin-users/${id}/roles`))
export const assignUserRoles = (id, roleIds) => asDataResponse(http.post(`/api/v1/admin/admin-users/${id}/roles`, { roleIds }))
export const batchAssignRoles = (data) => asDataResponse(http.post('/api/v1/admin/admin-users/batch-assign-roles', data))
export const getUserDepartments = (id) => asDataResponse(http.get(`/api/v1/admin/admin-users/${id}/departments`))

export const importUsers = (file) => asDataResponse(http.upload('/api/v1/admin/admin-users/import', file))
export const exportUsers = (params) => http.download('/api/v1/admin/admin-users/export', params, 'admin_users.csv')

export const getUserStats = () => asDataResponse(http.get('/api/v1/admin/admin-users/stats'))
export const unlockUser = (id) => asDataResponse(http.post(`/api/v1/admin/admin-users/${id}/unlock`))
export const getUserLoginHistory = (id, params) => asDataResponse(http.get(`/api/v1/admin/admin-users/${id}/login-history`, { params }))
export const changeCurrentPassword = (data) => asDataResponse(http.put('/api/v1/admin/admin-users/change-password', data))

// aliases for existing callers
export const getUsers = getUserList
export const getCurrentUser = getUserDetail
export const updateCurrentUser = updateUser
export const disableUsers = (ids) => Promise.all(ids.map((id) => updateUserStatus(id, 'inactive')))
export const enableUsers = (ids) => Promise.all(ids.map((id) => updateUserStatus(id, 'active')))
export const searchUsers = getUserList
