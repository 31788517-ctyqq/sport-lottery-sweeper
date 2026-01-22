// src/api/auth.js
import axios from './client'

export const login = async (username, password) => {
  try {
    const response = await axios.post('/api/v1/auth/login', {
      username,
      password
    })
    return response.data
  } catch (error) {
    throw error
  }
}

// 可扩展其他认证相关接口，如 logout, refreshToken 等