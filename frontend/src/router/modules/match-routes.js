// 比赛数据管理模块路由
const matchRoutes = [
  // 嵌套在/admin下的比赛数据管理子路由
  {
    path: 'match-data',
    name: 'MatchDataManagement',
    redirect: '/admin/match-data/matches',
    meta: {
      title: '比赛数据管理',
      icon: 'Soccer',
      roles: ['admin', 'manager'],
      order: 4
    },
    children: [
      {
        path: 'matches',
        name: 'MatchDataMatches',
        component: () => import('@/views/admin/sp/CompetitionManagement.vue'),
        meta: {
          title: '比赛管理',
          icon: 'calendar',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: 'odds',
        name: 'OddsManagement',
        component: () => import('@/views/admin/sp/OddsManagement.vue'),
        meta: {
          title: '赔率管理',
          icon: 'trend-charts',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: 'schedule/jczq',
        name: 'JCZQSchedule',
        component: () => import('@/views/admin/sp/ScheduleManagement.vue'),
        props: { scheduleType: 'jczq' },
        meta: {
          title: '竞彩赛程',
          icon: 'calendar',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: 'schedule/bd',
        name: 'BDSchedule',
        component: () => import('@/views/admin/sp/ScheduleManagement.vue'),
        props: { scheduleType: 'bd' },
        meta: {
          title: '北单赛程',
          icon: 'calendar',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: 'leagues',
        name: 'LeagueManagement',
        component: () => import('@/views/admin/match/LeagueManagement.vue'),
        meta: {
          title: '联赛管理',
          icon: 'football',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      }
    ]
  }
]

export default matchRoutes