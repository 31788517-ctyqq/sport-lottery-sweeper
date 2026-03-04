import http from '@/utils/http'

/**
 * 部门管理 API
 */

export const getDepartmentList = (params) => {
  return http.get('/api/v1/admin/departments/', { params })
}

export const getDepartmentTree = () => {
  return http.get('/api/v1/admin/departments/tree')
}

export const getDepartmentDetail = (id) => {
  return http.get(`/api/v1/admin/departments/${id}`)
}

export const createDepartment = (data) => {
  return http.post('/api/v1/admin/departments/', data)
}

export const updateDepartment = (id, data) => {
  return http.put(`/api/v1/admin/departments/${id}`, data)
}

export const deleteDepartment = (id) => {
  return http.delete(`/api/v1/admin/departments/${id}`)
}

export const batchDeleteDepartments = (ids) => {
  return http.delete('/api/v1/admin/departments/batch', { data: { ids } })
}

export const updateDepartmentStatus = (id, status) => {
  return http.patch(`/api/v1/admin/departments/${id}/status`, { status })
}

export const moveDepartment = (id, data) => {
  return http.patch(`/api/v1/admin/departments/${id}/move`, data)
}

export const getDepartmentMembers = (id, params) => {
  return http.get(`/api/v1/admin/departments/${id}/members`, { params })
}

export const addDepartmentMembers = (departmentId, userIds) => {
  return http.post(`/api/v1/admin/departments/${departmentId}/members`, { user_ids: userIds })
}

export const removeDepartmentMember = (departmentId, userId) => {
  return http.delete(`/api/v1/admin/departments/${departmentId}/members/${userId}`)
}

export const batchRemoveDepartmentMembers = (departmentId, userIds) => {
  return http.delete(`/api/v1/admin/departments/${departmentId}/members/batch`, {
    data: { user_ids: userIds }
  })
}

export const assignUserToDepartment = (departmentId, userId) => {
  return http.post(`/api/v1/admin/departments/${departmentId}/members/${userId}`)
}

export const removeUserFromDepartment = (departmentId, userId) => {
  return http.delete(`/api/v1/admin/departments/${departmentId}/members/${userId}`)
}

export const getDepartmentOptions = () => {
  return http.get('/api/v1/admin/departments/options')
}

export const getDepartmentStats = () => {
  return http.get('/api/v1/admin/departments/stats')
}

// 兼容旧调用
export const getDepartments = getDepartmentList
