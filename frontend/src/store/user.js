// src/store/user.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(null)
  const isAuthenticated = ref(false)
  const userInfo = ref(null)

  const setToken = (authToken) => {
    token.value = authToken
  }

  const setUserInfo = (info) => {
    userInfo.value = info
  }

  const clear = () => {
    token.value = null
    userInfo.value = null
    isAuthenticated.value = false
  }

  return {
    token,
    isAuthenticated,
    userInfo,
    setToken,
    setUserInfo,
    clear
  }
})