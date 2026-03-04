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
          <div class="stat-title">系统版本</div>
          <div class="stat-value">{{ stats.version }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">运行时长</div>
          <div class="stat-value">{{ stats.uptime }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 工具栏 -->
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <el-input v-model="search" placeholder="搜索配置键或描述" clearable style="width: 240px" />
        <el-button type="primary" @click="handleAdd">新增配置</el-button>
        <el-button @click="loadData">刷新</el-button>
      </div>
    </el-card>

    <!-- 配置表格 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="filteredTableData" v-loading="loading" style="width: 100%" class="modern-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="key" label="配置键" />
        <el-table-column prop="value" label="配置值" />
        <el-table-column prop="desc" label="描述" />
        <el-table-column label="操作" width="160">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 原有设置表单与系统信息双栏 -->
    <el-row :gutter="20" style="margin-top: 24px;">
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="form-card">
          <template #header><span>基本设置</span></template>
          <el-form label-width="100px">
            <el-form-item label="系统名称">
              <el-input v-model="settings.siteName" />
            </el-form-item>
            <el-form-item label="维护模式">
              <el-switch v-model="settings.maintenanceMode" />
            </el-form-item>
            <el-form-item label="日志级别">
              <el-select v-model="settings.logLevel" style="width: 100%">
                <el-option label="DEBUG" value="debug" />
                <el-option label="INFO" value="info" />
                <el-option label="WARN" value="warn" />
                <el-option label="ERROR" value="error" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings">保存</el-button>
              <el-button @click="resetSettings">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="info-card">
          <template #header><span>系统信息</span></template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="版本">{{ stats.version }}</el-descriptions-item>
            <el-descriptions-item label="运行时间">{{ stats.uptime }}</el-descriptions-item>
            <el-descriptions-item label="Node版本">18.17.0</el-descriptions-item>
            <el-descriptions-item label="数据库">SQLite</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新增/编辑弹窗 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="400px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="配置键" prop="key">
          <el-input v-model="form.key" placeholder="请输入配置键" />
        </el-form-item>
        <el-form-item label="配置值" prop="value">
          <el-input v-model="form.value" placeholder="请输入配置值" />
        </el-form-item>
        <el-form-item label="描述" prop="desc">
          <el-input v-model="form.desc" placeholder="请输入描述" />
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
import { getSystemList, createSystem, deleteSystem } from '@/api/system'

const tableData = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增配置')
const formRef = ref(null)
const search = ref('')

const stats = reactive({
  total: 36,
  enabled: 32,
  version: 'v1.0.0',
  uptime: '12天 4小时'
})

const settings = reactive({
  siteName: '竞彩足球扫盘系统',
  maintenanceMode: false,
  logLevel: 'info'
})

const form = reactive({ id: null, key: '', value: '', desc: '' })

const rules = {
  key: [{ required: true, message: '请输入配置键', trigger: 'blur' }],
  value: [{ required: true, message: '请输入配置值', trigger: 'blur' }]
}

const filteredTableData = computed(() =>
  tableData.value.filter(row =>
    row.key.includes(search.value) || row.desc.includes(search.value)
  )
)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getSystemList()
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
  form.id = row.id
  form.key = row.key
  form.value = row.value
  form.desc = row.desc
  dialogVisible.value = true
}

const handleDelete = (id) => {
  ElMessageBox.confirm('确定删除该配置？', '提示', { type: 'warning' }).then(async () => {
    try {
      await deleteSystem(id)
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
      await createSystem(form)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const resetForm = () => {
  form.id = null
  form.key = ''
  form.value = ''
  form.desc = ''
  formRef.value?.resetFields()
}

function saveSettings() {
  ElMessage.success('保存成功')
}
function resetSettings() {
  settings.siteName = '竞彩足球扫盘系统'
  settings.maintenanceMode = false
  settings.logLevel = 'info'
}

onMounted(loadData)
</script>

<style scoped>
.stat-row {
  margin-bottom: 24px;
}
.stat-card {
  border-radius: 12px;
  text-align: center;
}
.stat-title {
  color: #64748b;
  font-size: 14px;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #1e293b;
}
.toolbar-card {
  border-radius: 12px;
  margin-bottom: 24px;
}
.toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}
.table-card {
  border-radius: 12px;
}
.modern-table {
  border-radius: 12px;
  overflow: hidden;
}
.form-card, .info-card {
  border-radius: 12px;
}
</style>