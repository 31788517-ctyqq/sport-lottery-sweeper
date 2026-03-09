import http, { request as httpRequest } from '@/utils/http'

const asDataResponse = async (promise) => {
  const result = await promise
  return result && typeof result === 'object' && 'data' in result ? result : { data: result }
}

const ROLE_LABEL_MAP = {
  super_admin: '超级管理员',
  admin: '管理员',
  moderator: '版主',
  auditor: '审计员',
  operator: '运营员'
}

const normalizeRoleNames = (raw = {}) => {
  if (Array.isArray(raw.roleNames)) return raw.roleNames
  if (Array.isArray(raw.role_names)) return raw.role_names
  if (Array.isArray(raw.roles)) {
    return raw.roles
      .map((role) => {
        if (typeof role === 'string') return role
        return role?.name || role?.code || role?.id
      })
      .filter(Boolean)
  }
  if (raw.role) return [raw.role]
  return []
}

const normalizeUserEntity = (raw = {}) => ({
  ...raw,
  id: Number(raw.id ?? raw.userId ?? 0),
  username: raw.username || '',
  realName: raw.realName || raw.real_name || '',
  email: raw.email || '',
  phone: raw.phone || '',
  departmentId: raw.departmentId ?? raw.department_id ?? null,
  departmentName: raw.departmentName || raw.department_name || raw.department || '',
  role: raw.role || '',
  roleLabel: ROLE_LABEL_MAP[raw.role] || raw.role || '',
  roleNames: normalizeRoleNames(raw),
  status: raw.status || '',
  createdAt: raw.createdAt || raw.created_at || null,
  updatedAt: raw.updatedAt || raw.updated_at || null,
  lastLoginTime: raw.lastLoginTime || raw.last_login_time || raw.last_login_at || null
})

const normalizeUserListData = (data = {}) => {
  const rows = Array.isArray(data.items) ? data.items.map(normalizeUserEntity) : []
  return {
    ...data,
    items: rows,
    total: Number(data.total ?? rows.length ?? 0),
    pages: Number(data.pages ?? 0),
    page: Number(data.page ?? 1),
    size: Number(data.size ?? rows.length ?? 0)
  }
}

const toBackendUserPayload = (data = {}, { isCreate = false } = {}) => {
  const payload = {}

  if (isCreate) {
    payload.username = data.username
    payload.password = data.password
  }

  if (data.email !== undefined) payload.email = data.email
  if (data.realName !== undefined || data.real_name !== undefined) {
    payload.real_name = data.realName ?? data.real_name
  }
  if (data.phone !== undefined) payload.phone = data.phone || null
  if (data.departmentName !== undefined || data.department !== undefined || data.department_name !== undefined) {
    payload.department = data.departmentName ?? data.department_name ?? data.department ?? null
  }
  if (data.position !== undefined) payload.position = data.position || null
  if (data.status !== undefined) payload.status = data.status
  if (data.remarks !== undefined || data.remark !== undefined) payload.remarks = data.remarks ?? data.remark ?? null
  if (data.role !== undefined) payload.role = data.role
  if (!payload.role && data.roleValue !== undefined) payload.role = data.roleValue

  return payload
}

const compactParams = (obj = {}) =>
  Object.fromEntries(Object.entries(obj).filter(([, value]) => value !== '' && value !== undefined && value !== null))

const normalizeListParams = (params = {}) => {
  const hasPage = Number.isFinite(Number(params.page))
  const hasSize = Number.isFinite(Number(params.size))
  const normalizedSize = hasSize ? Math.max(1, Number(params.size)) : Number(params.limit || 20)
  // Backend constraint: limit <= 100
  const limit = Math.min(100, normalizedSize)
  const skip = hasPage ? (Math.max(1, Number(params.page)) - 1) * limit : params.skip

  return compactParams({
    skip,
    limit,
    search: params.search,
    status: params.status,
    department: params.department || params.departmentName,
    role: params.role || params.roleValue || params.roleName
  })
}

export const getUserList = async (params) => {
  const response = await asDataResponse(http.get('/api/v1/admin/admin-users/', { params: normalizeListParams(params) }))
  return {
    ...response,
    data: normalizeUserListData(response?.data || {})
  }
}

export const getUserDetail = async (id) => {
  const response = await asDataResponse(http.get(`/api/v1/admin/admin-users/${id}`))
  return {
    ...response,
    data: normalizeUserEntity(response?.data || {})
  }
}

export const createUser = async (data) => {
  const payload = toBackendUserPayload(data, { isCreate: true })
  const response = await asDataResponse(http.post('/api/v1/admin/admin-users/', payload))
  return {
    ...response,
    data: normalizeUserEntity(response?.data || {})
  }
}

export const updateUser = async (id, data) => {
  const payload = toBackendUserPayload(data, { isCreate: false })
  const response = await asDataResponse(http.put(`/api/v1/admin/admin-users/${id}`, payload))
  return {
    ...response,
    data: normalizeUserEntity(response?.data || {})
  }
}

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

export const importUsers = (file) => asDataResponse(httpRequest.upload('/api/v1/admin/admin-users/import', file))
export const exportUsers = (params) => httpRequest.download('/api/v1/admin/admin-users/export', params, 'admin_users.csv')

export const getUserStats = () => asDataResponse(http.get('/api/v1/admin/admin-users/stats'))
export const unlockUser = (id) => asDataResponse(http.post(`/api/v1/admin/admin-users/${id}/unlock`))
export const getUserLoginHistory = (id, params) => asDataResponse(http.get(`/api/v1/admin/admin-users/${id}/login-history`, { params }))
export const changeCurrentPassword = (data) => asDataResponse(http.put('/api/v1/admin/admin-users/change-password', data))

export const getUsers = getUserList
export const getCurrentUser = getUserDetail
export const updateCurrentUser = updateUser
export const disableUsers = (ids) => Promise.all(ids.map((id) => updateUserStatus(id, 'inactive')))
export const enableUsers = (ids) => Promise.all(ids.map((id) => updateUserStatus(id, 'active')))
export const searchUsers = getUserList
