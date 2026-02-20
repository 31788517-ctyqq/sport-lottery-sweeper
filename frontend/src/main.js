import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import { useTheme } from './styles/theme.js'
import config, { ENV_HELPERS } from './config'
import { getErrorMessage, isBenignBrowserError } from '@/utils/benign-browser-errors'

console.log('main.js is loading...')

// Permission management
import { createPermissionDirective } from '@/composables/usePermissions'

// Import global styles
import './styles/index.css'
// Light theme for buttons, cards, tables
import './styles/light-theme.scss'

// Create Vue application
const app = createApp(App)

// Create Pinia store
const pinia = createPinia()

// AI_WORKING: coder1 @2026-01-28T03:30:00Z - 添加用户存储初始化
// Use plugins
app.use(pinia)

// Initialize user store from localStorage
useUserStore().initializeFromStorage()
// AI_DONE: coder1 @2026-01-28T03:30:00Z

app.use(router)
app.use(ElementPlus)
useTheme()

// Register all icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Register permission directives
createPermissionDirective(app)

// Error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error caught:', err)
  console.error('Component instance:', instance)
  console.error('Error info:', info)

  // In production, you might want to send this to an error tracking service
  if (import.meta.env.PROD) {
    // Example: Sentry.captureException(err)
  }
}

// ===== 新增：全局 JavaScript 错误捕获 =====
window.addEventListener('error', event => {
  const raw = event.error || event.message
  if (isBenignBrowserError(raw)) return
  console.error('Global JS error (window.onerror):', raw)
})
window.addEventListener('unhandledrejection', event => {
  if (isBenignBrowserError(event.reason)) return
  console.error('Unhandled promise rejection:', getErrorMessage(event.reason) || event.reason)
})
// ===========================================

// Global properties
app.config.globalProperties.$config = config
app.config.globalProperties.$ENV = ENV_HELPERS.getEnvironment()

// Development helpers
if (ENV_HELPERS.isDevelopment()) {
  // Add debug info to window
  window.__APP_CONFIG__ = config
  window.__DEBUG__ = {
    version: config.APP_CONSTANTS.APP_VERSION,
    environment: ENV_HELPERS.getEnvironment(),
    features: config.FEATURE_FLAGS
  }

  // Enable Vue devtools in development
  app.config.devtools = true
} else {
  // Disable Vue devtools in production for performance
  app.config.devtools = false
}

// Debug: log environment variables
console.log('Environment variables:')
console.log('VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL)
console.log('VITE_WS_BASE_URL:', import.meta.env.VITE_WS_BASE_URL)
console.log('MODE:', import.meta.env.MODE)
console.log('BASE_URL:', import.meta.env.BASE_URL)

// Mount the app
app.mount('#app')

// Service Worker registration (optional)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('SW registered: ', registration)
      })
      .catch(registrationError => {
        console.log('SW registration failed: ', registrationError)
      })
  })
}

console.log(`${config.APP_CONSTANTS.APP_NAME} v${config.APP_CONSTANTS.APP_VERSION} started in ${ENV_HELPERS.getEnvironment()} mode`)
console.log('Features enabled:', Object.entries(config.FEATURE_FLAGS).filter(([key, value]) => value).map(([key]) => key))

export { app }
