// 爬虫管理模块路由
const crawlerRoutes = [
  // 嵌套在/admin下的爬虫管理子路由
  {
    path: 'data-source',
    name: 'DataSourceManagement',
    redirect: '/admin/data-source/config',
    meta: {
      title: '数据源管理',
      icon: 'SetUp',
      roles: ['admin', 'manager']
    },
    children: [
      {
        path: 'config',
        name: 'DataSourceConfig',
        component: () => import('@/views/admin/crawler/DataSourceManagement.vue'),
        meta: {
          title: '数据源配置',
          icon: 'link',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'monitor',
        name: 'DataSourceMonitor',
        component: () => import('@/views/admin/crawler/SystemMonitor.vue'),
        meta: {
          title: '爬虫监控',
          icon: 'monitor',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'task-console',
        name: 'TaskConsole',
        component: () => import('@/views/admin/crawler/TaskConsole.vue'),
        meta: {
          title: '任务控制台',
          icon: 'console',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'data-center',
        name: 'DataCenter',
        component: () => import('@/views/admin/crawler/DataCenter.vue'),
        meta: {
          title: '数据中心',
          icon: 'data-analysis',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'ip-pool',
        name: 'IpPoolManagement',
        component: () => import('@/views/admin/crawler/IpPoolManagement.vue'),
        meta: {
          title: 'IP池管理',
          icon: 'connection',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'headers',
        name: 'HeadersManagement',
        component: () => import('@/views/admin/crawler/HeadersManagement.vue'),
        meta: {
          title: '请求头管理',
          icon: 'tickets',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'task-monitor',
        name: 'TaskExecutionMonitor',
        component: () => import('@/views/admin/crawler/TaskExecutionMonitor.vue'),
        meta: {
          title: '任务执行监控',
          icon: 'monitor',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'official-info',
        name: 'OfficialInfoManagement',
        component: () => import('@/views/admin/crawler/OfficialInfoManagement.vue'),
        meta: {
          title: '官方信息管理',
          icon: 'link',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      }
    ]
  }
]

export default crawlerRoutes