// 智能决策模块路由
const decisionRoutes = [
  // 嵌套在/admin下的智能决策子路由
  {
    path: 'intelligent-decision',
    name: 'IntelligentDecision',
    redirect: '/admin/intelligent-decision/hedging',
    meta: {
      title: '智能决策',
      icon: 'Management',
      roles: ['admin', 'manager']
    },
    children: [
      {
        path: 'hedging',
        name: 'HedgingManagement',
        component: () => import('@/views/admin/hedging/HedgingManagement.vue'),
        meta: {
          title: '对冲策略管理',
          icon: 'money',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'recommendations',
        name: 'RecommendationSystem',
        component: () => import('@/views/admin/intelligent-decision/RecommendationManagement.vue'),
        meta: {
          title: '推荐系统管理',
          icon: 'star',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'risk-control',
        name: 'RiskControl',
        component: () => import('@/views/admin/intelligent-decision/RiskControlManagement.vue'),
        meta: {
          title: '风险控制',
          icon: 'lock',
          roles: ['admin', 'manager']
        }
      }
    ]
  }
]

export default decisionRoutes