import http from '@/utils/http'
import { API_ENDPOINTS } from '@/config/api'

/**
 * 部门管理相关API
 */

// 获取部门列表
export const getDepartmentList = (params) => {
  return http.get(API_ENDPOINTS.DEPARTMENTS.LIST, { params })
}

// 获取部门树形结构
export const getDepartmentTree = () => {
  return http.get('/api/admin/departments/tree')
}

// 获取部门详情
export const getDepartmentDetail = (id) => {
  return http.get(`/api/admin/departments/${id}`)
}

// 创建部门
export const createDepartment = (data) => {
  return http.post('/api/admin/departments', data)
}

// 更新部门
export const updateDepartment = (id, data) => {
  return http.put(`/api/admin/departments/${id}`, data)
}

// 删除部门
export const deleteDepartment = (id) => {
  return http.delete(`/api/admin/departments/${id}`)
}

// 批量删除部门
export const batchDeleteDepartments = (ids) => {
  return http.delete('/api/admin/departments/batch', { data: { ids } })
}

// 更新部门状态
export const updateDepartmentStatus = (id, status) => {
  return http.patch(`/api/admin/departments/${id}/status`, { status })
}

// 获取部门成员
export const getDepartmentMembers = (id, params) => {
  return http.get(`/api/admin/departments/${id}/members`, { params })
}

// 添加部门成员
export const addDepartmentMembers = (id, userIds) => {
  return http.post(`/api/admin/departments/${id}/members`, { userIds })
}

// 移除部门成员
export const removeDepartmentMember = (departmentId, userId) => {
  return http.delete(`/api/admin/departments/${departmentId}/members/${userId}`)
}

// 批量移除部门成员
export const batchRemoveDepartmentMembers = (departmentId, userIds) => {
  return http.delete(`/api/admin/departments/${departmentId}/members/batch`, { data: { userIds } })
}

// 获取部门树（扁平结构）
export const getDepartmentOptions = () => {
  return http.get('/api/admin/departments/options')
}

// 移动部门
export const moveDepartment = (id, data) => {
  return http.patch(`/api/admin/departments/${id}/move`, data)
}

// 获取部门统计信息
export const getDepartmentStats = () => {
  return http.get('/api/admin/departments/stats')
}

// 导出部门
export const exportDepartments = (params) => {
  return http.get('/api/admin/departments/export', { params, responseType: 'blob' })
}

// 导入部门
export const importDepartments = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return http.post('/api/admin/departments/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 将用户分配到部门
export const assignUserToDepartment = (departmentId, userId) => {
  return http.post(`/api/admin/departments/${departmentId}/members/${userId}`)
}

// 从部门移除用户
export const removeUserFromDepartment = (departmentId, userId) => {
  return http.delete(`/api/admin/departments/${departmentId}/members/${userId}`)
}

// 别名导出，以匹配组件中的导入
export const getDepartments = getDepartmentList