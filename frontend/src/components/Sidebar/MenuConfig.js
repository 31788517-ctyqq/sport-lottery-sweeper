// 侧边栏菜单配置 - 基于实际路由的统一配置
const menuConfig = [
  {
    path: '/admin/dashboard',
    text: '仪表盘',
    icon: 'fas fa-tachometer-alt'
  },
  {
    name: 'userManagement',
    path: '/admin/users/list',
    text: '用户管理',
    icon: 'fas fa-users',
    children: [
      {
        path: '/admin/users/list',
        text: '用户列表'
      },
      {
        path: '/admin/users/roles',
        text: '角色与权限'
      },
      {
        path: '/admin/users/departments',
        text: '部门管理'
      },
      {
        path: '/admin/users/profile',
        text: '个人中心'
      },
      {
        path: '/admin/users/logs',
        text: '操作日志'
      }
    ]
  },
  {
    name: 'AnalyticTools',
    text: '精算工具中心',
    icon: 'fas fa-calculator',
    children: [
      {
        path: '/admin/beidan-filter',
        text: '北单三维筛选器',
        icon: 'fas fa-filter'
      },
      {
        path: '/admin/beidan-betting-sim',
        text: '北单投注模拟',
        icon: 'fas fa-coins'
      }
    ]
  },
  {
    path: '/admin/match-data',
    text: '比赛管理',
    icon: 'fas fa-futbol'
  },
  {
    path: '/admin/data-source',
    text: '数据源管理',
    icon: 'fas fa-link'
  },
  {
    name: 'DrawPrediction',
    path: '/admin/draw-prediction',
    text: '平局预测管理',
    icon: 'fas fa-balance-scale',
    children: [
      {
        path: '/admin/draw-prediction/ai-draw',
        text: '北单平局预测扫盘'
      },
      {
        path: '/admin/draw-prediction/poisson-11',
        text: '1-1比分预测扫盘'
      }
    ]
  },
  {
    path: '/admin/system',
    text: '系统设置',
    icon: 'fas fa-cog'
  }
]

export default menuConfig
