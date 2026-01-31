<template>
  <div class="backend-users-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>后台用户管理</h3>
          <el-button type="primary" @click="handleCreate">新建用户</el-button>
        </div>
      </template>
      
      <el-table
        :data="users"
        style="width: 100%"
        :loading="loading"
        row-key="id"
      >
        <el-table-column prop="id" label="ID" width="100" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            {{ getRoleText(row.role) }}
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" width="150" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" fixed="right" width="220">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="primary" @click="handlePermissions(row)">权限</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const users = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// Mock data initialization
onMounted(() => {
  loadData()
})

const loadData = () => {
  loading.value = true
  
  // Simulate API call with mock data
  setTimeout(() => {
    users.value = [
      { id: 1, username: 'admin_user', email: 'admin@example.com', role: 'admin', department: '系统管理部', status: 'active', createTime: '2024-01-10 10:30:00' },
      { id: 2, username: 'manager_user', email: 'manager@example.com', role: 'manager', department: '运营管理部', status: 'active', createTime: '2024-01-11 14:20:00' },
      { id: 3, username: 'operator_user', email: 'operator@example.com', role: 'operator', department: '业务运营部', status: 'inactive', createTime: '2024-01-12 09:15:00' },
    ]
    total.value = users.value.length
    loading.value = false
  }, 500)
}

const handleEdit = (row) => {
  ElMessage.info(`编辑用户: ${row.username}`)
}

const handlePermissions = (row) => {
  ElMessage.info(`设置用户权限: ${row.username}`)
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    
    // Simulate deletion
    users.value = users.value.filter(item => item.id !== row.id)
    total.value = users.value.length
    ElMessage.success('删除成功')
  } catch (error) {
    // Cancelled
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  loadData()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadData()
}

const handleCreate = () => {
  ElMessage.info('新建用户')
}

const getRoleText = (role) => {
  const roleMap = {
    admin: '管理员',
    manager: '经理',
    operator: '操作员'
  }
  return roleMap[role] || role
}
</script>

<style scoped>
.backend-users-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>