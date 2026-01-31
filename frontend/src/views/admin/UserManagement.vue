<template>
  <div class="user-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>👥 用户管理</h3>
            <p class="subtitle">用户信息管理、权限配置和账户状态</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="showAddUserDialog">添加用户</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-input v-model="searchQuery" placeholder="搜索用户名/邮箱" @keyup.enter="searchUsers" />
        </el-col>
        <el-col :span="6">
          <el-select v-model="roleFilter" placeholder="角色筛选" style="width: 100%;" @change="filterUsers">
            <el-option label="全部角色" value="" />
            <el-option label="超级管理员" value="super_admin" />
            <el-option label="管理员" value="admin" />
            <el-option label="分析师" value="analyst" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 100%;" @change="filterUsers">
            <el-option label="全部状态" value="" />
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
            <el-option label="待审核" value="pending" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="searchUsers">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <!-- 用户表格 -->
      <el-table 
        :data="filteredUsers" 
        style="width: 100%" 
        stripe 
        @selection-change="handleSelectionChange"
        v-loading="loading"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150">
          <template #default="scope">
            <div class="user-cell">
              <el-avatar :size="30" :src="scope.row.avatar" />
              <span>{{ scope.row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="scope">
            <el-tag :type="getRoleType(scope.row.role)">
              {{ getRoleLabel(scope.row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastLoginAt" label="最后登录" width="180" />
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewUserDetails(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="editUser(scope.row)">编辑</el-button>
            <el-button 
              size="small" 
              :type="scope.row.status === 'active' ? 'warning' : 'success'"
              @click="toggleUserStatus(scope.row)"
            >
              {{ scope.row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" type="danger" @click="deleteUser(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalUsers"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: center;"
      />

      <!-- 用户详情对话框 -->
      <el-dialog v-model="detailDialogVisible" title="用户详情" width="600px">
        <div v-if="selectedUser" class="user-detail">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="头像">
              <el-avatar :size="60" :src="selectedUser.avatar" />
            </el-descriptions-item>
            <el-descriptions-item label="用户名">
              {{ selectedUser.username }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ selectedUser.email }}
            </el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag :type="getRoleType(selectedUser.role)">
                {{ getRoleLabel(selectedUser.role) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(selectedUser.status)">
                {{ getStatusLabel(selectedUser.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">
              {{ selectedUser.createdAt }}
            </el-descriptions-item>
            <el-descriptions-item label="最后登录">
              {{ selectedUser.lastLoginAt || '从未登录' }}
            </el-descriptions-item>
            <el-descriptions-item label="个人简介">
              {{ selectedUser.bio || '暂无简介' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-dialog>

      <!-- 用户编辑/添加对话框 -->
      <el-dialog 
        :title="editingUser ? '编辑用户' : '添加用户'" 
        v-model="editDialogVisible" 
        width="500px"
      >
        <el-form :model="userForm" :rules="userFormRules" ref="userFormRef" label-width="100px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="userForm.username" :disabled="!!editingUser" />
          </el-form-item>
          
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="userForm.email" />
          </el-form-item>
          
          <el-form-item label="角色" prop="role">
            <el-select v-model="userForm.role" placeholder="选择角色" style="width: 100%;">
              <el-option label="超级管理员" value="super_admin" />
              <el-option label="管理员" value="admin" />
              <el-option label="分析师" value="analyst" />
              <el-option label="普通用户" value="user" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="状态" prop="status">
            <el-select v-model="userForm.status" placeholder="选择状态" style="width: 100%;">
              <el-option label="启用" value="active" />
              <el-option label="禁用" value="inactive" />
              <el-option label="待审核" value="pending" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="个人简介">
            <el-input 
              v-model="userForm.bio" 
              type="textarea" 
              :rows="3"
              placeholder="输入个人简介（可选）"
            />
          </el-form-item>
          
          <el-form-item v-if="!editingUser" label="密码" prop="password">
            <el-input v-model="userForm.password" type="password" show-password />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUser">确定</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 响应式数据
const loading = ref(false)
const detailDialogVisible = ref(false)
const editDialogVisible = ref(false)
const selectedUser = ref(null)
const editingUser = ref(null)

// 表格数据
const users = ref([
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    role: 'super_admin',
    status: 'active',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f4c99b3a30486ab54e4jpeg.jpeg',
    createdAt: '2023-01-15 10:30:00',
    lastLoginAt: '2023-05-20 14:22:30',
    bio: '系统超级管理员'
  },
  {
    id: 2,
    username: 'analyst1',
    email: 'analyst1@example.com',
    role: 'analyst',
    status: 'active',
    avatar: 'https://cube.elemecdn.com/3/7c/3ea086c3c7e7a5c9e5c8c4c7c6c7ejpeg.jpeg',
    createdAt: '2023-02-20 09:15:00',
    lastLoginAt: '2023-05-20 11:45:12',
    bio: '数据分析专家'
  },
  {
    id: 3,
    username: 'user1',
    email: 'user1@example.com',
    role: 'user',
    status: 'active',
    avatar: 'https://cube.elemecdn.com/1/8e/74e4ce963bb9c1a82b5f34c1e7ec4jpeg.jpeg',
    createdAt: '2023-03-10 16:20:00',
    lastLoginAt: '2023-05-19 18:30:45',
    bio: '普通用户'
  },
  {
    id: 4,
    username: 'moderator',
    email: 'moderator@example.com',
    role: 'admin',
    status: 'inactive',
    avatar: 'https://cube.elemecdn.com/9/46/48e9f4c4b24e5d4e8c4c7c4c7c4cjpeg.jpeg',
    createdAt: '2023-01-25 11:45:00',
    lastLoginAt: '2023-05-18 09:15:30',
    bio: '内容审核员'
  }
])

// 筛选和分页数据
const filteredUsers = ref([...users.value])
const currentPage = ref(1)
const pageSize = ref(10)
const totalUsers = ref(users.value.length)
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')

// 用户表单
const userForm = reactive({
  username: '',
  email: '',
  role: 'user',
  status: 'active',
  bio: '',
  password: ''
})

const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ]
}

// 方法
const getRoleLabel = (role) => {
  const roles = {
    super_admin: '超级管理员',
    admin: '管理员',
    analyst: '分析师',
    user: '普通用户'
  }
  return roles[role] || role
}

const getRoleType = (role) => {
  const types = {
    super_admin: 'danger',
    admin: 'warning',
    analyst: 'primary',
    user: 'info'
  }
  return types[role] || 'info'
}

const getStatusLabel = (status) => {
  const statuses = {
    active: '启用',
    inactive: '禁用',
    pending: '待审核'
  }
  return statuses[status] || status
}

const getStatusType = (status) => {
  const types = {
    active: 'success',
    inactive: 'danger',
    pending: 'warning'
  }
  return types[status] || 'info'
}

const viewUserDetails = (user) => {
  selectedUser.value = user
  detailDialogVisible.value = true
}

const showAddUserDialog = () => {
  editingUser.value = null
  Object.assign(userForm, {
    username: '',
    email: '',
    role: 'user',
    status: 'active',
    bio: '',
    password: ''
  })
  editDialogVisible.value = true
}

const editUser = (user) => {
  editingUser.value = user
  Object.assign(userForm, {
    username: user.username,
    email: user.email,
    role: user.role,
    status: user.status,
    bio: user.bio || ''
  })
  editDialogVisible.value = true
}

const saveUser = async () => {
  // 这里应该调用实际的API保存用户
  if (editingUser.value) {
    // 更新现有用户
    Object.assign(editingUser.value, {
      email: userForm.email,
      role: userForm.role,
      status: userForm.status,
      bio: userForm.bio
    })
    ElMessage.success('用户信息更新成功')
  } else {
    // 添加新用户
    const newUser = {
      id: users.value.length + 1,
      username: userForm.username,
      email: userForm.email,
      role: userForm.role,
      status: userForm.status,
      bio: userForm.bio,
      avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f4c99b3a30486ab54e4jpeg.jpeg',
      createdAt: new Date().toLocaleString('zh-CN'),
      lastLoginAt: null
    }
    users.value.push(newUser)
    totalUsers.value = users.value.length
    ElMessage.success('用户添加成功')
  }
  
  editDialogVisible.value = false
  // 重新筛选用户列表
  applyFilters()
}

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const index = users.value.findIndex(u => u.id === user.id)
    if (index !== -1) {
      users.value.splice(index, 1)
      totalUsers.value = users.value.length
      applyFilters()
      ElMessage.success('用户删除成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除用户失败')
    }
  }
}

const toggleUserStatus = async (user) => {
  try {
    const newStatus = user.status === 'active' ? 'inactive' : 'active'
    await ElMessageBox.confirm(
      `确定要${user.status === 'active' ? '禁用' : '启用'}用户 "${user.username}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: user.status === 'active' ? 'warning' : 'success'
      }
    )
    
    user.status = newStatus
    ElMessage.success(`用户已${newStatus === 'active' ? '启用' : '禁用'}`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const searchUsers = () => {
  applyFilters()
}

const filterUsers = () => {
  applyFilters()
}

const resetFilters = () => {
  searchQuery.value = ''
  roleFilter.value = ''
  statusFilter.value = ''
  applyFilters()
}

const applyFilters = () => {
  let result = [...users.value]
  
  // 应用搜索
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(user => 
      user.username.toLowerCase().includes(query) || 
      user.email.toLowerCase().includes(query)
    )
  }
  
  // 应用角色筛选
  if (roleFilter.value) {
    result = result.filter(user => user.role === roleFilter.value)
  }
  
  // 应用状态筛选
  if (statusFilter.value) {
    result = result.filter(user => user.status === statusFilter.value)
  }
  
  filteredUsers.value = result
  totalUsers.value = result.length
}

const handleSelectionChange = (selection) => {
  console.log('选中的用户:', selection)
}

const handleSizeChange = (size) => {
  pageSize.value = size
  console.log(`每页 ${size} 条`)
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  console.log(`当前页: ${page}`)
}

// 初始化数据
onMounted(() => {
  applyFilters()
})
</script>

<style scoped>
.card-container {
  margin: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header > div:first-child h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-detail {
  padding: 20px 0;
}

:deep(.el-descriptions__header) {
  margin-bottom: 20px;
}
</style>