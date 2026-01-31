<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>平局预测特征管理</span>
          <el-button type="primary" @click="handleAddFeature">新增特征</el-button>
        </div>
      </template>
      <div class="card-content">
        <div class="toolbar">
          <el-input
            v-model="keyword"
            placeholder="请输入关键词搜索"
            style="width: 200px; margin-right: 10px;"
          />
          <el-button type="primary" @click="fetchFeatures">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </div>

        <el-table :data="featureList" border style="width: 100%; margin-top: 20px;">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="特征名称" width="150" />
          <el-table-column prop="description" label="描述" />
          <el-table-column prop="source_type" label="来源类型" width="120" />
          <el-table-column prop="is_active" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
                {{ scope.row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" :formatter="formatDate" />
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
              <el-button 
                size="small" 
                :type="scope.row.is_active ? 'warning' : 'success'"
                @click="toggleStatus(scope.row)"
              >
                {{ scope.row.is_active ? '禁用' : '启用' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          style="margin-top: 20px; text-align: right;"
        />
      </div>
    </el-card>

    <!-- 特征编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="特征名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入特征名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入特征描述" />
        </el-form-item>
        <el-form-item label="来源类型" prop="source_type">
          <el-select v-model="form.source_type" placeholder="请选择来源类型" style="width: 100%;">
            <el-option label="基本面数据" value="fundamental" />
            <el-option label="技术面数据" value="technical" />
            <el-option label="历史数据" value="historical" />
            <el-option label="统计数据" value="statistical" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否启用" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDrawFeatures, createDrawFeature, updateDrawFeature, deleteDrawFeature } from '@/api/drawPrediction'
import { ElMessage, ElMessageBox } from 'element-plus'

const keyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const featureList = ref([])
const dialogVisible = ref(false)
const formRef = ref()
const dialogType = ref('add') // 'add' 或 'edit'

const form = ref({
  id: null,
  name: '',
  description: '',
  source_type: 'fundamental',
  is_active: true
})

const rules = {
  name: [
    { required: true, message: '请输入特征名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入特征描述', trigger: 'blur' }
  ],
  source_type: [
    { required: true, message: '请选择来源类型', trigger: 'change' }
  ]
}

const dialogTitle = computed(() => {
  return dialogType.value === 'add' ? '新增特征' : '编辑特征'
})

const fetchFeatures = async () => {
  try {
    const params = {
      keyword: keyword.value,
      page: currentPage.value,
      size: pageSize.value
    }
    const res = await getDrawFeatures(params)
    // 处理可能的不同响应格式
    if (res.data && Array.isArray(res.data)) {
      featureList.value = res.data
      // 如果没有提供总数，使用当前数据长度
      total.value = res.total || res.data.length
    } else {
      featureList.value = res
      total.value = res.length
    }
  } catch (err) {
    console.error('获取特征列表失败:', err)
    ElMessage.error('获取特征列表失败')
  }
}

const handleAddFeature = () => {
  dialogType.value = 'add'
  form.value = {
    id: null,
    name: '',
    description: '',
    source_type: 'fundamental',
    is_active: true
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogType.value = 'edit'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个特征吗?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteDrawFeature(id)
    ElMessage.success('删除成功')
    fetchFeatures()
  } catch (err) {
    if (err !== 'cancel') {
      console.error('删除特征失败:', err)
      ElMessage.error('删除特征失败')
    }
  }
}

const toggleStatus = async (row) => {
  try {
    const newStatus = !row.is_active
    const updateData = { ...row, is_active: newStatus }
    await updateDrawFeature(row.id, updateData)
    ElMessage.success(newStatus ? '启用成功' : '禁用成功')
    fetchFeatures()
  } catch (err) {
    console.error('更新状态失败:', err)
    ElMessage.error('更新状态失败')
  }
}

const submitForm = async () => {
  try {
    await formRef.value.validate()
    
    if (dialogType.value === 'add') {
      await createDrawFeature(form.value)
      ElMessage.success('新增成功')
    } else {
      await updateDrawFeature(form.value.id, form.value)
      ElMessage.success('更新成功')
    }
    
    dialogVisible.value = false
    fetchFeatures()
  } catch (err) {
    console.error('提交失败:', err)
    ElMessage.error('提交失败')
  }
}

const resetFilter = () => {
  keyword.value = ''
  currentPage.value = 1
  fetchFeatures()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  fetchFeatures()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchFeatures()
}

const formatDate = (row, column, cellValue) => {
  if (!cellValue) return ''
  const d = new Date(cellValue)
  return d.toLocaleString()
}

onMounted(() => {
  fetchFeatures()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
