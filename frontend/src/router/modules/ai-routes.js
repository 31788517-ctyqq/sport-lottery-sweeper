// AI服务管理模块路由
const aiRoutes = [
  // 嵌套在/admin下的AI服务管理子路由
  {
    path: 'ai-services',
    name: 'AIServiceManagement',
    redirect: '/admin/ai-services/local',
    meta: {
      title: 'AI服务管理',
      icon: 'ChatLineRound',
      roles: ['admin', 'manager']
    },
    children: [
      {
        path: 'local',
        name: 'LocalAIService',
        component: () => import('@/views/admin/ai-services/LocalAIService.vue'),
        meta: {
          title: '本地AI服务',
          icon: 'office-building',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'remote',
        name: 'RemoteAIService',
        component: () => import('@/views/admin/ai-services/RemoteAIService.vue'),
        meta: {
          title: '远程AI服务',
          icon: 'position',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'costs',
        name: 'CostMonitoring',
        component: () => import('@/views/admin/ai-services/CostMonitoring.vue'),
        meta: {
          title: '成本监控',
          icon: 'wallet',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'agents',
        name: 'AgentManagement',
        component: () => import('@/views/admin/ai-services/AgentManagement.vue'),
        meta: {
          title: '智能体管理',
          icon: 'avatar',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'models',
        name: 'ModelManagement',
        component: () => import('@/views/admin/ai-services/ModelManagement.vue'),
        meta: {
          title: '预测模型管理',
          icon: 'data-analysis',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'conversation',
        name: 'ConversationAssistant',
        component: () => import('@/views/admin/ai-services/ConversationAssistant.vue'),
        meta: {
          title: '对话助手',
          icon: 'chat-line',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'config',
        name: 'ConfigManagement',
        component: () => import('@/views/admin/ai-services/ConfigManagement.vue'),
        meta: {
          title: '配置管理',
          icon: 'setting',
          roles: ['admin', 'manager']
        }
      }
    ]
  }
]

export default aiRoutes