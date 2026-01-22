<template>
  <div class="frontend-users-container">
    <el-card class="users-card" :body-style="{ padding: '0' }">
      <div class="card-header">
        <h3>前台用户管理</h3>
      </div>
      
      <!-- 搜索和控制区域 -->
      <div class="users-controls">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索用户名、邮箱或昵称"
              clearable
              class="search-input"
            />
          </el-col>
          <el-col :span="4">
            <el-select
              v-model="filters.status"
              placeholder="请选择状态"
              clearable
              class="status-selector"
            >
              <el-option label="全部状态" value="" />
              <el-option label="活跃" value="active" />
              <el-option label="未激活" value="inactive" />
              <el-option label="暂停" value="suspended" />
              <el-option label="禁用" value="banned" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select
              v-model="filters.user_type"
              placeholder="请选择类型"
              clearable
              class="type-selector"
            >
              <el-option label="全部类型" value="" />
              <el-option label="普通用户" value="normal" />
              <el-option label="高级用户" value="premium" />
              <el-option label="分析师" value="analyst" />
            </el-select>
          </el-col>
          <el-col :span="10">
            <el-button type="primary" @click="handleSearch" class="action-btn">
              查询
            </el-button>
            <el-button @click="handleReset" class="action-btn">
              重置
            </el-button>
            <el-button type="success" @click="refreshData" class="action-btn">
              刷新
            </el-button>
          </el-col>
        </el-row>
      </div>
      
      <!-- 操作按钮区域 -->
      <div class="action-bar">
    <el-button type="primary" @click="handleCreate">
      新建用户
    </el-button>
    <el-button 
      v-if="selectedUsers.length > 0"
      type="danger" 
      @click="handleBatchDelete"
    >
          批量删除 ({{ selectedUsers.length }})
        </el-button>
      </div>

      <!-- 表格区域 -->
      <div class="table-wrapper">
        <el-table
          :data="tableData" 
          stripe 
          style="width: 100%" 
          v-loading="loading"
          height="calc(100vh - 320px)"
          :header-cell-style="{background: '#f5f7fa', color: '#606266'}"
          class="modern-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="email" label="邮箱" width="180" />
          <el-table-column prop="nickname" label="昵称" width="120">
            <template #default="scope">
              {{ scope.row.nickname || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="user_type" label="用户类型" width="100">
            <template #default="scope">
              {{ getUserTypeText(scope.row.user_type) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              {{ getStatusText(scope.row.status) }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="注册时间" width="160">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="last_login_at" label="最后登录" width="160">
            <template #default="scope">
              {{ formatDate(scope.row.last_login_at) || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="scope">
              <el-button type="primary" size="small" @click="handleView(scope.row.id)">
                查看
              </el-button>
              <el-button type="warning" size="small" @click="handleEdit(scope.row.id)">
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div v-if="tableData.length === 0" class="empty-state">
          <p>暂无用户数据</p>
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

    <!-- 用户详情/编辑对话框 -->
    <div v-if="showUserDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>{{ dialogMode === 'view' ? '用户详情' : '编辑用户' }}</h3>
          <button class="close-btn" @click="closeDialog">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="currentUser.username" :disabled="dialogMode === 'view'" />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input v-model="currentUser.email" :disabled="dialogMode === 'view'" />
          </div>
          <div class="form-group">
            <label>昵称</label>
            <input v-model="currentUser.nickname" :disabled="dialogMode === 'view'" />
          </div>
          <div class="form-group">
            <label>用户类型</label>
            <select v-model="currentUser.user_type" :disabled="dialogMode === 'view'">
              <option value="normal">普通用户</option>
              <option value="premium">高级用户</option>
              <option value="analyst">分析师</option>
            </select>
          </div>
          <div class="form-group">
            <label>状态</label>
            <select v-model="currentUser.status" :disabled="dialogMode === 'view'">
              <option value="active">活跃</option>
              <option value="inactive">未激活</option>
              <option value="suspended">暂停</option>
              <option value="banned">禁用</option>
            </select>
          </div>
        </div>
        <div class="dialog-footer">
          <button v-if="dialogMode === 'edit'" class="btn-primary" @click="handleSave">保存</button>
          <button class="btn-secondary" @click="closeDialog">{{ dialogMode === 'view' ? '关闭' : '取消' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getFrontendUsers,
  getFrontendUserDetail,
  updateFrontendUser,
  deleteFrontendUser,
  getFrontendUserStats,
  batchDeleteUsers,
  batchUpdateUserStatus
} from '../../../api/modules/frontendUsers'

export default {
  name: 'FrontendUsers',
  setup() {
    const tableData = ref([]) // Element Plus表格数据
    const stats = ref({})
    const loading = ref(false)
    const searchKeyword = ref('')
    const selectedUsers = ref([])
    const showUserDialog = ref(false)
    const dialogMode = ref('view') // 'view' | 'edit'
    const currentUser = ref({})
    
    const filters = reactive({
      status: '',
      user_type: ''
    })
    
    const pagination = reactive({
      page: 1,
      size: 20,
      total: 0,
      pages: 0
    })

    // 加载用户列表
    const loadUsers = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.page,
          size: pagination.size,
          search: searchKeyword.value,
          status: filters.status,
          user_type: filters.user_type
        }
        
        const response = await getFrontendUsers(params)
        // 注意：由于响应拦截器的处理，response已经是data对象
        // 我们的模拟数据返回格式是 { data: { items: [], total: 0, pages: 0 } }
        if (response && response.data) {
          // 检查是否是我们的模拟数据格式
          if (response.data.items !== undefined) {
            tableData.value = response.data.items || []
            pagination.total = response.data.total || 0
            pagination.pages = response.data.pages || 0
          } else {
            // 兼容其他可能的响应格式
            tableData.value = response.items || response.data || []
            pagination.total = response.total || 0
            pagination.pages = response.pages || 1
          }
        }
      } catch (error) {
        console.error('加载用户列表失败:', error)
        alert('加载用户列表失败')
      } finally {
        loading.value = false
      }
    }

    // 加载统计信息
    const loadStats = async () => {
      try {
    const response = await getFrontendUserStats()
    // 注意：由于响应拦截器的处理，response已经是data对象
    if (response) {
      // 检查是否是我们的模拟数据格式 { data: { data: {...} } }
      if (response.data && response.data.data) {
        stats.value = response.data.data
      } else if (response.data) {
        // 兼容其他可能的响应格式
        stats.value = response.data
      } else {
        stats.value = response
      }
    }
      } catch (error) {
        console.error('加载统计信息失败:', error)
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
      filters.status = ''
      filters.user_type = ''
      pagination.page = 1
      loadUsers()
    }

    // 表格多选处理
    const handleSelectionChange = (selection) => {
      selectedUsers.value = selection.map(item => item.id)
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

    // 刷新数据
    const refreshData = () => {
      loadUsers()
      loadStats()
    }

    // 查看用户
    const handleView = async (userId) => {
      try {
        const response = await getFrontendUserDetail(userId)
        // 注意：由于响应拦截器的处理，response已经是data对象
        currentUser.value = response.data || response
        dialogMode.value = 'view'
        showUserDialog.value = true
      } catch (error) {
        console.error('获取用户详情失败:', error)
        ElMessage.error('获取用户详情失败')
      }
    }

    // 编辑用户
    const handleEdit = async (userId) => {
      try {
        const response = await getFrontendUserDetail(userId)
        // 注意：由于响应拦截器的处理，response已经是data对象
        currentUser.value = response.data || response
        dialogMode.value = 'edit'
        showUserDialog.value = true
      } catch (error) {
        console.error('获取用户信息失败:', error)
        ElMessage.error('获取用户信息失败')
      }
    }

    // 保存用户
    const handleSave = async () => {
      try {
        await updateFrontendUser(currentUser.value.id, currentUser.value)
        ElMessage.success('保存成功')
        closeDialog()
        loadUsers()
      } catch (error) {
        console.error('保存失败:', error)
        ElMessage.error('保存失败')
      }
    }

    // 新建用户（暂时显示提示）
    const handleCreate = () => {
      ElMessage.info('新建用户功能开发中...')
    }

    // 删除用户
    const handleDelete = async (userId) => {
      try {
        await ElMessageBox.confirm('确定要删除该用户吗？', '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await deleteFrontendUser(userId)
        ElMessage.success('删除成功')
        loadUsers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除失败:', error)
          ElMessage.error('删除失败')
        }
      }
    }

    // 批量更新状态
    const handleBatchUpdateStatus = async (status) => {
      if (selectedUsers.value.length === 0) return
      if (!confirm(`确定要将选中的 ${selectedUsers.value.length} 个用户设置为${status}吗？`)) return
      
      try {
        await batchUpdateUserStatus(selectedUsers.value, status)
        alert('批量更新成功')
        selectedUsers.value = []
        showBatchActions.value = false
        loadUsers()
      } catch (error) {
        console.error('批量更新失败:', error)
        alert('批量更新失败')
      }
    }

    // 批量删除
    const handleBatchDelete = async () => {
      if (selectedUsers.value.length === 0) return
      
      try {
        await ElMessageBox.confirm(`确定要删除选中的 ${selectedUsers.value.length} 个用户吗？`, '确认批量删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await batchDeleteUsers(selectedUsers.value)
        ElMessage.success('批量删除成功')
        selectedUsers.value = []
        loadUsers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('批量删除失败:', error)
          ElMessage.error('批量删除失败')
        }
      }
    }

    // 关闭对话框
    const closeDialog = () => {
      showUserDialog.value = false
      currentUser.value = {}
    }

    // 格式化日期
    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleString('zh-CN')
    }

    // 获取用户类型文本
    const getUserTypeText = (type) => {
      const typeMap = {
        normal: '普通用户',
        premium: '高级用户',
        analyst: '分析师'
      }
      return typeMap[type] || type
    }

    // 获取状态文本
    const getStatusText = (status) => {
      const statusMap = {
        active: '活跃',
        inactive: '未激活',
        suspended: '暂停',
        banned: '禁用'
      }
      return statusMap[status] || status
    }

    onMounted(() => {
      loadUsers()
      loadStats()
    })

    return {
      tableData,
      stats,
      searchKeyword,
      filters,
      pagination,
      selectedUsers,
      showUserDialog,
      dialogMode,
      currentUser,
      handleSearch,
      handleReset,
      handleSelectionChange,
      handleSizeChange,
      handlePageChange,
      refreshData,
      handleView,
      handleEdit,
      handleSave,
      handleDelete,
      handleBatchDelete,
      closeDialog,
      formatDate,
      getUserTypeText,
      getStatusText
    }
  }
}
</script>

<style scoped>
.frontend-users-container {
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

.status-selector,
.type-selector {
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

.dialog-overlay {
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

.dialog-content {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
}

.dialog-header {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #909399;
  line-height: 1;
}

.dialog-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #606266;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.dialog-footer {
  padding: 15px 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-primary,
.btn-secondary {
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-primary:hover {
  background: #66b1ff;
}

.btn-secondary {
  background: #f4f4f5;
  color: #606266;
}

.btn-secondary:hover {
  background: #e9e9eb;
}
</style>
