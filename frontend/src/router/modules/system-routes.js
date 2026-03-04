// 系统管理模块路由
const systemRoutes = [
  // 嵌套在/admin下的系统管理子路由
  {
    path: 'system',
    name: 'SystemManagement',
    redirect: '/admin/system/config',
    meta: {
      title: '系统管理',
      icon: 'Setting',
      roles: ['admin'],
      order: 12
    },
    children: [
      {
        path: 'config',
        name: 'SystemConfig',
        component: () => import('@/views/admin/system/SystemManagement.vue'),
        meta: {
          title: 'System Config',
          icon: 'setting',
          roles: ['admin'],
          tab: 'config'
        }
      },
      {
        path: 'entity-mappings',
        name: 'EntityMappings',
        component: () => import('@/views/admin/system/EntityMappings.vue'),
        meta: {
          title: '实体映射管理',
          icon: 'map-location',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: ':rest(.*)*',
        redirect: '/admin/system/config'
      }
    ]
  }
]

export default systemRoutes