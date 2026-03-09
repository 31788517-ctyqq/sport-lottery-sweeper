<template>
  <div class="user-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">👥 用户管理</h1>
      <p class="page-description">管理系统用户、角色和权限分配</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      ❌ {{ error }}
      <button @click="error = null" class="close-error">×</button>
    </div>

    <!-- 快速操作工具栏 -->
    <div class="toolbar">
      <div class="search-box">
        <input 
          v-model="searchKeyword"
          type="text"
          placeholder="搜索用户..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">
          <span>🔍</span> 搜索
        </button>
      </div>
      
      <div class="filters">
        <select v-model="filters.role" @change="handleFilterChange">
          <option value="">全部角色</option>
          <option value="admin">管理员</option>
          <option value="moderator">版主</option>
          <option value="analyst">分析师</option>
          <option value="user">普通用户</option>
        </select>
        
        <select v-model="filters.status" @change="handleFilterChange">
          <option value="">全部状态</option>
          <option value="active">活跃</option>
          <option value="inactive">非活跃</option>
          <option value="suspended">暂停</option>
          <option value="pending">待激活</option>
        </select>
        
        <select v-model="filters.department" @change="handleFilterChange">
          <option value="">全部部门</option>
          <option value="management">管理层</option>
          <option value="analysis">分析部</option>
          <option value="operations">运营部</option>
          <option value="support">支持部</option>
        </select>
      </div>

      <div class="actions">
        <button class="action-btn primary" @click="createNewUser">
          <span>➕</span> 新增用户
        </button>
        <button class="action-btn secondary" @click="refreshUsers" :disabled="loading">
          <span>🔄</span> {{ loading ? '加载中...' : '刷新' }}
        </button>
        <button class="action-btn tertiary" @click="exportUserData" :disabled="loading">
          <span>📤</span> 导出用户
        </button>
        <button class="action-btn danger" @click="batchDeleteSelected" :disabled="!selectedUsers.length">
          <span>🗑️</span> 批量删除 ({{ selectedUsers.length }})
        </button>
      </div>
    </div>

    <!-- 用户统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon total">
          <i class="icon-total">👤</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">总用户数</div>
          <div class="stat-value">{{ stats.totalUsers }}</div>
          <div class="stat-change positive">+{{ stats.newThisMonth }} 本月新增</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon active">
          <i class="icon-active">⚡</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">活跃用户</div>
          <div class="stat-value">{{ stats.activeUsers }}</div>
          <div class="stat-change neutral">/{{ stats.totalUsers }} 总数</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon online">
          <i class="icon-online">🟢</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">在线用户</div>
          <div class="stat-value">{{ stats.onlineUsers }}</div>
          <div class="stat-change positive">+{{ stats.joinedToday }} 今日加入</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon roles">
          <i class="icon-roles">🏷️</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">角色数</div>
          <div class="stat-value">{{ stats.roleTypes }}</div>
          <div class="stat-change neutral">{{ stats.mostCommonRole }} 最多</div>
        </div>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="users-section">
      <div class="section-header">
        <h2>📋 用户列表</h2>
        <div class="users-stats">
          <span class="stat-item">显示: {{ filteredUsers.length }} 位</span>
          <span class="stat-item total">总计: {{ allUsers.length }} 位</span>
        </div>
      </div>
      
      <div class="users-table-container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <span>⏳ 加载中，请稍候...</span>
        </div>
        
        <!-- 空状态 -->
        <div v-else-if="!filteredUsers.length" class="empty-state">
          <span>📭 暂无用户数据</span>
        </div>
        
        <!-- 正常表格 -->
        <table v-else class="users-table">
          <thead>
            <tr>
              <th><input type="checkbox" @change="toggleSelectAll" /></th>
              <th>头像</th>
              <th>用户名</th>
              <th>姓名</th>
              <th>角色</th>
              <th>部门</th>
              <th>邮箱</th>
              <th>状态</th>
              <th>最后活动</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedUsers" :key="user.id" :class="{ selected: user.selected }">
              <td><input type="checkbox" v-model="user.selected" /></td>
              <td>
                <div class="avatar-cell">
                  <img :src="user.avatar" :alt="user.username" class="avatar" v-if="user.avatar" />
                  <div v-else class="avatar-placeholder">{{ user.firstName.charAt(0) }}</div>
                </div>
              </td>
              <td>{{ user.username }}</td>
              <td>{{ user.firstName }} {{ user.lastName }}</td>
              <td>
                <span class="role-badge" :class="user.role">
                  {{ roleLabels[user.role] }}
                </span>
              </td>
              <td>{{ departmentLabels[user.department] }}</td>
              <td>{{ user.email }}</td>
              <td>
                <span class="status-badge" :class="user.status">
                  {{ statusLabels[user.status] }}
                </span>
              </td>
              <td>{{ formatDateTime(user.lastActivity) }}</td>
              <td>
                <button class="action-btn view" @click="viewUser(user)">👁️</button>
                <button class="action-btn edit" @click="editUser(user)">✏️</button>
                <button class="action-btn reset-password" @click="resetPassword(user)">🔑</button>
                <button class="action-btn delete" @click="deleteUserHandler(user)">🗑️</button>
                <button v-if="user.status === 'suspended'" class="action-btn unlock" @click="unlockUserAccount(user)">
                  🔓 解锁
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <button 
          class="pagination-btn" 
          @click="prevPage" 
          :disabled="currentPage === 1"
        >
          上一页
        </button>
        <span class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
        <button 
          class="pagination-btn" 
          @click="nextPage" 
          :disabled="currentPage === totalPages"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 添加/编辑用户对话框 -->
    <div v-if="showUserModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingUser ? '编辑用户' : '新增用户' }}</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group half-width">
              <label>用户名 *</label>
              <input 
                v-model="currentUser.username" 
                type="text" 
                placeholder="输入用户名"
              />
            </div>
            
            <div class="form-group half-width">
              <label>邮箱 *</label>
              <input 
                v-model="currentUser.email" 
                type="email" 
                placeholder="输入邮箱"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>姓 *</label>
              <input 
                v-model="currentUser.firstName" 
                type="text" 
                placeholder="输入姓氏"
              />
            </div>
            
            <div class="form-group half-width">
              <label>名 *</label>
              <input 
                v-model="currentUser.lastName" 
                type="text" 
                placeholder="输入名字"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>角色 *</label>
              <select v-model="currentUser.role">
                <option value="user">普通用户</option>
                <option value="analyst">分析师</option>
                <option value="moderator">版主</option>
                <option value="admin">管理员</option>
              </select>
            </div>
            
            <div class="form-group half-width">
              <label>部门</label>
              <select v-model="currentUser.department">
                <option value="operations">运营部</option>
                <option value="analysis">分析部</option>
                <option value="management">管理层</option>
                <option value="support">支持部</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>电话</label>
              <input 
                v-model="currentUser.phone" 
                type="tel" 
                placeholder="输入电话号码"
              />
            </div>
            
            <div class="form-group half-width">
              <label>状态 *</label>
              <select v-model="currentUser.status">
                <option value="active">活跃</option>
                <option value="inactive">非活跃</option>
                <option value="suspended">暂停</option>
                <option value="pending">待激活</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>头像URL</label>
              <input 
                v-model="currentUser.avatar" 
                type="text" 
                placeholder="用户头像URL"
              />
            </div>
            
            <div class="form-group half-width">
              <label>入职日期</label>
              <input 
                v-model="currentUser.joinDate" 
                type="date"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label>个人简介</label>
            <textarea 
              v-model="currentUser.bio" 
              placeholder="用户个人简介"
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeModal">取消</button>
          <button 
            class="btn primary" 
            @click="saveUser"
            :disabled="!isValidUser"
          >
            {{ editingUser ? '更新' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 用户详情对话框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>用户详情 - {{ selectedUser.username }}</h3>
          <button class="close-btn" @click="closeDetailModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <div class="detail-label">头像</div>
            <div class="detail-value">
              <img :src="selectedUser.avatar" :alt="selectedUser.username" class="avatar-large" v-if="selectedUser.avatar" />
              <div v-else class="avatar-placeholder-large">{{ selectedUser.firstName.charAt(0) }}</div>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">用户名</div>
            <div class="detail-value">{{ selectedUser.username }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">姓名</div>
            <div class="detail-value">{{ selectedUser.firstName }} {{ selectedUser.lastName }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">角色</div>
            <div class="detail-value">
              <span class="role-badge" :class="selectedUser.role">
                {{ roleLabels[selectedUser.role] }}
              </span>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">部门</div>
            <div class="detail-value">{{ departmentLabels[selectedUser.department] }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">邮箱</div>
            <div class="detail-value">{{ selectedUser.email }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">电话</div>
            <div class="detail-value">{{ selectedUser.phone || '未填写' }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">状态</div>
            <div class="detail-value">
              <span class="status-badge" :class="selectedUser.status">
                {{ statusLabels[selectedUser.status] }}
              </span>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">入职日期</div>
            <div class="detail-value">{{ formatDate(selectedUser.joinDate) }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">最后活动</div>
            <div class="detail-value">{{ formatDateTime(selectedUser.lastActivity) }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">创建时间</div>
            <div class="detail-value">{{ formatDateTime(selectedUser.createdAt) }}</div>
          </div>
          <div class="detail-row full-width">
            <div class="detail-label">个人简介</div>
            <div class="detail-value">{{ selectedUser.bio || '无简介' }}</div>
          </div>
          <div class="detail-row full-width">
            <div class="detail-label">权限</div>
            <div class="detail-value">
              <div class="permissions-list">
                <div class="permission-header">
                  <p>该用户拥有的权限：</p>
                  <button class="btn secondary small" @click="showPermissionEdit = !showPermissionEdit">
                    {{ showPermissionEdit ? '取消编辑' : '编辑权限' }}
                  </button>
                </div>
                
                <div v-if="showPermissionEdit" class="permission-edit-section">
                  <div class="permission-category" v-for="(category, catIndex) in allPermissions" :key="catIndex">
                    <h4>{{ category.name }}</h4>
                    <div class="permission-items">
                      <label v-for="(perm, idx) in category.permissions" :key="idx" class="permission-checkbox">
                        <input 
                          type="checkbox" 
                          :value="perm.id" 
                          v-model="selectedUserPermissions"
                          :disabled="!canModifyPermissions"
                        />
                        {{ perm.name }} - {{ perm.description }}
                      </label>
                    </div>
                  </div>
                  
                  <div class="permission-actions">
                    <button class="btn secondary" @click="updateUserPermissions">更新权限</button>
                  </div>
                </div>
                
                <ul v-else>
                  <li v-for="permission in getUserPermissions(selectedUser.role)" :key="permission">{{ permission }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeDetailModal">关闭</button>
          <button class="btn primary" @click="editUser(selectedUser)">编辑</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  getUserList, 
  createUser, 
  updateUser, 
  deleteUser, 
  getUserStats,
  updateUserStatus,
  resetUserPassword,
  batchDeleteUsers,
  getUserRoles,
  unlockUser,
  getUserDepartments
} from '@/api/modules/users'

// 用户数据
const allUsers = ref([])
const loading = ref(false)
const error = ref(null)

// 搜索和筛选
const searchKeyword = ref('')
const filters = ref({
  role: '',
  status: '',
  department: ''
})

// 统计数据
const stats = ref({
  totalUsers: 0,
  newThisMonth: 0,
  activeUsers: 0,
  onlineUsers: 0,
  joinedToday: 0,
  roleTypes: 0,
  mostCommonRole: ''
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 用户模态框
const showUserModal = ref(false)
const editingUser = ref(null)
const currentUser = ref({
  id: null,
  username: '',
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  role: 'user',
  department: 'operations',
  status: 'pending',
  avatar: '',
  bio: '',
  joinDate: new Date(),
  lastActivity: new Date(),
  createdAt: new Date()
})

// 详情模态框
const showDetailModal = ref(false)
const selectedUser = ref({})

// 权限编辑相关
const showPermissionEdit = ref(false)
const selectedUserPermissions = ref([])
const canModifyPermissions = ref(true)

// 所有权限定义
const allPermissions = ref([
  {
    name: '用户管理',
    permissions: [
      { id: 'user_read', name: '查看用户', description: '可以查看所有用户信息' },
      { id: 'user_create', name: '创建用户', description: '可以创建新用户' },
      { id: 'user_update', name: '更新用户', description: '可以更新用户信息' },
      { id: 'user_delete', name: '删除用户', description: '可以删除用户' }
    ]
  },
  {
    name: '数据管理',
    permissions: [
      { id: 'data_read', name: '查看数据', description: '可以查看系统数据' },
      { id: 'data_create', name: '创建数据', description: '可以创建新数据' },
      { id: 'data_update', name: '更新数据', description: '可以更新数据' },
      { id: 'data_delete', name: '删除数据', description: '可以删除数据' }
    ]
  },
  {
    name: '系统管理',
    permissions: [
      { id: 'system_config', name: '系统配置', description: '可以修改系统配置' },
      { id: 'system_monitor', name: '系统监控', description: '可以查看系统监控信息' },
      { id: 'system_logs', name: '查看日志', description: '可以查看系统日志' }
    ]
  },
  {
    name: '内容管理',
    permissions: [
      { id: 'content_read', name: '查看内容', description: '可以查看所有内容' },
      { id: 'content_create', name: '创建内容', description: '可以创建新内容' },
      { id: 'content_update', name: '更新内容', description: '可以更新内容' },
      { id: 'content_delete', name: '删除内容', description: '可以删除内容' }
    ]
  }
])

// 计算属性
const filteredUsers = computed(() => {
  let users = [...allUsers.value]
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    users = users.filter(user => 
      user.username.toLowerCase().includes(keyword) ||
      user.firstName.toLowerCase().includes(keyword) ||
      user.lastName.toLowerCase().includes(keyword) ||
      user.email.toLowerCase().includes(keyword)
    )
  }
  
  if (filters.value.role) {
    users = users.filter(user => user.role === filters.value.role)
  }
  
  if (filters.value.status) {
    users = users.filter(user => user.status === filters.value.status)
  }
  
  if (filters.value.department) {
    users = users.filter(user => user.department === filters.value.department)
  }
  
  return users
})

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredUsers.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / pageSize.value)
})

const roleLabels = {
  admin: '管理员',
  moderator: '版主',
  analyst: '分析师',
  user: '普通用户'
}

const departmentLabels = {
  management: '管理层',
  analysis: '分析部',
  operations: '运营部',
  support: '支持部'
}

const statusLabels = {
  active: '活跃',
  inactive: '非活跃',
  suspended: '暂停',
  pending: '待激活'
}

const isValidUser = computed(() => {
  return currentUser.value.username.trim() !== '' && 
         currentUser.value.firstName.trim() !== '' &&
         currentUser.value.lastName.trim() !== '' &&
         currentUser.value.email.trim() !== '' &&
         currentUser.value.role !== '' &&
         currentUser.value.status !== ''
})

// 方法
const handleSearch = () => {
  console.log('搜索关键词:', searchKeyword.value)
  currentPage.value = 1
}

const handleFilterChange = () => {
  console.log('筛选条件改变:', filters.value)
  currentPage.value = 1
}

// 从API获取用户列表
const fetchUsers = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await getUserList({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      role: filters.value.role,
      status: filters.value.status,
      search: searchKeyword.value
    })
    
    allUsers.value = response.data.items || []
  } catch (err) {
    error.value = err.message || '获取用户列表失败'
    console.error('获取用户列表失败:', err)
  } finally {
    loading.value = false
  }
}

const refreshUsers = async () => {
  console.log('刷新用户列表')
  currentPage.value = 1
  await fetchUsers()
}

const createNewUser = () => {
  editingUser.value = null
  currentUser.value = {
    id: null,
    username: '',
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    role: 'user',
    department: 'operations',
    status: 'pending',
    avatar: '',
    bio: '',
    joinDate: new Date(),
    lastActivity: new Date(),
    createdAt: new Date()
  }
  showUserModal.value = true
}

const editUser = (user) => {
  editingUser.value = user
  currentUser.value = { ...user }
  showUserModal.value = true
}

const closeModal = () => {
  showUserModal.value = false
  editingUser.value = null
}

const saveUser = async () => {
  if (!isValidUser.value) return

  try {
    if (editingUser.value) {
      // 更新现有用户
      const response = await updateUser(editingUser.value.id, {
        ...currentUser.value,
        realName: `${currentUser.value.firstName} ${currentUser.value.lastName}`
      })
      const updatedUser = response.data
      
      // 更新本地数据
      const index = allUsers.value.findIndex(u => u.id === editingUser.value.id)
      if (index !== -1) {
        allUsers.value[index] = updatedUser
      }
    } else {
      // 添加新用户
      const response = await createUser({
        ...currentUser.value,
        realName: `${currentUser.value.firstName} ${currentUser.value.lastName}`
      })
      const newUser = response.data
      allUsers.value.unshift(newUser)
    }
    
    closeModal()
  } catch (err) {
    console.error('保存用户失败:', err)
    alert(`保存用户失败: ${err.message || '未知错误'}`)
  }
}

const viewUser = async (user) => {
  selectedUser.value = user
  // 获取用户权限信息
  try {
    const rolesResponse = await getUserRoles(user.id)
    selectedUserPermissions.value = rolesResponse.data.roles || []
  } catch (err) {
    console.error('获取用户角色失败:', err)
    selectedUserPermissions.value = []
  }
  showDetailModal.value = true
  showPermissionEdit.value = false
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedUser.value = {}
  showPermissionEdit.value = false
}

const deleteUserHandler = async (user) => {
  if (confirm(`确定要删除用户 "${user.username}" 吗？`)) {
    try {
      await deleteUser(user.id)
      // 从本地列表中移除用户
      const index = allUsers.value.indexOf(user)
      if (index !== -1) {
        allUsers.value.splice(index, 1)
      }
    } catch (error) {
      console.error('删除用户失败:', error)
      // 显示错误信息给用户
    }
  }
}

const resetPassword = async (user) => {
  try {
    await resetUserPassword(user.id, { newPassword: 'default123' }) // 这里应该是重置密码的逻辑
    alert(`用户: ${user.username} 的密码已重置`)
  } catch (error) {
    console.error('重置密码失败:', error)
    // 显示错误信息给用户
  }
}

const exportUserData = () => {
  console.log('导出用户数据...')
  // 在实际应用中，这里会导出数据到文件
  alert('正在导出用户数据...')
}

const toggleSelectAll = () => {
  const allSelected = paginatedUsers.value.every(user => user.selected)
  paginatedUsers.value.forEach(user => {
    user.selected = !allSelected
  })
}

// 批量操作
const selectedUsers = computed(() => {
  return paginatedUsers.value.filter(user => user.selected)
})

const batchDeleteSelected = async () => {
  if (selectedUsers.value.length === 0) {
    alert('请选择要删除的用户')
    return
  }
  
  if (confirm(`确定要删除选中的 ${selectedUsers.value.length} 个用户吗？`)) {
    try {
      const userIds = selectedUsers.value.map(user => user.id)
      await batchDeleteUsers(userIds)
      // 从本地列表中移除用户
      selectedUsers.value.forEach(user => {
        const index = allUsers.value.indexOf(user)
        if (index !== -1) {
          allUsers.value.splice(index, 1)
        }
      })
    } catch (err) {
      console.error('批量删除用户失败:', err)
      alert(`批量删除失败: ${err.message || '未知错误'}`)
    }
  }
}

const unlockUserAccount = async (user) => {
  try {
    await unlockUser(user.id)
    alert(`用户: ${user.username} 的账户已解锁`)
    // 更新本地状态
    user.status = 'active'
  } catch (err) {
    console.error('解锁用户失败:', err)
    alert(`解锁用户失败: ${err.message || '未知错误'}`)
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString()
}

const formatDateTime = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getUserPermissions = (role) => {
  const permissions = {
    admin: [
      '所有资源的完全访问权限',
      '用户管理权限',
      '系统配置权限',
      '数据导出权限',
      '日志查看权限'
    ],
    moderator: [
      '内容审核权限',
      '用户评论管理',
      '数据查看权限',
      '举报处理权限'
    ],
    analyst: [
      '数据分析权限',
      '预测模型查看',
      '统计报表权限',
      '数据导出权限（受限）'
    ],
    user: [
      '个人资料管理',
      '预测查看权限',
      '评论权限',
      '个人数据导出'
    ]
  }
  
  return permissions[role] || permissions.user
}

// 获取角色对应的权限ID列表
const getUserPermissionIds = (role) => {
  if (role === 'admin') {
    return allPermissions.value.flatMap(cat => cat.permissions.map(p => p.id))
  } else if (role === 'moderator') {
    return ['content_read', 'content_update', 'data_read']
  } else if (role === 'analyst') {
    return ['data_read', 'data_create']
  } else {
    return ['user_read']
  }
}

// 更新用户权限
const updateUserPermissions = () => {
  console.log(`更新用户 ${selectedUser.value.username} 的权限`, selectedUserPermissions.value)
  // 在实际应用中，这里会调用API更新用户权限
  alert(`已更新用户 ${selectedUser.value.username} 的权限`)
  showPermissionEdit.value = false
}

// 初始化数据
onMounted(async () => {
  console.log('User Management 页面已加载')
  await fetchUsers()
})
</script>

<style scoped>
.user-management-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

/* 错误消息样式 */
.error-message {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-error {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #b91c1c;
}

.close-error:hover {
  opacity: 0.7;
}

/* 加载和空状态样式 */
.loading-state,
.empty-state {
  padding: 40px;
  text-align: center;
  color: #6b7280;
  border-top: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
}

/* 批量操作按钮 */
.action-btn.danger {
  background: #ef4444;
  color: white;
}

.action-btn.danger:hover {
  background: #dc2626;
}

.action-btn.danger:disabled {
  background: #fca5a5;
  cursor: not-allowed;
}

.action-btn.unlock {
  background: #06b6d4;
  color: white;
  padding: 6px 10px;
}

.action-btn.unlock:hover {
  background: #0891b2;
}

/* 其他现有样式保持不变 */

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

/* 工具栏样式 */
.toolbar {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 300px;
}

.search-box input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-box input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-btn {
  padding: 10px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.search-btn:hover {
  background: #2563eb;
}

.filters {
  display: flex;
  gap: 12px;
}

.filters select {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: white;
  cursor: pointer;
}

.actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn.primary {
  background: #10b981;
  color: white;
}

.action-btn.primary:hover {
  background: #059669;
}

.action-btn.secondary {
  background: #6366f1;
  color: white;
}

.action-btn.secondary:hover {
  background: #4f46e5;
}

.action-btn.tertiary {
  background: #f59e0b;
  color: white;
}

.action-btn.tertiary:hover {
  background: #d97706;
}

.action-btn.view {
  background: #e5e7eb;
  color: #374151;
  padding: 6px 10px;
}

.action-btn.view:hover {
  background: #d1d5db;
}

.action-btn.edit {
  background: #94a3b8;
  color: white;
  padding: 6px 10px;
}

.action-btn.edit:hover {
  background: #64748b;
}

.action-btn.reset-password {
  background: #a78bfa;
  color: white;
  padding: 6px 10px;
}

.action-btn.reset-password:hover {
  background: #8b5cf6;
}

.action-btn.delete {
  background: #ef4444;
  color: white;
  padding: 6px 10px;
}

.action-btn.delete:hover {
  background: #dc2626;
}

/* 统计卡片样式 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.active {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.online {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-icon.roles {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.stat-change {
  font-size: 12px;
  font-weight: 500;
}

.stat-change.positive {
  color: #059669;
}

.stat-change.neutral {
  color: #6b7280;
}

/* 用户区样式 */
.users-section {
  background: white;
  border-radius: 12px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.section-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.users-stats {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #6b7280;
}

.users-table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.users-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.users-table tbody tr:hover {
  background-color: #f9fafb;
}

.users-table tbody tr.selected {
  background-color: #e0f2fe;
}

.avatar-cell {
  display: flex;
  align-items: center;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.role-badge {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.admin {
  background: #fef2f2;
  color: #b91c1c;
}

.role-badge.moderator {
  background: #fffbeb;
  color: #b45309;
}

.role-badge.analyst {
  background: #f0fdf4;
  color: #166534;
}

.role-badge.user {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #dcfce7;
  color: #166534;
}

.status-badge.inactive {
  background: #e5e7eb;
  color: #374151;
}

.status-badge.suspended {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.pending {
  background: #dbeafe;
  color: #1e40af;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-top: 1px solid #e5e7eb;
}

.pagination-btn {
  padding: 8px 16px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.pagination-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
}

.page-info {
  color: #6b7280;
  font-size: 14px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 600px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px rgba(0, 0, 0, 0.2);
}

.large-modal {
  width: 800px;
  max-width: 90vw;
  max-height: 80vh;
}

.avatar-large {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder-large {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 600;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #9ca3af;
}

.close-btn:hover {
  color: #6b7280;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group.half-width {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #1f2937;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.detail-row {
  display: flex;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.detail-row.full-width {
  flex-direction: column;
}

.detail-label {
  width: 120px;
  font-weight: 600;
  color: #374151;
}

.detail-value {
  flex: 1;
  color: #6b7280;
}

.permissions-list ul {
  padding-left: 20px;
  margin: 10px 0;
}

.permissions-list li {
  margin-bottom: 8px;
}

.permission-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.permission-edit-section {
  margin-top: 15px;
  padding: 15px;
  background-color: #f9fafb;
  border-radius: 8px;
}

.permission-category {
  margin-bottom: 20px;
}

.permission-category h4 {
  margin: 0 0 10px 0;
  padding-bottom: 5px;
  border-bottom: 1px solid #e5e7eb;
  color: #1f2937;
}

.permission-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.permission-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 0;
}

.permission-checkbox input[type="checkbox"] {
  margin: 0;
}

.permission-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.btn.cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn.cancel:hover {
  background: #e5e7eb;
}

.btn.primary {
  background: #3b82f6;
  color: white;
}

.btn.primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn.primary:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

.btn.secondary {
  background: #eab308;
  color: white;
}

.btn.secondary:hover {
  background: #ca8a04;
}

.btn.secondary.small {
  padding: 4px 8px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .user-management-container {
    padding: 16px;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .users-table {
    min-width: 800px;
  }
  
  .users-table th,
  .users-table td {
    padding: 8px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
  }
  
  .modal-content {
    width: 95vw;
  }
  
  .large-modal {
    width: 95vw;
  }
  
  .detail-row {
    flex-direction: column;
  }
  
  .detail-label {
    width: auto;
    margin-bottom: 4px;
  }
}
</style>