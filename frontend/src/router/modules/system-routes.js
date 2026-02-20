// 绯荤粺绠＄悊妯″潡璺敱
const systemRoutes = [
  // 宓屽鍦?admin涓嬬殑绯荤粺绠＄悊瀛愯矾鐢?
  {
    path: 'system',
    name: 'SystemManagement',
    redirect: '/admin/system/config',
    meta: {
      title: '绯荤粺绠＄悊',
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
        path: ':rest(.*)*',
        redirect: '/admin/system/config'
      }
    ]
  }
]

export default systemRoutes
