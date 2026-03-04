// 前台用户页面模块路由 - AI_WORKING: coder1 @1770224919 - 提取前台用户页面路由
const frontendRoutes = [
  {
    path: '/home',
    name: 'HomeView',
    component: () => import('@/views/HomeView.vue'),
    meta: { 
      title: '首页',
      showNavbar: true,
      showBottomNav: true
    }
  },
  {
    path: '/filter',
    name: 'Filter',
    component: () => import('@/views/FilterView.vue'),
    meta: { 
      title: '筛选',
      showNavbar: true,
      showBottomNav: true
    }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('@/views/FavoritesView.vue'),
    meta: { 
      title: '收藏',
      showNavbar: true,
      showBottomNav: true
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { 
      title: '个人中心',
      showNavbar: true,
      showBottomNav: true
    }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue'),
    meta: { title: '关于我们' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: {
      title: '仪表盘',
      requiresAuth: true
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: {
      title: '设置',
      requiresAuth: true
    }
  }
]

export default frontendRoutes