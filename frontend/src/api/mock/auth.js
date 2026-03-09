/**
 * Mock认证API - 临时解决后端500错误问题
 * 用于前端开发和测试
 */

// 模拟登录响应
const mockLoginResponse = {
  code: 200,
  message: "登录成功",
  data: {
    access_token: "mock-jwt-token-1234567890",
    token_type: "bearer",
    user_info: {
      userId: 1,
      username: "admin",
      email: "admin@sportlottery.com",
      roles: ["admin"],
      status: "active"
    }
  }
}

// Mock登录函数
export const mockLogin = (credentials) => {
  console.log('Using mock login for:', credentials.username)
  
  // 模拟异步请求
  return new Promise((resolve) => {
    setTimeout(() => {
      // 简单的用户名密码验证
      if (credentials.username === 'admin' && credentials.password === 'admin123') {
        // 保存token到localStorage
        localStorage.setItem('access_token', mockLoginResponse.data.access_token)
        localStorage.setItem('user_info', JSON.stringify(mockLoginResponse.data.user_info))
        resolve(mockLoginResponse)
      } else {
        resolve({
          code: 401,
          message: "用户名或密码错误",
          data: null
        })
      }
    }, 500) // 模拟网络延迟
  })
}

// Mock登出函数
export const mockLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_info')
  return Promise.resolve({ code: 200, message: "登出成功" })
}

// Mock获取用户信息
export const mockGetUserInfo = () => {
  const userInfo = localStorage.getItem('user_info')
  if (userInfo) {
    return Promise.resolve({
      code: 200,
      message: "获取成功",
      data: JSON.parse(userInfo)
    })
  }
  return Promise.resolve({ code: 401, message: "未登录", data: null })
}
