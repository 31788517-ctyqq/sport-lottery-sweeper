import http from '@/utils/http'
// import { request } from '@/utils/request'  // 这一行不需要，因为request.js没有具名导出request

/**
 * 用户个人资料相关API
 */

// 获取个人资料
export const getProfile = () => {
  return http.get('/user/profile')
}

// 更新个人资料
export const updateProfile = (data) => {
  return http.put('/user/profile', data)
}

// 修改密码
export const changePassword = (data) => {
  return http.put('/user/change-password', data)
}

// 上传头像
export const uploadAvatar = (file) => {
  const formData = new FormData()
  formData.append('avatar', file)
  
  return http.post('/user/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取登录历史
export const getLoginHistory = (params) => {
  return http.get('/user/login-history', { params })
}

// 获取个人操作日志
export const getPersonalLogs = (params) => {
  return http.get('/user/operation-logs', { params })
}

// 绑定第三方账号
export const bindThirdPartyAccount = (data) => {
  return http.post('/user/bind-third-party', data)
}

// 解绑第三方账号
export const unbindThirdPartyAccount = (provider) => {
  return http.delete(`/user/unbind-third-party/${provider}`)
}

// 获取第三方账号绑定状态
export const getThirdPartyBindStatus = () => {
  return http.get('/user/third-party-status')
}

// 设置安全问题
export const setSecurityQuestions = (data) => {
  return http.post('/user/security-questions', data)
}

// 验证安全问题
export const verifySecurityQuestions = (data) => {
  return http.post('/user/verify-security-questions', data)
}

// 获取通知设置
export const getNotificationSettings = () => {
  return http.get('/user/notification-settings')
}

// 更新通知设置
export const updateNotificationSettings = (data) => {
  return http.put('/user/notification-settings', data)
}

// 获取隐私设置
export const getPrivacySettings = () => {
  return http.get('/user/privacy-settings')
}

// 更新隐私设置
export const updatePrivacySettings = (data) => {
  return http.put('/user/privacy-settings', data)
}

// 导出个人数据
export const exportPersonalData = (types) => {
  return http.post('/user/export-data', { types }, { responseType: 'blob' })
}

// 删除账号
export const deleteAccount = (data) => {
  return http.delete('/user/account', { data })
}

// 获取会话列表
export const getSessions = () => {
  return http.get('/user/sessions')
}

// 撤销指定会话
export const revokeSession = (sessionId) => {
  return http.delete(`/user/sessions/${sessionId}`)
}

// 撤销所有其他会话
export const revokeAllOtherSessions = () => {
  return http.delete('/user/sessions/others')
}

// 获取账号统计信息
export const getAccountStats = () => {
  return http.get('/user/stats')
}

// 别名导出，以匹配组件中的导入
export const getUserStats = getAccountStats