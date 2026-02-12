<template>
  <div class="data-management-enhanced">
    <el-card class="page-header">
      <div class="header-content">
        <h2>数据管理</h2>
        <div class="header-actions">
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
          <el-button @click="showImportDialog = true">
            <el-icon><Upload /></el-icon>
            导入数据
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="main-content">
      <GenericTable
        :columns="tableColumns"
        :table-data="dataStore.currentList"
        :loading="dataStore.loading"
        :pagination="dataStore.pagination"
        :show-add="true"
        title="数据记录"
        @add="handleAddData"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        @selection-change="handleSelectionChange"
      >
        <template #column-status="{ value }">
          <el-tag 
            :type="value === 'active' ? 'success' : 'info'"
            disable-transitions
          >
            {{ value === 'active' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </GenericTable>
    </el-card>

    <!-- 数据编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dataStore.isNew ? '新增数据' : '编辑数据'"
      width="600px"
      :before-close="closeDialog"
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

    <!-- 导入对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="导入数据"
      width="500px"
    >
      <el-form>
        <el-form-item label="文件类型">
          <el-radio-group v-model="importType">
            <el-radio value="excel">Excel</el-radio>
            <el-radio value="csv">CSV</el-radio>
            <el-radio value="json">JSON</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="上传文件">
          <el-upload
            drag
            action="/api/v1/admin/data/upload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :auto-upload="false"
            ref="uploadRef"
          >
            <el-icon class="el-icon--upload">
              <Upload />
            </el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或<em>点击上传</em>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="startImport">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useDataManagerStore } from '@/stores/dataManager'
import GenericTable from '@/components/common/GenericTable.vue'
import GenericForm from '@/components/common/GenericForm.vue'
import { ElMessage, ElMessageBox, ElDialog, ElUpload } from 'element-plus'
import { Refresh, Upload, Edit, Delete } from '@element-plus/icons-vue'
import * as api from '@/api'

// 使用数据管理store
const dataStore = useDataManagerStore()

// 对话框控制
const dialogVisible = ref(false)
const showImportDialog = ref(false)
const importType = ref('excel')
const formRef = ref(null)
const uploadRef = ref(null)

// 表格列配置
const tableColumns = computed(() => [
  {
    prop: 'id',
    label: 'ID',
    width: 80,
    sortable: true
  },
  {
    prop: 'name',
    label: '名称',
    minWidth: 150
  },
  {
    prop: 'type',
    label: '类型',
    width: 120
  },
  {
    prop: 'status',
    label: '状态',
    width: 100,
    // 使用插槽自定义渲染
  },
  {
    prop: 'createdAt',
    label: '创建时间',
    width: 160,
    type: 'date'
  },
  {
    prop: 'updatedAt',
    label: '更新时间',
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
    name: 'name',
    label: '名称',
    type: 'input',
    placeholder: '请输入数据名称',
    required: true,
    rules: [
      { required: true, message: '请输入数据名称', trigger: 'blur' },
      { min: 2, max: 50, message: '长度在2到50个字符', trigger: 'blur' }
    ]
  },
  {
    name: 'type',
    label: '类型',
    type: 'select',
    placeholder: '请选择类型',
    options: [
      { label: '比赛数据', value: 'match' },
      { label: '赔率数据', value: 'odds' },
      { label: '用户数据', value: 'user' },
      { label: '配置数据', value: 'config' }
    ],
    required: true
  },
  {
    name: 'description',
    label: '描述',
    type: 'textarea',
    placeholder: '请输入描述信息',
    attrs: { rows: 3 }
  },
  {
    name: 'status',
    label: '状态',
    type: 'select',
    placeholder: '请选择状态',
    options: [
      { label: '启用', value: 'active' },
      { label: '禁用', value: 'inactive' }
    ],
    required: true
  }
])

// 刷新数据
const refreshData = async () => {
  try {
    await dataStore.fetchList('dataGetList')
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

// 处理新增数据
const handleAddData = () => {
  dataStore.setEditingItem({}, true)
  dialogVisible.value = true
}

// 处理编辑数据
const handleEdit = (row) => {
  dataStore.setEditingItem(row, false)
  dialogVisible.value = true
}

// 处理删除数据
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除数据 "${row.name}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await dataStore.deleteItem('data', row.id)
    ElMessage.success('删除成功')
    refreshData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 处理保存
const handleSave = async (formData) => {
  try {
    await dataStore.saveItem('data', formData)
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

// 处理文件上传成功
const handleUploadSuccess = (response) => {
  ElMessage.success('文件上传成功')
}

// 处理文件上传失败
const handleUploadError = (error) => {
  ElMessage.error('文件上传失败')
  console.error('Upload error:', error)
}

// 开始导入
const startImport = () => {
  ElMessage.success('开始导入数据')
  showImportDialog.value = false
}

// 初始化数据
onMounted(async () => {
  try {
    await dataStore.fetchList('dataGetList')
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
})
</script>

<style scoped>
.data-management-enhanced {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.main-content {
  padding: 20px 0;
}

.dialog-footer {
  text-align: right;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
</style>