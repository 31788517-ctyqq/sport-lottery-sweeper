import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia

// 示例：用户 Store（防止 http.js 中引用报错）
import { defineStore } from 'pinia'
export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    userInfo: null,
  }),
  actions: {
    setToken(tk) {
      this.token = tk
    },
    logout() {
      this.token = ''
      this.userInfo = null
    },
  },
})