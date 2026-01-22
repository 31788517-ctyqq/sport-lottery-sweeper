<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <span class="card-header">数据特征工程</span>
      </template>
      <div class="card-content">
        <!-- 搜索与操作 -->
        <div class="toolbar">
          <el-input
            v-model="searchKeyword"
            placeholder="输入特征名称搜索"
            clearable
            style="width: 300px; margin-right: 10px;"
            @clear="fetchFeatures"
            @keyup.enter="fetchFeatures"
          />
          <el-button type="primary" @click="openAddDialog">新增特征</el-button>
        </div>

        <!-- 特征列表 -->
        <el-table :data="featureList" border style="width: 100%; margin-top: 20px;">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="特征名称" />
          <el-table-column prop="description" label="描述" />
          <el-table-column prop="source_type" label="来源类型" />
          <el-table-column prop="created_at" label="创建时间" :formatter="formatDate" />
          <el-table-column label="操作" width="180">
            <template #default="scope">
              <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteFeature(scope.row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 新增/编辑对话框 -->
        <el-dialog
          v-model="dialogVisible"
          :title="isEdit ? '编辑特征' : '新增特征'"
          width="500px"
        >
          <el-form :model="form" label-width="100px">
            <el-form-item label="特征名称">
              <el-input v-model="form.name" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="form.description" type="textarea" />
            </el-form-item>
            <el-form-item label="来源类型">
              <el-input v-model="form.source_type" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitForm">确定</el-button>
          </template>
        </el-dialog>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const searchKeyword = ref('')
const featureList = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)

const form = reactive({
  id: null,
  name: '',
  description: '',
  source_type: ''
})

const fetchFeatures = async () => {
  try {
    const res = await axios.get('/api/v1/admin/draw-prediction/features', {
      params: { keyword: searchKeyword.value }
    })
    featureList.value = res.data
  } catch (err) {
    ElMessage.error('获取特征列表失败')
  }
}

const openAddDialog = () => {
  isEdit.value = false
  form.id = null
  form.name = ''
  form.description = ''
  form.source_type = ''
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  form.id = row.id
  form.name = row.name
  form.description = row.description
  form.source_type = row.source_type
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    if (isEdit.value) {
      await axios.put(`/api/v1/admin/draw-prediction/features/${form.id}`, form)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/v1/admin/draw-prediction/features', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchFeatures()
  } catch (err) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  }
}

const deleteFeature = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该特征吗？', '提示', { type: 'warning' })
    await axios.delete(`/api/v1/admin/draw-prediction/features/${id}`)
    ElMessage.success('删除成功')
    fetchFeatures()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error('删除失败')
  }
}

const formatDate = (row, column, cellValue) => {
  if (!cellValue) return ''
  const d = new Date(cellValue)
  return d.toLocaleString()
}

onMounted(fetchFeatures)
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
}
</style>
