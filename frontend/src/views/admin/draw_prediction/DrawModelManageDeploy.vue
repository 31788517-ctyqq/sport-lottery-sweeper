<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <span class="card-header">模型管理与部署</span>
      </template>
      <div class="card-content">
        <!-- 工具栏 -->
        <div class="toolbar">
          <el-input
            v-model="searchKeyword"
            placeholder="输入版本标签搜索"
            clearable
            style="width: 300px; margin-right: 10px;"
            @clear="fetchModels"
            @keyup.enter="fetchModels"
          />
          <el-button type="primary" @click="openCreateDialog">创建模型版本</el-button>
        </div>

        <!-- 模型版本列表 -->
        <el-table :data="modelList" border style="width: 100%; margin-top: 20px;">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="version_tag" label="版本标签" />
          <el-table-column prop="training_job_id" label="训练任务ID" width="140" />
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
                {{ scope.row.status === 'active' ? '上线' : '未上线' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="deployed_at" label="部署时间" :formatter="formatDate" />
          <el-table-column label="操作" width="240">
            <template #default="scope">
              <el-button
                v-if="scope.row.status !== 'active'"
                size="small"
                type="primary"
                @click="deployModel(scope.row.id)"
              >上线</el-button>
              <el-button
                v-if="scope.row.status === 'active'"
                size="small"
                type="warning"
                @click="rollbackModel(scope.row.id)"
              >回滚</el-button>
              <el-button size="small" @click="viewDetails(scope.row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 创建模型版本对话框（预留，实际由训练任务生成） -->
        <el-dialog
          v-model="createDialogVisible"
          title="创建模型版本"
          width="500px"
        >
          <el-form :model="createForm" label-width="120px">
            <el-form-item label="版本标签">
              <el-input v-model="createForm.version_tag" />
            </el-form-item>
            <el-form-item label="训练任务ID">
              <el-input v-model="createForm.training_job_id" type="number" />
            </el-form-item>
            <el-form-item label="模型路径">
              <el-input v-model="createForm.model_path" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="createDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitCreateModel">确定</el-button>
          </template>
        </el-dialog>

        <!-- 详情对话框 -->
        <el-dialog
          v-model="detailDialogVisible"
          title="模型详情"
          width="600px"
        >
          <div v-if="currentModel">
            <p><strong>版本标签：</strong>{{ currentModel.version_tag }}</p>
            <p><strong>训练任务ID：</strong>{{ currentModel.training_job_id }}</p>
            <p><strong>模型路径：</strong>{{ currentModel.model_path }}</p>
            <p><strong>状态：</strong>{{ currentModel.status }}</p>
            <p><strong>性能指标：</strong></p>
            <pre style="background: #f5f5f5; padding: 10px; overflow-x: auto;">{{ JSON.stringify(currentModel.performance_metrics, null, 2) }}</pre>
          </div>
        </el-dialog>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const searchKeyword = ref('')
const modelList = ref([])
const createDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const currentModel = ref(null)

const createForm = reactive({
  version_tag: '',
  training_job_id: '',
  model_path: ''
})

const fetchModels = async () => {
  try {
    const res = await axios.get('/api/v1/admin/draw-prediction/models', {
      params: { keyword: searchKeyword.value }
    })
    modelList.value = res.data
  } catch (err) {
    ElMessage.error('获取模型列表失败')
  }
}

const openCreateDialog = () => {
  createForm.version_tag = ''
  createForm.training_job_id = ''
  createForm.model_path = ''
  createDialogVisible.value = true
}

const submitCreateModel = async () => {
  try {
    // 注意：这个接口实际可能不存在，模型版本通常由训练任务自动生成
    await axios.post('/api/v1/admin/draw-prediction/models', createForm)
    ElMessage.success('创建成功')
    createDialogVisible.value = false
    fetchModels()
  } catch (err) {
    ElMessage.error('创建失败')
  }
}

const deployModel = async (id) => {
  try {
    await axios.post(`/api/v1/admin/draw-prediction/models/${id}/deploy`)
    ElMessage.success('模型已上线')
    fetchModels()
  } catch (err) {
    ElMessage.error('上线失败')
  }
}

const rollbackModel = async (id) => {
  try {
    await axios.post(`/api/v1/admin/draw-prediction/models/${id}/rollback`)
    ElMessage.success('模型已回滚')
    fetchModels()
  } catch (err) {
    ElMessage.error('回滚失败')
  }
}

const viewDetails = (row) => {
  currentModel.value = row
  detailDialogVisible.value = true
}

const formatDate = (row, column, cellValue) => {
  if (!cellValue) return ''
  const d = new Date(cellValue)
  return d.toLocaleString()
}

onMounted(fetchModels)
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
}
</style>
