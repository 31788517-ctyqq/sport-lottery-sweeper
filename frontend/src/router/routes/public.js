// frontend/src/router/routes/public.js
const publicRoutes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'), // 使用动态导入以实现代码分割
    meta: { 
      title: '首页',
      showNavbar: true,
      showBottomNav: true
    } // 可以设置页面标题等元信息
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
  },
  // 更多公开路由...
];

export default publicRoutes;