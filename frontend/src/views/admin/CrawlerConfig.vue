<template>
  <el-main>
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">配置总数</div>
          <div class="stat-value">{{ stats.total }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">已启用</div>
          <div class="stat-value">{{ stats.enabled }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">已停用</div>
          <div class="stat-value">{{ stats.disabled }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">平均间隔</div>
          <div class="stat-value">{{ stats.avgInterval }} min</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 工具栏 -->
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <el-input v-model="search" placeholder="搜索数据源名称或URL规则" clearable style="width: 240px" />
        <el-button type="primary" @click="handleAdd">新增</el-button>
        <el-button @click="loadData">刷新</el-button>
      </div>
    </el-card>

    <!-- 配置表格 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="filteredTableData" v-loading="loading" style="width: 100%" class="modern-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="sourceName" label="数据源名称" />
        <el-table-column prop="urlPattern" label="URL规则" />
        <el-table-column prop="interval" label="抓取间隔(分钟)" width="140" />
        <el-table-column prop="enabled" label="启用" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.enabled ? 'success' : 'info'">{{ scope.row.enabled ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="500px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="数据源名称" prop="sourceName">
          <el-input v-model="form.sourceName" placeholder="请输入数据源名称" />
        </el-form-item>
        <el-form-item label="URL规则" prop="urlPattern">
          <el-input v-model="form.urlPattern" placeholder="如 https://www.500.com/*" />
        </el-form-item>
        <el-form-item label="抓取间隔(分钟)" prop="interval">
          <el-input-number v-model="form.interval" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="启用" prop="enabled">
          <el-switch v-model="form.enabled" />
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
import { getCrawlerConfigList, createCrawlerConfig, deleteCrawlerConfig } from '@/api/crawlerConfig'

const tableData = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增配置')
const formRef = ref(null)
const search = ref('')

const stats = reactive({
  total: 12,
  enabled: 9,
  disabled: 3,
  avgInterval: 55
})

const form = reactive({
  id: null, sourceName: '', urlPattern: '', interval: 60, enabled: true
})

const rules = {
  sourceName: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
  urlPattern: [{ required: true, message: '请输入URL规则', trigger: 'blur' }],
  interval: [{ required: true, message: '请输入抓取间隔', trigger: 'blur' }]
}

const filteredTableData = computed(() =>
  tableData.value.filter(row =>
    row.sourceName.includes(search.value) || row.urlPattern.includes(search.value)
  )
)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getCrawlerConfigList()
    tableData.value = res.data || []
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增配置'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑配置'
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = (id) => {
  ElMessageBox.confirm('确定删除该配置？', '提示', { type: 'warning' }).then(async () => {
    try {
      await deleteCrawlerConfig(id)
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
    if (form.id) {
      ElMessage.info('编辑功能待实现')
    } else {
      await createCrawlerConfig(form)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const resetForm = () => {
  Object.assign(form, { id: null, sourceName: '', urlPattern: '', interval: 60, enabled: true })
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