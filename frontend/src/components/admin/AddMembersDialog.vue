<template>
  <el-dialog
    class="um-dialog"
    v-model="visible"
    title="添加部门成员"
    width="720px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="toolbar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索用户名或姓名"
        clearable
        style="width: 320px"
        @input="applyFilter"
      />
      <el-button :loading="loading" @click="loadUsers">刷新</el-button>
    </div>

    <el-table
      ref="tableRef"
      v-loading="loading"
      :data="filteredUsers"
      height="360px"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="realName" label="姓名" min-width="140" />
      <el-table-column prop="username" label="用户名" min-width="140" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="phone" label="手机号" min-width="120" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">
            {{ row.status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        添加（{{ selectedUsers.length }}）
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getUsers } from '@/api/modules/users'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  departmentId: { type: Number, default: null },
  excludeUserIds: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const visible = ref(false)
const loading = ref(false)
const submitting = ref(false)
const searchKeyword = ref('')
const allUsers = ref([])
const filteredUsers = ref([])
const selectedUsers = ref([])
const tableRef = ref(null)

const normalizeUser = (item) => {
  const statusRaw = item.status
  const isActive = statusRaw === 'active' || statusRaw === 1 || statusRaw === true || statusRaw === '1'
  return {
    id: Number(item.id),
    username: item.username || '',
    realName: item.realName || item.real_name || item.username || `用户${item.id}`,
    email: item.email || '',
    phone: item.phone || '',
    status: isActive ? 'active' : 'inactive'
  }
}

const applyFilter = () => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  if (!keyword) {
    filteredUsers.value = [...allUsers.value]
    return
  }
  filteredUsers.value = allUsers.value.filter((user) => {
    return user.username.toLowerCase().includes(keyword) || user.realName.toLowerCase().includes(keyword)
  })
}

const loadUsers = async () => {
  if (!visible.value) return
  loading.value = true
  try {
    const response = await getUsers({ skip: 0, limit: 500 })
    const payload = response?.data ?? response
    const rows = Array.isArray(payload?.items) ? payload.items : []
    const excludeSet = new Set((props.excludeUserIds || []).map((id) => Number(id)))

    allUsers.value = rows
      .map(normalizeUser)
      .filter((user) => user.id && !excludeSet.has(user.id))
      .sort((a, b) => a.realName.localeCompare(b.realName))
    applyFilter()
  } catch (error) {
    console.error('加载可选用户失败:', error)
    ElMessage.error('加载可选用户失败')
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedUsers.value = selection
}

const handleSubmit = async () => {
  if (!props.departmentId) {
    ElMessage.warning('请先选择部门')
    return
  }
  if (selectedUsers.value.length === 0) {
    ElMessage.warning('请先选择成员')
    return
  }

  submitting.value = true
  try {
    emit('submit', {
      departmentId: props.departmentId,
      userIds: selectedUsers.value.map((item) => item.id)
    })
  } finally {
    submitting.value = false
  }
}

const resetDialogState = () => {
  searchKeyword.value = ''
  allUsers.value = []
  filteredUsers.value = []
  selectedUsers.value = []
  tableRef.value?.clearSelection()
}

const handleClose = () => {
  visible.value = false
}

watch(
  () => props.modelValue,
  async (val) => {
    visible.value = val
    if (val) {
      resetDialogState()
      await loadUsers()
    }
  },
  { immediate: true }
)

watch(visible, (val) => {
  emit('update:modelValue', val)
  if (!val) resetDialogState()
})
</script>

<style scoped>
:deep(.um-dialog.el-dialog) {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  box-shadow: none;
  overflow: hidden;
}

:deep(.um-dialog .el-dialog__header) {
  margin-right: 0;
  padding: 14px 16px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.um-dialog .el-dialog__title) {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

:deep(.um-dialog .el-dialog__body) {
  padding: 16px;
}

:deep(.um-dialog .el-dialog__footer) {
  padding: 12px 16px;
  border-top: 1px solid #ebeef5;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
</style>
