import Layout from '@/layout/index.vue'

// 用户管理相关的异步组件
const UserList = () => import('@/views/admin/users/UserList.vue')
const RolePermission = () => import('@/views/admin/users/RolePermission.vue')
const DepartmentManagement = () => import('@/views/admin/users/DepartmentManagement.vue')
const UserProfile = () => import('@/views/admin/users/UserProfile.vue')
const OperationLog = () => import('@/views/admin/users/OperationLog.vue')

const usersRouter = [
  {
    path: '/admin/users',
    component: Layout,
    redirect: '/admin/users/list',
    meta: {
      title: '用户管理',
      icon: 'UserFilled',
      order: 2,
      breadcrumb: false
    },
    children: [
      {
        path: 'list',
        name: 'UserList',
        component: UserList,
        meta: {
          title: '用户列表',
          icon: 'User',
          keepAlive: true,
          affix: false
        }
      },
      {
        path: 'roles',
        name: 'RolePermission',
        component: RolePermission,
        meta: {
          title: '角色与权限',
          icon: 'Key',
          keepAlive: true,
          affix: false
        }
      },
      {
        path: 'departments',
        name: 'DepartmentManagement',
        component: DepartmentManagement,
        meta: {
          title: '部门管理',
          icon: 'OfficeBuilding',
          keepAlive: true,
          affix: false
        }
      },
      {
        path: 'profile',
        name: 'UserProfile',
        component: UserProfile,
        meta: {
          title: '个人中心',
          icon: 'Avatar',
          keepAlive: false,
          affix: false
        }
      },
      {
        path: 'logs',
        name: 'OperationLog',
        component: OperationLog,
        meta: {
          title: '操作日志',
          icon: 'Document',
          keepAlive: true,
          affix: false
        }
      }
    ]
  }
]

export default usersRouter