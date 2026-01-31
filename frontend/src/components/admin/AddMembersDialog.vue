<template>
  <el-dialog
    title="添加部门成员"
    v-model="visible"
    width="600px"
    @close="handleClose"
  >
    <div class="add-members-content">
      <!-- 搜索区域 -->
      <div class="search-section">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户姓名或用户名"
          clearable
          @input="handleSearch"
          style="width: 300px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <!-- 可选用户列表 -->
      <div class="available-users">
        <div class="section-header">
          <h4>可选用户 ({{ availableUsers.length }})</h4>
          <el-button size="small" @click="selectAll">全选</el-button>
        </div>
        <el-table
          :data="availableUsers"
          height="300px"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="realName" label="姓名" width="100" />
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="email" label="邮箱" width="180" />
          <el-table-column prop="phone" label="手机号" width="130" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
                {{ scope.row.status === 1 ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 已选择用户 -->
      <div class="selected-users" v-if="selectedUsers.length > 0">
        <div class="section-header">
          <h4>已选择 ({{ selectedUsers.length }})</h4>
          <el-button size="small" @click="clearSelection">清空</el-button>
        </div>
        <div class="selected-list">
          <el-tag
            v-for="user in selectedUsers"
            :key="user.id"
            closable
            @close="removeSelectedUser(user.id)"
            class="user-tag"
          >
            {{ user.realName }}
          </el-tag>
        </div>
      </div>
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          添加 ({{ selectedUsers.length }})
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  modelValue: Boolean,
  departmentId: Number,
  excludeUserIds: Array
})

// Emits
const emit = defineEmits(['update:modelValue', 'submit'])

// 响应式数据
const visible = ref(false)
const submitting = ref(false)
const searchKeyword = ref('')
const availableUsers = ref([])
const selectedUsers = ref([])
const selectedRows = ref([])

// 模拟用户数据（实际应该从API获取）
const mockUsers = [
  { id: 1, realName: '张三', username: 'zhangsan', email: 'zhangsan@example.com', phone: '13800138001', status: 1 },
  { id: 2, realName: '李四', username: 'lisi', email: 'lisi@example.com', phone: '13800138002', status: 1 },
  { id: 3, realName: '王五', username: 'wangwu', email: 'wangwu@example.com', phone: '13800138003', status: 0 },
  { id: 4, realName: '赵六', username: 'zhaoliu', email: 'zhaoliu@example.com', phone: '13800138004', status: 1 },
  { id: 5, realName: '钱七', username: 'qianqi', email: 'qianqi@example.com', phone: '13800138005', status: 1 }
]

// 监听器
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadAvailableUsers()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
  if (!val) {
    resetData()
  }
})

// 方法
const loadAvailableUsers = () => {
  // 过滤掉已在部门中的用户和排除的用户ID
  let filteredUsers = mockUsers
  
  if (props.excludeUserIds && props.excludeUserIds.length > 0) {
    filteredUsers = filteredUsers.filter(user => !props.excludeUserIds.includes(user.id))
  }
  
  availableUsers.value = filteredUsers
}

const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    loadAvailableUsers()
    return
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  availableUsers.value = mockUsers.filter(user => 
    user.realName.toLowerCase().includes(keyword) ||
    user.username.toLowerCase().includes(keyword)
  )
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
  selectedUsers.value = selection
}

const selectAll = () => {
  // 这里需要调用表格的全选方法
  // 简化处理，直接选中所有当前页数据
  selectedRows.value = [...availableUsers.value]
  selectedUsers.value = [...availableUsers.value]
}

const clearSelection = () => {
  selectedRows.value = []
  selectedUsers.value = []
}

const removeSelectedUser = (userId) => {
  selectedUsers.value = selectedUsers.value.filter(user => user.id !== userId)
  // 同时从表格选中状态中移除
  const rowIndex = selectedRows.value.findIndex(row => row.id === userId)
  if (rowIndex > -1) {
    selectedRows.value.splice(rowIndex, 1)
  }
}

const handleSubmit = async () => {
  if (selectedUsers.value.length === 0) {
    ElMessage.warning('请先选择要添加的用户')
    return
  }
  
  try {
    submitting.value = true
    
    const submitData = {
      departmentId: props.departmentId,
      userIds: selectedUsers.value.map(u => u.id)
    }
    
    emit('submit', submitData)
    
  } catch (error) {
    console.error('添加部门成员失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  visible.value = false
}

const resetData = () => {
  searchKeyword.value = ''
  selectedUsers.value = []
  selectedRows.value = []
}

// 暴露方法
defineExpose({
  visible
})
</script>

<style scoped>
.add-members-content {
  max-height: 500px;
  overflow-y: auto;
}

.search-section {
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0 12px 0;
}

.section-header h4 {
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 14px;
}

.available-users {
  margin-bottom: 20px;
}

.selected-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.user-tag {
  margin: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>