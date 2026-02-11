import http from '@/utils/http'

/**
 * 用户画像管理相关API
 */

// 获取用户画像列表
export const getUserProfiles = (params) => {
  return http.get('/api/v1/admin/user-profiles', { params })
}

// 获取单个用户画像
export const getUserProfile = (id) => {
  return http.get(`/api/v1/admin/user-profiles/${id}`)
}

// 更新用户画像
export const updateUserProfile = (id, data) => {
  return http.put(`/api/v1/admin/user-profiles/${id}`, data)
}

// 批量更新用户画像
export const batchUpdateUserProfiles = (data) => {
  return http.put('/api/v1/admin/user-profiles/batch', data)
}

// 导出用户画像
export const exportUserProfiles = (params) => {
  return http.get('/api/v1/admin/user-profiles/export', { 
    params, 
    responseType: 'blob' 
  })
}

// 获取用户画像统计
export const getUserProfileStats = () => {
  return http.get('/api/v1/admin/user-profiles/stats')
}

// 获取用户画像标签
export const getUserProfileTags = () => {
  return http.get('/api/v1/admin/user-profiles/tags')
}

// 删除用户画像
export const deleteUserProfile = (id) => {
  return http.delete(`/api/v1/admin/user-profiles/${id}`)
}

// 批量删除用户画像
export const batchDeleteUserProfiles = (ids) => {
  return http.delete('/api/v1/admin/user-profiles/batch', { data: { ids } })
}

// 别名导出
export const fetchUserProfiles = getUserProfiles
export const fetchUserProfile = getUserProfile