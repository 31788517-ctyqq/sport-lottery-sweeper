<template>
  <div class="backend-users-container">
    <el-card class="users-card" :body-style="{ padding: '0' }">
      <div class="card-header">
        <h3>后台用户管理</h3>
      </div>
      
      <!-- 搜索和控制区域 -->
      <div class="users-controls">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索用户名、真实姓名或邮箱"
              clearable
              class="search-input"
              @keyup.enter="handleSearch"
            />
          </el-col>
          <el-col :span="4">
            <el-select
              v-model="filters.role"
              placeholder="请选择角色"
              clearable
              class="role-selector"
              @change="handleSearch"
            >
              <el-option label="全部角色" value="" />
              <el-option label="超级管理员" value="super_admin" />
              <el-option label="管理员" value="admin" />
              <el-option label="内容审核员" value="moderator" />
              <el-option label="审计员" value="auditor" />
              <el-option label="运营人员" value="operator" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select
              v-model="filters.status"
              placeholder="请选择状态"
              clearable
              class="status-selector"
              @change="handleSearch"
            >
              <el-option label="全部状态" value="" />
              <el-option label="激活" value="active" />
              <el-option label="未激活" value="inactive" />
              <el-option label="暂停" value="suspended" />
              <el-option label="锁定" value="locked" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select
              v-model="filters.department"
              placeholder="请选择部门"
              clearable
              class="dept-selector"
              @change="handleSearch"
            >
              <el-option label="全部部门" value="" />
              <el-option label="运营部" value="运营部" />
              <el-option label="技术部" value="技术部" />
              <el-option label="客服部" value="客服部" />
              <el-option label="审计部" value="审计部" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="handleSearch" class="action-btn">
              查询
            </el-button>
            <el-button @click="handleReset" class="action-btn">
              重置
            </el-button>
            <el-button type="success" @click="handleCreate" class="action-btn">
              新建用户
            </el-button>
          </el-col>
        </el-row>
      </div>

      <!-- 操作按钮区域 -->
      <div class="action-bar">
        <el-button type="primary" @click="handleCreate">
          新建后台用户
        </el-button>
      </div>

      <!-- 表格区域 -->
      <div class="table-wrapper">
        <el-table
          :data="users" 
          stripe 
          style="width: 100%" 
          v-loading="loading"
          height="calc(100vh - 400px)"
          :header-cell-style="{background: '#f5f7fa', color: '#606266'}"
          class="modern-table"
        >
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="real_name" label="真实姓名" width="100" />
          <el-table-column prop="email" label="邮箱" width="180" />
          <el-table-column prop="role" label="角色" width="120">
            <template #default="scope">
              {{ getRoleText(scope.row.role) }}
            </template>
          </el-table-column>
          <el-table-column prop="department" label="部门" width="100">
            <template #default="scope">
              {{ scope.row.department || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              {{ getStatusText(scope.row.status) }}
            </template>
          </el-table-column>
          <el-table-column prop="two_factor_enabled" label="双因素认证" width="120">
            <template #default="scope">
              {{ scope.row.two_factor_enabled ? '已启用' : '未启用' }}
            </template>
          </el-table-column>
          <el-table-column prop="last_login_at" label="最后登录" width="160">
            <template #default="scope">
              {{ formatDate(scope.row.last_login_at) || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280" fixed="right">
            <template #default="scope">
              <el-button type="primary" size="small" @click="handleView(scope.row.id)">
                详情
              </el-button>
              <el-button type="warning" size="small" @click="handleEdit(scope.row.id)">
                编辑
              </el-button>
              <el-button type="info" size="small" @click="handleResetPassword(scope.row.id)">
                重置密码
              </el-button>
              <el-button 
                v-if="scope.row.role !== 'super_admin'"
                type="danger" 
                size="small" 
                @click="handleDelete(scope.row.id)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div v-if="users.length === 0" class="empty-state">
          <p>暂无后台用户数据</p>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getBackendUsers,
  getBackendUserDetail,
  createBackendUser,
  updateBackendUser,
  deleteBackendUser,
  resetBackendUserPassword,
  getBackendUserStats,
  getBackendUserOperationLogs,
  getBackendUserLoginLogs
} from '../../../api/modules/backendUsers'

export default {
  name: 'BackendUsers',
  setup() {
    const users = ref([])
    const stats = ref({})
    const loading = ref(false)
    const searchKeyword = ref('')
    const showUserDialog = ref(false)
    const showResetPasswordDialog = ref(false)
    const showLogDialog = ref(false)
    const dialogMode = ref('view') // 'view' | 'edit' | 'create'
    const currentUser = ref({})
    const resetPasswordUserId = ref(null)
    const logUserId = ref(null)
    
    // 日志相关
    const activeTab = ref('operation')
    const operationLogs = ref([])
    const loginLogs = ref([])
    
    const filters = reactive({
      role: '',
      status: '',
      department: ''
    })
    
    const logFilters = reactive({
      action: '',
      resource_type: '',
      page: 1,
      size: 10
    })
    
    const loginLogFilters = reactive({
      success: '',
      page: 1,
      size: 10
    })
    
    const operationPagination = reactive({
      page: 1,
      size: 10,
      total: 0,
      pages: 0
    })
    
    const loginPagination = reactive({
      page: 1,
      size: 10,
      total: 0,
      pages: 0
    })
    
    const pagination = reactive({
      page: 1,
      size: 20,
      total: 0,
      pages: 0
    })

    const resetPasswordForm = reactive({
      new_password: '',
      must_change_password: true
    })

    const dialogTitle = computed(() => {
      const titles = {
        view: '后台用户详情',
        edit: '编辑后台用户',
        create: '新建后台用户'
      }
      return titles[dialogMode.value]
    })

    const logDialogTitle = computed(() => {
      return `${currentUser.value.real_name || currentUser.value.username} 的日志详情`
    })

    const ipWhitelistText = computed({
      get() {
        if (Array.isArray(currentUser.value.login_allowed_ips)) {
          return currentUser.value.login_allowed_ips.join('\n')
        }
        return ''
      },
      set(value) {
        currentUser.value.login_allowed_ips = value.split('\n').filter(ip => ip.trim())
      }
    })

    // 加载用户列表
    const loadUsers = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.page,
          size: pagination.size,
          search: searchKeyword.value,
          role: filters.role,
          status: filters.status,
          department: filters.department
        }
        
        const response = await getBackendUsers(params)
        // 兼容多种响应格式：{data: {items: []}} 或直接返回数组
        if (response.data && response.data.items) {
          users.value = response.data.items || []
          pagination.total = response.data.total || 0
          pagination.pages = response.data.pages || 0
        } else if (Array.isArray(response.data)) {
          users.value = response.data
          pagination.total = response.data.length
          pagination.pages = 1
        } else if (response.data) {
          users.value = [response.data]
          pagination.total = 1
          pagination.pages = 1
        } else {
          users.value = []
          pagination.total = 0
          pagination.pages = 0
        }
      } catch (error) {
        console.error('加载后台用户列表失败:', error)
        ElMessage.error('加载后台用户列表失败')
      } finally {
        loading.value = false
      }
    }

    // 加载统计信息
    const loadStats = async () => {
      try {
        const response = await getBackendUserStats()
        if (response.data) {
          stats.value = response.data
        } else {
          stats.value = {}
        }
      } catch (error) {
        console.error('加载统计信息失败:', error)
        stats.value = {}
      }
    }

    // 搜索
    const handleSearch = () => {
      pagination.page = 1
      loadUsers()
    }

    // 重置
    const handleReset = () => {
      searchKeyword.value = ''
      filters.role = ''
      filters.status = ''
      filters.department = ''
      pagination.page = 1
      loadUsers()
    }

    // 分页大小改变
    const handleSizeChange = (size) => {
      pagination.size = size
      pagination.page = 1
      loadUsers()
    }

    // 分页
    const handlePageChange = (page) => {
      pagination.page = page
      loadUsers()
    }

    // 新建用户
    const handleCreate = () => {
      currentUser.value = {
        username: '',
        email: '',
        real_name: '',
        phone: '',
        role: 'operator',
        status: 'inactive',
        department: '',
        position: '',
        two_factor_enabled: false,
        login_allowed_ips: [],
        remarks: '',
        password: ''
      }
      dialogMode.value = 'create'
      showUserDialog.value = true
    }

    // 查看用户
    const handleView = async (userId) => {
      try {
        const response = await getBackendUserDetail(userId)
        currentUser.value = response.data || {}
        dialogMode.value = 'view'
        showUserDialog.value = true
      } catch (error) {
        console.error('获取用户详情失败:', error)
        alert('获取用户详情失败')
      }
    }

    // 编辑用户
    const handleEdit = async (userId) => {
      try {
        const response = await getBackendUserDetail(userId)
        currentUser.value = response.data || {}
        dialogMode.value = 'edit'
        showUserDialog.value = true
      } catch (error) {
        console.error('获取用户信息失败:', error)
        alert('获取用户信息失败')
      }
    }

    // 查看日志
    const handleViewLogs = async (userId) => {
      try {
        const response = await getBackendUserDetail(userId)
        currentUser.value = response.data
        logUserId.value = userId
        showLogDialog.value = true
        
        // 默认加载操作日志
        await loadOperationLogs()
      } catch (error) {
        console.error('获取用户信息失败:', error)
        alert('获取用户信息失败')
      }
    }

    // 加载操作日志
    const loadOperationLogs = async () => {
      try {
        const params = {
          page: operationPagination.page,
          size: operationPagination.size,
          action: logFilters.action,
          resource_type: logFilters.resource_type
        }
        
        const response = await getBackendUserOperationLogs(logUserId.value, params)
        if (response.data && response.data.items) {
          operationLogs.value = response.data.items || []
          operationPagination.total = response.data.total || 0
          operationPagination.pages = response.data.pages || 0
        } else if (Array.isArray(response.data)) {
          operationLogs.value = response.data
          operationPagination.total = response.data.length
          operationPagination.pages = 1
        } else {
          operationLogs.value = []
          operationPagination.total = 0
          operationPagination.pages = 0
        }
      } catch (error) {
        console.error('加载操作日志失败:', error)
        alert('加载操作日志失败')
      }
    }

    // 加载登录日志
    const loadLoginLogs = async () => {
      try {
        const params = {
          page: loginPagination.page,
          size: loginPagination.size,
          success: loginLogFilters.success === '' ? undefined : loginLogFilters.success === 'true'
        }
        
        const response = await getBackendUserLoginLogs(logUserId.value, params)
        if (response.data && response.data.items) {
          loginLogs.value = response.data.items || []
          loginPagination.total = response.data.total || 0
          loginPagination.pages = response.data.pages || 0
        } else if (Array.isArray(response.data)) {
          loginLogs.value = response.data
          loginPagination.total = response.data.length
          loginPagination.pages = 1
        } else {
          loginLogs.value = []
          loginPagination.total = 0
          loginPagination.pages = 0
        }
      } catch (error) {
        console.error('加载登录日志失败:', error)
        alert('加载登录日志失败')
      }
    }

    // 保存用户
    const handleSave = async () => {
      try {
        if (dialogMode.value === 'create') {
          await createBackendUser(currentUser.value)
          alert('创建成功')
        } else {
          await updateBackendUser(currentUser.value.id, currentUser.value)
          alert('保存成功')
        }
        closeDialog()
        loadUsers()
        loadStats()
      } catch (error) {
        console.error('保存失败:', error)
        alert(error.response?.data?.detail || '保存失败')
      }
    }

    // 删除用户
    const handleDelete = async (userId) => {
      try {
        await ElMessageBox.confirm('确定要删除该后台用户吗？', '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await deleteBackendUser(userId)
        ElMessage.success('删除成功')
        loadUsers()
        loadStats()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除失败:', error)
          ElMessage.error('删除失败')
        }
      }
    }

    // 重置密码
    const handleResetPassword = (userId) => {
      resetPasswordUserId.value = userId
      resetPasswordForm.new_password = ''
      resetPasswordForm.must_change_password = true
      showResetPasswordDialog.value = true
    }

    const confirmResetPassword = async () => {
      if (!resetPasswordForm.new_password) {
        alert('请输入新密码')
        return
      }
      
      try {
        await resetBackendUserPassword(resetPasswordUserId.value, resetPasswordForm)
        alert('密码重置成功')
        closeResetPasswordDialog()
      } catch (error) {
        console.error('重置密码失败:', error)
        alert(error.response?.data?.detail || '重置密码失败')
      }
    }

    // 关闭对话框
    const closeDialog = () => {
      showUserDialog.value = false
      currentUser.value = {}
    }

    const closeResetPasswordDialog = () => {
      showResetPasswordDialog.value = false
      resetPasswordUserId.value = null
    }

    const closeLogDialog = () => {
      showLogDialog.value = false
      logUserId.value = null
      operationLogs.value = []
      loginLogs.value = []
    }

    // 日志标签切换
    const switchTab = (tab) => {
      activeTab.value = tab
      if (tab === 'operation') {
        loadOperationLogs()
      } else if (tab === 'login') {
        loadLoginLogs()
      }
    }

    // 日志分页
    const handleLogPageChange = async (type, page) => {
      if (type === 'operation') {
        operationPagination.page = page
        await loadOperationLogs()
      } else if (type === 'login') {
        loginPagination.page = page
        await loadLoginLogs()
      }
    }

    // 格式化日期
    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleString('zh-CN')
    }

    // 获取角色文本
    const getRoleText = (role) => {
      const roleMap = {
        super_admin: '超级管理员',
        admin: '管理员',
        moderator: '内容审核员',
        auditor: '审计员',
        operator: '运营人员'
      }
      return roleMap[role] || role
    }

    // 获取状态文本
    const getStatusText = (status) => {
      const statusMap = {
        active: '激活',
        inactive: '未激活',
        suspended: '暂停',
        locked: '锁定'
      }
      return statusMap[status] || status
    }

    // 获取操作文本
    const getActionText = (action) => {
      const actionMap = {
        create: '创建',
        update: '更新',
        delete: '删除',
        change_password: '修改密码',
        reset_password: '重置密码'
      }
      return actionMap[action] || action
    }

    // 获取资源类型文本
    const getResourceTypeText = (resourceType) => {
      const resourceMap = {
        admin_user: '后台用户',
        match: '比赛',
        intelligence: '情报'
      }
      return resourceMap[resourceType] || resourceType
    }

    onMounted(() => {
      loadUsers()
      loadStats()
    })

    return {
      users,
      stats,
      loading,
      searchKeyword,
      filters,
      pagination,
      showUserDialog,
      dialogMode,
      currentUser,
      handleSearch,
      handleReset,
      handleSizeChange,
      handlePageChange,
      handleCreate,
      handleView,
      handleEdit,
      handleSave,
      handleDelete,
      closeDialog,
      formatDate,
      getRoleText,
      getStatusText
    }
  }
}
</script>

<style scoped>
.backend-users-container {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.users-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
}

.card-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.users-controls {
  padding: 20px;
  background: white;
  border-bottom: 1px solid #ebeef5;
}

.search-input {
  width: 100%;
}

.role-selector,
.status-selector,
.dept-selector {
  width: 100%;
}

.action-bar {
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  gap: 12px;
}

.action-btn {
  border-radius: 4px;
}

.table-wrapper {
  padding: 0;
}

.modern-table {
  border-radius: 0;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.pagination-wrapper {
  padding: 20px;
  background: white;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: center;
}
</style>