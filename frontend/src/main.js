import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 导入主路由配置
import router from './router/index.js'
import App from './App.vue'

// 创建应用实例
const app = createApp(App)
const pinia = createPinia()

// 注册Element Plus
app.use(ElementPlus)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册 Pinia
app.use(pinia)

// 注册路由
app.use(router)

// 挂载应用
app.mount('#app')