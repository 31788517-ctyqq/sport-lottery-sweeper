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

// AI_WORKING: coder1 @2026-02-01 - 导出通用数据管理Store
export * from './dataManager'
// AI_DONE: coder1 @2026-02-01

// AI_WORKING: coder1 @2026-02-04 - 导出任务监控Store
export * from './taskMonitorStore'
// AI_DONE: coder1 @2026-02-04