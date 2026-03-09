// src/store/modules/user.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(null)
  const isAuthenticated = ref(false)
  const user = ref(null)

  const setAuth = (authToken, userInfo) => {
    token.value = authToken
    user.value = userInfo
    isAuthenticated.value = true
  }

  const clearAuth = () => {
    token.value = null
    user.value = null
    isAuthenticated.value = false
  }

  return {
    token,
    isAuthenticated,
    user,
    setAuth,
    clearAuth
  }
})