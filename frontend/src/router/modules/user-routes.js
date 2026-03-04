// 用户管理模块路由 - AI_WORKING: coder1 @1770223796 - 移除独立路由，仅保留/admin下的子路由定义
const userRoutes = [
  // 嵌套在/admin下的用户管理子路由
  {
    path: 'users',
    name: 'UserManagement',
    redirect: '/admin/users/list',
    meta: {
      title: '用户管理',
      icon: 'UserFilled',
      roles: ['admin'],
      order: 2
    },
    children: [
      {
        path: 'list',
        name: 'UserList',
        component: () => import('@/views/admin/users/UserList.vue'),
        meta: {
          title: '用户列表',
          icon: 'User',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: 'roles',
        name: 'RolePermission',
        component: () => import('@/views/admin/users/RolePermission.vue'),
        meta: {
          title: '角色与权限',
          icon: 'Key',
          roles: ['admin'],
          keepAlive: true
        }
      },
      {
        path: 'departments',
        name: 'DepartmentManagement',
        component: () => import('@/views/admin/users/DepartmentManagement.vue'),
        meta: {
          title: '部门管理',
          icon: 'OfficeBuilding',
          roles: ['admin'],
          keepAlive: true
        }
      },
      {
        path: 'profile',
        name: 'UserProfile',
        component: () => import('@/views/admin/users/UserProfile.vue'),
        meta: {
          title: '个人中心',
          icon: 'Avatar',
          roles: ['admin', 'manager'],
          keepAlive: false
        }
      },
      {
        path: 'profiles',
        name: 'UserProfileManagement',
        component: () => import('@/views/admin/users/UserProfileManagement.vue'),
        meta: {
        title: '用户画像管理',
          icon: 'User',
          roles: ['admin'],
          keepAlive: true
        }
      },
      {
        path: 'logs',
        name: 'OperationLog',
        component: () => import('@/views/admin/users/OperationLog.vue'),
        meta: {
          title: '操作日志',
          icon: 'Document',
          roles: ['admin'],
          keepAlive: true
        }
      }
    ]
  }
]

export default userRoutes
// AI_DONE: coder1 @1770223796