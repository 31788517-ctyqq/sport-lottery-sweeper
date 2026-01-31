<template>
  <div class="user-management-container">
    <!-- AI_WORKING: coder1 @2026-01-26T08:55:00Z - 替换el-card为BaseCard，应用标准化头部样式 -->
    <BaseCard class="user-management-card" icon="el-icon-user" title="用户管理">
    <!-- AI_DONE: coder1 @2026-01-26T08:55:00Z -->

      <!-- 搜索和筛选 -->
      <div class="search-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input 
              v-model="searchQuery" 
              placeholder="搜索用户名/邮箱" 
              clearable
              @keyup.enter="handleSearch"
            />
          </el-col>
          <el-col :span="6">
            <el-select 
              v-model="statusFilter" 
              placeholder="用户状态" 
              clearable
              @change="handleFilterChange"
            >
              <el-option label="启用" value="active" />
              <el-option label="禁用" value="inactive" />
              <el-option label="待激活" value="pending" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-col>
        </el-row>
      </div>

      <!-- 用户操作按钮 -->
      <div class="operation-section">
        <el-button type="primary" @click="addUser">新增用户</el-button>
        <el-button @click="batchDelete" :disabled="!multipleSelection.length">
          批量删除
        </el-button>
        <el-button @click="refreshData">刷新</el-button>
      </div>

      <!-- 用户列表 -->
      <el-table 
        :data="userData" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="row.role === 'admin' ? 'danger' : row.role === 'manager' ? 'warning' : 'info'"
            >
              {{ roleMap[row.role] || row.role }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ statusMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column prop="updated_at" label="更新时间" width="160" />
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button size="small" @click="editUser(row)">编辑</el-button>
            <el-button size="small" type="primary" @click="resetPassword(row)">重置密码</el-button>
            <el-button 
              size="small" 
              :type="row.status === 'active' ? 'warning' : 'success'"
              @click="toggleStatus(row)"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="pagination.currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pagination.pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
        />
      </div>
<!-- AI_WORKING: coder1 @2026-01-26T08:58:00Z - 替换闭合标签 -->
    </BaseCard>
<!-- AI_DONE: coder1 @2026-01-26T08:58:00Z -->

    <!-- 用户编辑对话框 -->
    <el-dialog 
      :title="dialogTitle" 
      v-model="dialogVisible" 
      width="500px"
      @close="closeDialog"
    >
      <el-form 
        :model="userForm" 
        :rules="userRules" 
        ref="userFormRef"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="!!userForm.id" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
            <el-option label="经理" value="manager" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="userForm.status" placeholder="请选择状态">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
            <el-option label="待激活" value="pending" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeDialog">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
// AI_WORKING: coder1 @2026-01-26T08:56:00Z - 添加BaseCard组件导入
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserList, createUser, updateUser, deleteUser, updateUserStatus, resetUserPassword } from '@/api/userManagement'
import BaseCard from '@/components/common/BaseCard.vue'
// AI_DONE: coder1 @2026-01-26T08:56:00Z

// AI_WORKING: coder1 @2026-01-26T08:57:00Z - 注册BaseCard组件
export default {
  name: 'UserManagement',
  components: {
    BaseCard
  },
  setup() {
// AI_DONE: coder1 @2026-01-26T08:57:00Z
    // 用户数据
    const userData = ref([])
    const loading = ref(false)
    
    // 搜索和筛选
    const searchQuery = ref('')
    const statusFilter = ref('')
    
    // 分页
    const pagination = reactive({
      currentPage: 1,
      pageSize: 10,
      total: 0
    })
    
    // 多选
    const multipleSelection = ref([])
    
    // 对话框
    const dialogVisible = ref(false)
    const dialogTitle = ref('')
    const userForm = reactive({
      id: null,
      username: '',
      email: '',
      role: 'user',
      status: 'active'
    })
    
    // 表单验证规则
    const userRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '长度在3到20个字符', trigger: 'blur' }
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
      ]
    }
    
    // 角色和状态映射
    const roleMap = {
      user: '普通用户',
      admin: '管理员',
      manager: '经理'
    }
    
    const statusMap = {
      active: '启用',
      inactive: '禁用',
      pending: '待激活'
    }
    
    // 获取用户列表
    const getUserListData = async () => {
      loading.value = true
      
      try {
        const params = {
          page: pagination.currentPage,
          size: pagination.pageSize
        }
        
        if (searchQuery.value) {
          params.search = searchQuery.value
        }
        
        if (statusFilter.value) {
          params.status = statusFilter.value
        }
        
        const response = await getUserList(params)
        const result = response.data
        
        userData.value = result.users || []
        pagination.total = result.total || 0
      } catch (error) {
        console.error('获取用户列表失败:', error)
        ElMessage.error('获取用户列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 刷新数据
    const refreshData = () => {
      pagination.currentPage = 1
      getUserListData()
    }
    
    // 搜索处理
    const handleSearch = () => {
      pagination.currentPage = 1
      getUserListData()
    }
    
    // 筛选处理
    const handleFilterChange = () => {
      handleSearch()
    }
    
    // 重置筛选
    const resetFilters = () => {
      searchQuery.value = ''
      statusFilter.value = ''
      handleSearch()
    }
    
    // 表格多选处理
    const handleSelectionChange = (val) => {
      multipleSelection.value = val
    }
    
    // 分页大小改变
    const handleSizeChange = (val) => {
      pagination.pageSize = val
      pagination.currentPage = 1
      getUserListData()
    }
    
    // 当前页改变
    const handleCurrentChange = (val) => {
      pagination.currentPage = val
      getUserListData()
    }
    
    // 添加用户
    const addUser = () => {
      dialogTitle.value = '新增用户'
      Object.assign(userForm, {
        id: null,
        username: '',
        email: '',
        role: 'user',
        status: 'active'
      })
      dialogVisible.value = true
    }
    
    // 编辑用户
    const editUser = (row) => {
      dialogTitle.value = '编辑用户'
      Object.assign(userForm, { ...row })
      dialogVisible.value = true
    }
    
    // 重置密码
    const resetPassword = async (row) => {
      try {
        await ElMessageBox.confirm(
          `确定要重置用户 "${row.username}" 的密码吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 调用API重置密码
        await resetUserPassword(row.id, '123456') // 示例密码，实际应用中应该生成随机密码
        ElMessage.success(`用户 "${row.username}" 的密码已重置`)
      } catch (error) {
        console.log('取消重置')
      }
    }
    
    // 切换用户状态
    const toggleStatus = async (row) => {
      const newStatus = row.status === 'active' ? 'inactive' : 'active'
      const actionText = newStatus === 'active' ? '启用' : '禁用'
      
      try {
        await ElMessageBox.confirm(
          `确定要${actionText}用户 "${row.username}" 吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 调用API更新用户状态
        await updateUserStatus(row.id, newStatus)
        row.status = newStatus
        ElMessage.success(`用户 "${row.username}" 已${actionText}`)
      } catch (error) {
        console.log(`取消${actionText}`)
      }
    }
    
    // 批量删除
    const batchDelete = async () => {
      if (!multipleSelection.value.length) {
        ElMessage.warning('请至少选择一项')
        return
      }
      
      const ids = multipleSelection.value.map(user => user.id)
      
      try {
        await ElMessageBox.confirm(
          `确定要删除选中的 ${multipleSelection.value.length} 个用户吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'danger'
          }
        )
        
        // 调用API删除用户
        const promises = ids.map(id => deleteUser(id))
        await Promise.all(promises)
        
        ElMessage.success(`已删除 ${multipleSelection.value.length} 个用户`)
        refreshData()
      } catch (error) {
        console.log('取消删除')
      }
    }
    
    // 提交表单
    const submitForm = async () => {
      try {
        if (userForm.id) {
          // 更新用户
          await updateUser(userForm.id, userForm)
          ElMessage.success('用户更新成功')
        } else {
          // 创建用户
          await createUser(userForm)
          ElMessage.success('用户创建成功')
        }
        
        dialogVisible.value = false
        refreshData()
      } catch (error) {
        console.error('提交表单失败:', error)
        ElMessage.error(error.message || '操作失败')
      }
    }
    
    // 关闭对话框
    const closeDialog = () => {
      dialogVisible.value = false
    }
    
    // 获取状态类型
    const getStatusType = (status) => {
      switch (status) {
        case 'active':
          return 'success'
        case 'inactive':
          return 'danger'
        case 'pending':
          return 'warning'
        default:
          return 'info'
      }
    }
    
    // 初始化
    onMounted(() => {
      getUserListData()
    })
    
    return {
      userData,
      loading,
      searchQuery,
      statusFilter,
      pagination,
      multipleSelection,
      dialogVisible,
      dialogTitle,
      userForm,
      userRules,
      roleMap,
      statusMap,
      getUserListData,
      refreshData,
      handleSearch,
      handleFilterChange,
      resetFilters,
      handleSelectionChange,
      handleSizeChange,
      handleCurrentChange,
      addUser,
      editUser,
      resetPassword,
      toggleStatus,
      batchDelete,
      submitForm,
      closeDialog,
      getStatusType
    }
  }
}
</script>

<style scoped>
.user-management-container {
  padding: 20px;
}

.user-management-card {
  min-height: 600px;
}

/* AI_WORKING: coder1 @2026-01-26T08:59:00Z - 移除不再使用的card-header样式 */
/* AI_DONE: coder1 @2026-01-26T08:59:00Z */

.search-section {
  margin-bottom: 20px;
}

.operation-section {
  margin-bottom: 20px;
}

.pagination-section {
  margin-top: 20px;
  text-align: right;
}

.dialog-footer {
  text-align: right;
}
</style>