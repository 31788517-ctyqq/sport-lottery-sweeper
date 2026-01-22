// frontend/src/router/routes/admin.js
const adminRoutes = [
  {
    path: '/admin',
    name: 'AdminHome',
    component: () => import('@/views/admin/AdminHome.vue'),
    meta: {
      title: '管理后台',
      requiresAuth: true,
      roles: ['admin'] // 标记此路由需要 'admin' 角色
    }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('@/views/admin/Users.vue'),
    meta: {
      title: '用户管理',
      requiresAuth: true,
      roles: ['admin']
    }
  },
  {
    path: '/admin/products',
    name: 'AdminProducts',
    component: () => import('@/views/admin/Products.vue'),
    meta: {
      title: '产品管理',
      requiresAuth: true,
      roles: ['admin']
    }
  },
  // 更多管理后台路由...
];

export default adminRoutes;