<template>
  <div class="user-management-enhanced">
    <GenericTable
      :columns="tableColumns"
      :table-data="dataStore.currentList"
      :loading="dataStore.loading"
      :pagination="dataStore.pagination"
      :show-add="true"
      title="用户管理"
      @add="handleAddUser"
      @current-change="handlePageChange"
      @size-change="handleSizeChange"
      @selection-change="handleSelectionChange"
    >
      <template #header>
        <div class="table-header">
          <h3>用户管理</h3>
          <div class="header-actions">
            <el-button 
              type="danger" 
              :disabled="dataStore.getSelectedCount === 0"
              @click="handleBatchDelete"
            >
              批量删除 ({{ dataStore.getSelectedCount }})
            </el-button>
            <el-button 
              icon="Refresh" 
              @click="refreshData"
              :loading="dataStore.loading"
            >
              刷新
            </el-button>
            <el-button 
              type="primary" 
              icon="Plus"
              @click="handleAddUser"
            >
              新增用户
            </el-button>
          </div>
        </div>
      </template>
    </GenericTable>

    <!-- 用户编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dataStore.isNew ? '新增用户' : '编辑用户'"
      width="500px"
    >
      <GenericForm
        v-if="dialogVisible"
        ref="formRef"
        :fields="formFields"
        :initial-data="dataStore.editingItem || {}"
        :show-cancel="true"
        @submit="handleSave"
        @cancel="closeDialog"
        @reset="closeDialog"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useDataManagerStore } from '@/stores/dataManager'
import GenericTable from '@/components/common/GenericTable.vue'
import GenericForm from '@/components/common/GenericForm.vue'
import { ElMessage, ElMessageBox, ElDialog } from 'element-plus'
import { Plus, Delete, Edit, Search } from '@element-plus/icons-vue'
import * as api from '@/api'

// 使用数据管理store
const dataStore = useDataManagerStore()

// 对话框控制
const dialogVisible = ref(false)
const formRef = ref(null)

// 表格列配置
const tableColumns = computed(() => [
  {
    prop: 'id',
    label: 'ID',
    width: 80,
    sortable: true
  },
  {
    prop: 'username',
    label: '用户名',
    minWidth: 120
  },
  {
    prop: 'email',
    label: '邮箱',
    minWidth: 180
  },
  {
    prop: 'role',
    label: '角色',
    width: 120,
    type: 'status',
    statusMap: [
      { value: 'admin', label: '管理员', type: 'danger' },
      { value: 'user', label: '普通用户', type: 'primary' },
      { value: 'guest', label: '访客', type: 'info' }
    ]
  },
  {
    prop: 'status',
    label: '状态',
    width: 100,
    type: 'status',
    statusMap: [
      { value: 'active', label: '激活', type: 'success' },
      { value: 'inactive', label: '禁用', type: 'warning' },
      { value: 'pending', label: '待审核', type: 'info' }
    ]
  },
  {
    prop: 'createdAt',
    label: '创建时间',
    width: 160,
    type: 'date'
  },
  {
    label: '操作',
    width: 180,
    type: 'operation',
    buttons: [
      {
        text: '编辑',
        type: 'primary',
        icon: Edit,
        handler: handleEdit
      },
      {
        text: '删除',
        type: 'danger',
        icon: Delete,
        handler: handleDelete
      }
    ]
  }
])

// 表单字段配置
const formFields = computed(() => [
  {
    name: 'username',
    label: '用户名',
    type: 'input',
    placeholder: '请输入用户名',
    required: true,
    rules: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
      { min: 3, max: 20, message: '长度在3到20个字符', trigger: 'blur' }
    ]
  },
  {
    name: 'email',
    label: '邮箱',
    type: 'input',
    inputType: 'email',
    placeholder: '请输入邮箱',
    required: true,
    rules: [
      { required: true, message: '请输入邮箱地址', trigger: 'blur' },
      { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
    ]
  },
  {
    name: 'role',
    label: '角色',
    type: 'select',
    placeholder: '请选择角色',
    options: [
      { label: '管理员', value: 'admin' },
      { label: '普通用户', value: 'user' },
      { label: '访客', value: 'guest' }
    ],
    required: true
  },
  {
    name: 'status',
    label: '状态',
    type: 'select',
    placeholder: '请选择状态',
    options: [
      { label: '激活', value: 'active' },
      { label: '禁用', value: 'inactive' },
      { label: '待审核', value: 'pending' }
    ],
    required: true
  }
])

// 刷新数据
const refreshData = async () => {
  try {
    await dataStore.refresh('adminGetUsers')
  } catch (error) {
    ElMessage.error('刷新数据失败')
  }
}

// 处理页面变化
const handlePageChange = (page) => {
  dataStore.updatePagination(page, dataStore.pagination.pageSize)
  refreshData()
}

// 处理每页大小变化
const handleSizeChange = (size) => {
  dataStore.updatePagination(1, size)
  refreshData()
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  dataStore.selectItems(selection)
}

// 处理新增用户
const handleAddUser = () => {
  dataStore.setEditingItem({}, true)
  dialogVisible.value = true
}

// 处理编辑用户
const handleEdit = (row) => {
  dataStore.setEditingItem(row, false)
  dialogVisible.value = true
}

// 处理删除用户
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await dataStore.deleteItem('adminUser', row.id)
    ElMessage.success('删除成功')
    refreshData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 处理批量删除
const handleBatchDelete = async () => {
  const ids = dataStore.getSelectedIds
  if (ids.length === 0) {
    ElMessage.warning('请至少选择一项')
    return
  }

  try {
    await ElMessageBox.confirm(`确定要删除这 ${ids.length} 项吗？`, '确认批量删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await dataStore.batchDelete('adminUser', ids)
    ElMessage.success('批量删除成功')
    refreshData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 处理保存
const handleSave = async (formData) => {
  try {
    await dataStore.saveItem('adminUser', formData)
    ElMessage.success(dataStore.isNew ? '新增成功' : '更新成功')
    closeDialog()
    refreshData()
  } catch (error) {
    ElMessage.error(dataStore.isNew ? '新增失败' : '更新失败')
  }
}

// 关闭对话框
const closeDialog = () => {
  dialogVisible.value = false
  dataStore.setEditingItem(null)
}

// 初始化数据
onMounted(async () => {
  try {
    await dataStore.fetchList('adminGetUsers')
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
})
</script>

<style scoped>
.user-management-enhanced {
  padding: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style>