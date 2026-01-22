<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <span class="card-header">源配置</span>
        <el-button type="primary" size="small" @click="openForm()" style="float:right;">新增配置</el-button>
      </template>

      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="配置名称" />
        <el-table-column prop="config_type" label="类型" />
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column prop="updated_at" label="更新时间" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="openForm(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="formTitle" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="配置名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.config_type" placeholder="请选择">
            <el-option label="全局" value="global" />
            <el-option label="单源" value="single" />
          </el-select>
        </el-form-item>
        <el-form-item label="配置内容">
          <el-input v-model="form.contentJson" type="textarea" :rows="6" placeholder='请输入 JSON 配置' />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getConfigs, createConfig, updateConfig, deleteConfig } from '@/api/crawlerConfig'

const tableData = ref([])
const dialogVisible = ref(false)
const form = reactive({ id: null, name: '', config_type: 'global', contentJson: '' })
let isEdit = false

const formTitle = computed(() => isEdit ? '编辑配置' : '新增配置')

const loadData = async () => {
  const res = await getConfigs()
  tableData.value = res.data || []
}

const openForm = (row = null) => {
  if (row) {
    isEdit = true
    form.id = row.id
    form.name = row.name
    form.config_type = row.config_type
    form.contentJson = JSON.stringify(row.content, null, 2)
  } else {
    isEdit = false
    form.id = null
    form.name = ''
    form.config_type = 'global'
    form.contentJson = ''
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    const contentObj = JSON.parse(form.contentJson)
    const payload = { name: form.name, config_type: form.config_type, content: contentObj }
    if (isEdit) {
      await updateConfig(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createConfig(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('JSON 格式错误或请求失败')
  }
}

const handleDelete = (id) => {
  ElMessageBox.confirm('确定删除该配置吗？', '提示', { type: 'warning' }).then(async () => {
    await deleteConfig(id)
    ElMessage.success('删除成功')
    loadData()
  })
}

loadData()
</script>

<style scoped>
.page-container {
  padding: 20px;
}
.card-header {
  font-weight: bold;
  font-size: 18px;
}
</style>