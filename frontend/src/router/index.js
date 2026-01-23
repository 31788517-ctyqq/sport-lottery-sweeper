import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

// 基础路由配置 - 临时占位页面
const routes = [
  {
    path: '/',
    redirect: '/admin'
  },
  {
    path: '/admin',
    redirect: '/admin/dashboard'
  },
  {
    path: '/admin/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/admin/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/admin/users/:type',
    name: 'UserManagement',
    component: () => import('../views/UserManagement.vue')
  },
  {
    path: '/admin/match/:type',
    name: 'MatchManagement',
    component: () => import('../views/MatchManagement.vue')
  },
  {
    path: '/admin/intelligence',
    name: 'IntelligenceManagement',
    component: () => import('../views/IntelligenceManagement.vue')
  },
  {
    path: '/admin/data',
    name: 'DataManagement',
    component: () => import('../views/DataManagement.vue')
  },
  {
    path: '/admin/crawler/:type',
    name: 'CrawlerManagement',
    component: () => import('../views/CrawlerManagement.vue')
  },
  {
    path: '/admin/sp/:type',
    name: 'SPManagement',
    component: () => import('../views/SPManagement.vue')
  },
  {
    path: '/admin/draw-prediction/:type',
    name: 'DrawPrediction',
    component: () => import('../views/DrawPrediction.vue')
  },
  {
    path: '/admin/system',
    name: 'SystemManagement',
    component: () => import('../views/SystemManagement.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由守卫 - 权限控制
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const isLogin = !!userStore.token || !!localStorage.getItem('token')
  if (to.path.startsWith('/admin') && !isLogin) {
    next('/admin/login')
  } else {
    next()
  }
})

export default router