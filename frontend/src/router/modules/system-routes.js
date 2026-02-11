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
        component: () => import('@/views/admin/SystemManagement.vue'),
        meta: {
          title: '系统配置',
          icon: 'setting',
          roles: ['admin'],
          tab: 'config'
        }
      },
      {
        path: 'monitoring',
        name: 'SystemMonitoring',
        component: () => import('@/views/admin/SystemManagement.vue'),
        meta: {
          title: '系统监控',
          icon: 'monitor',
          roles: ['admin'],
          tab: 'monitoring'
        }
      },
      {
        path: 'logs',
        name: 'SystemLogs',
        component: () => import('@/views/admin/SystemManagement.vue'),
        meta: {
          title: '系统日志',
          icon: 'document',
          roles: ['admin'],
          tab: 'logs'
        }
      },
      {
        path: 'maintenance',
        name: 'SystemMaintenance',
        component: () => import('@/views/admin/SystemManagement.vue'),
        meta: {
          title: '维护工具',
          icon: 'tools',
          roles: ['admin'],
          tab: 'maintenance'
        }
      },
      {
        path: 'backup',
        name: 'SystemBackup',
        component: () => import('@/views/admin/SystemManagement.vue'),
        meta: {
          title: '数据备份',
          icon: 'backup',
          roles: ['admin'],
          tab: 'backup'
        }
      },
      {
        path: 'api',
        name: 'SystemAPI',
        component: () => import('@/views/admin/SystemManagement.vue'),
        meta: {
          title: 'API管理',
          icon: 'api',
          roles: ['admin'],
          tab: 'api'
        }
      }
    ]
  }
]

export default systemRoutes