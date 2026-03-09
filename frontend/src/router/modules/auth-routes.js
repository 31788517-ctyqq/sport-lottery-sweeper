// 认证模块路由 - AI_WORKING: coder1 @1770224919 - 提取认证相关路由（登录/注册）
const authRoutes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Login.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册' }
  }
]

export default authRoutes