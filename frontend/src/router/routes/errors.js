// frontend/src/router/routes/errors.js
const errorRoutes = [
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/errors/NotFound.vue'),
    meta: { title: '页面未找到' }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/errors/Forbidden.vue'),
    meta: { title: '无权访问' }
  },
  {
    path: '/500',
    name: 'InternalServerError',
    component: () => import('@/views/errors/InternalServerError.vue'),
    meta: { title: '服务器内部错误' }
  },
  // 将所有未匹配到的路径重定向到 404 页面
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
    meta: { requiresAuth: false } // 404 页面通常是公开的
  }
];

export default errorRoutes;