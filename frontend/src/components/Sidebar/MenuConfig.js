// 侧边栏菜单配置
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
      { path: '/admin/users/list', text: '用户列表' },
      { path: '/admin/users/roles', text: '角色与权限' },
      { path: '/admin/users/departments', text: '部门管理' },
      { path: '/admin/users/profile', text: '个人中心' },
      { path: '/admin/users/logs', text: '操作日志' }
    ]
  },
  {
    name: 'AnalyticTools',
    text: '精算工具中心',
    icon: 'fas fa-calculator',
    children: [
      { path: '/admin/beidan-filter', text: '北单三维筛选器', icon: 'fas fa-filter' },
      { path: '/admin/beidan-betting-sim', text: '北单投注模拟', icon: 'fas fa-coins' }
    ]
  },
  {
    path: '/admin/match-data',
    text: '比赛数据管理',
    icon: 'fas fa-futbol'
  },
  {
    path: '/admin/data-source/overview',
    text: '数据源管理',
    icon: 'fas fa-link',
    children: [
      { path: '/admin/data-source/overview', text: '运行总览' },
      { path: '/admin/data-source/tasks', text: '任务中心' },
      { path: '/admin/data-source/assets', text: '数据资产中心' },
      { path: '/admin/data-source/config', text: '数据源配置' },
      { path: '/admin/data-source/ip-pool', text: 'IP池管理' },
      { path: '/admin/data-source/headers', text: '请求头管理' }
    ]
  },
  {
    name: 'DrawPrediction',
    path: '/admin/draw-prediction',
    text: '平局预测管理',
    icon: 'fas fa-balance-scale',
    children: [
      { path: '/admin/draw-prediction/ai-draw', text: '北单平局预测扫盘' },
      { path: '/admin/draw-prediction/poisson-11', text: '1-1比分预测扫盘' },
      { path: '/admin/draw-prediction/suggestion-center', text: '下注建议中心' },
      { path: '/admin/draw-prediction/killswitch', text: '风控与熔断监控' },
      { path: '/admin/draw-prediction/model-workbench', text: '模型工坊' }
    ]
  },
  {
    path: '/admin/system',
    text: '系统管理',
    icon: 'fas fa-cog'
  }
]

export default menuConfig
