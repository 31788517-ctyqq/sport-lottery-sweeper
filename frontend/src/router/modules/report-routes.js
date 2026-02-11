// 报告生成模块路由 - AI_WORKING: coder1 @1770224919 - 提取报告生成模块路由
const reportRoutes = [
  {
    path: 'reports',
    name: 'ReportGeneration',
    redirect: '/admin/reports/auto',
    meta: {
      title: '报告生成',
      icon: 'Memo',
      roles: ['admin', 'manager']
    },
    children: [
      {
        path: 'auto',
        name: 'AutoReports',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: {
          title: '自动报告',
          icon: 'document-checked',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'custom',
        name: 'CustomReports',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: {
          title: '自定义报告',
          icon: 'edit',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'templates',
        name: 'ReportTemplates',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: {
          title: '模板管理',
          icon: 'folder',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'distribution',
        name: 'ReportDistribution',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: {
          title: '报告分发',
          icon: 'position',
          roles: ['admin', 'manager']
        }
      }
    ]
  }
]

export default reportRoutes