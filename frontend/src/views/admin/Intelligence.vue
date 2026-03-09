<template>
  <el-main>
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">分析总数</div>
          <div class="stat-value">{{ stats.total }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">已完成</div>
          <div class="stat-value">{{ stats.completed }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">运行中</div>
          <div class="stat-value">{{ stats.running }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">平均准确率</div>
          <div class="stat-value">{{ stats.avgAccuracy }}%</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 工具栏 -->
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <el-input v-model="search" placeholder="搜索模型名称" clearable style="width: 240px" />
        <el-button type="primary" @click="handleAdd">新增</el-button>
        <el-button @click="loadData">刷新</el-button>
      </div>
    </el-card>

    <!-- 分析记录表格 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="filteredTableData" v-loading="loading" style="width: 100%" class="modern-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="model" label="模型名称" />
        <el-table-column prop="accuracy" label="准确率" />
        <el-table-column prop="createdAt" label="生成时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '完成' ? 'success' : 'warning'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="scope">
            <el-button size="small" @click="handleView(scope.row)">查看</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增弹窗 -->
    <el-dialog title="新增分析记录" v-model="dialogVisible" width="400px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="模型名称" prop="model">
          <el-input v-model="form.model" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="准确率" prop="accuracy">
          <el-input v-model="form.accuracy" placeholder="如 82%" />
        </el-form-item>
        <el-form-item label="生成时间" prop="createdAt">
          <el-date-picker v-model="form.createdAt" type="datetime" placeholder="选择日期时间" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%;">
            <el-option label="完成" value="完成" />
            <el-option label="运行中" value="运行中" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </el-main>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getIntelligenceList, createIntelligence, deleteIntelligence } from '@/api/intelligence'

const tableData = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const search = ref('')

const stats = reactive({
  total: 58,
  completed: 50,
  running: 8,
  avgAccuracy: 83
})

const form = reactive({
  id: null, model: '', accuracy: '', createdAt: '', status: '完成'
})

const rules = {
  model: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  accuracy: [{ required: true, message: '请输入准确率', trigger: 'blur' }],
  createdAt: [{ required: true, message: '请选择生成时间', trigger: 'change' }]
}

const filteredTableData = computed(() =>
  tableData.value.filter(row => row.model.includes(search.value))
)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getIntelligenceList()
    tableData.value = res.data || []
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  resetForm()
  dialogVisible.value = true
}

const handleView = (row) => {
  ElMessage.info(`查看详情：${row.model}`)
}

const handleDelete = (id) => {
  ElMessageBox.confirm('确定删除该记录？', '提示', { type: 'warning' }).then(async () => {
    try {
      await deleteIntelligence(id)
      ElMessage.success('删除成功')
      loadData()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  })
}

const submitForm = async () => {
  await formRef.value.validate()
  try {
    await createIntelligence(form)
    ElMessage.success('新增成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const resetForm = () => {
  Object.assign(form, { id: null, model: '', accuracy: '', createdAt: '', status: '完成' })
  formRef.value?.resetFields()
}

onMounted(loadData)
</script>

<style scoped>
.stat-row { margin-bottom: 24px; }
.stat-card { border-radius: 12px; text-align: center; }
.stat-title { color: #64748b; font-size: 14px; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: bold; color: #1e293b; }
.toolbar-card { border-radius: 12px; margin-bottom: 24px; }
.toolbar { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
.table-card { border-radius: 12px; }
.modern-table { border-radius: 12px; overflow: hidden; }
</style>