// 情报分析模块路由
const intelligenceRoutes = [
  // 嵌套在/admin下的情报分析子路由
  {
    path: 'intelligence',
    name: 'IntelligenceManagement',
    redirect: '/admin/intelligence/screening',
    meta: {
      title: '情报分析',
      icon: 'Document',
      roles: ['admin', 'manager']
    },
    children: [
      {
        path: 'screening',
        name: 'IntelligenceScreening',
        component: () => import('@/views/admin/intelligence/ScreeningManagement.vue'),
        meta: {
          title: '智能筛选',
          icon: 'document',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'collection',
        name: 'IntelligenceCollection',
        component: () => import('@/views/admin/intelligence/CollectionManagement.vue'),
        meta: {
          title: '采集管理',
          icon: 'document',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'model',
        name: 'IntelligenceModel',
        component: () => import('@/views/admin/intelligence/ModelManagement.vue'),
        meta: {
          title: '模型管理',
          icon: 'cpu',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'weight',
        name: 'IntelligenceWeight',
        component: () => import('@/views/admin/intelligence/WeightManagement.vue'),
        meta: {
          title: '权重管理',
          icon: 'scale-to-original',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'graph',
        name: 'IntelligenceGraph',
        component: () => import('@/views/admin/intelligence/GraphManagement.vue'),
        meta: {
          title: '图谱管理',
          icon: 'share',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'sentiment',
        name: 'SentimentAnalysis',
        component: () => import('@/views/admin/intelligence/SentimentAnalysis.vue'),
        meta: {
          title: '情感分析',
          icon: 'chat-dot-square',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'multimodal',
        name: 'MultimodalAnalysis',
        component: () => import('@/views/admin/intelligence/MultimodalAnalysis.vue'),
        meta: {
          title: '多模态分析',
          icon: 'camera',
          roles: ['admin', 'manager']
        }
      }
    ]
  }
]

export default intelligenceRoutes
