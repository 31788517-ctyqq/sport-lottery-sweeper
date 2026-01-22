// frontend/src/router/index.js
import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/jczq',
    name: 'Jczq',
    component: () => import('../views/JczqSchedule.vue')
  },
  {
    path: '/jczq-schedule',
    name: 'JczqSchedule',
    component: () => import('../views/JczqSchedule.vue')
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/AdminLogin.vue')
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('../views/AdminDashboard.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),  // 使用hash模式，支持 #/ 路径
  routes
})

export default router