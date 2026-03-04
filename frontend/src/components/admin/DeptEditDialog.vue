<template>
  <el-dialog
    class="um-dialog"
    v-model="visible"
    :title="isEdit ? '编辑部门' : '新增部门'"
    width="560px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
      <el-form-item label="部门名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入部门名称" />
      </el-form-item>

      <el-form-item label="上级部门">
        <el-tree-select
          v-model="formData.parentId"
          :data="departmentTree"
          :props="treeProps"
          placeholder="可选"
          check-strictly
          clearable
        />
      </el-form-item>

      <el-form-item label="部门负责人">
        <el-select v-model="formData.managerId" placeholder="可选" clearable filterable>
          <el-option
            v-for="user in managers"
            :key="user.id"
            :label="user.realName || user.real_name || user.username"
            :value="user.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="排序">
        <el-input-number
          v-model="formData.sortOrder"
          :min="0"
          :max="9999"
          controls-position="right"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="状态">
        <el-radio-group v-model="formData.status">
          <el-radio :value="true">启用</el-radio>
          <el-radio :value="false">停用</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="描述">
        <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入描述" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  deptData: { type: Object, default: () => ({}) },
  departmentTree: { type: Array, default: () => [] },
  managers: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const visible = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const formData = reactive({
  id: null,
  name: '',
  parentId: null,
  managerId: null,
  sortOrder: 0,
  status: true,
  description: ''
})

const treeProps = { children: 'children', label: 'name', value: 'id' }

const rules = {
  name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度应在 2 到 50 个字符', trigger: 'blur' }
  ]
}

const isEdit = computed(() => !!formData.id)

const resetForm = () => {
  Object.assign(formData, {
    id: null,
    name: '',
    parentId: null,
    managerId: null,
    sortOrder: 0,
    status: true,
    description: ''
  })
  formRef.value?.clearValidate()
}

const loadDeptData = (deptData) => {
  Object.assign(formData, {
    id: deptData.id ?? null,
    name: deptData.name ?? '',
    parentId: deptData.parentId ?? deptData.parent_id ?? null,
    managerId: deptData.managerId ?? deptData.leader_id ?? null,
    sortOrder: deptData.sortOrder ?? deptData.sort_order ?? 0,
    status: deptData.status === undefined ? true : !!deptData.status,
    description: deptData.description ?? ''
  })
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true
    emit('submit', { ...formData })
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  visible.value = false
}

watch(
  () => props.modelValue,
  (val) => {
    visible.value = val
    if (val) {
      resetForm()
      if (props.deptData && Object.keys(props.deptData).length > 0) {
        loadDeptData(props.deptData)
      }
    }
  },
  { immediate: true }
)

watch(visible, (val) => {
  emit('update:modelValue', val)
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
</style>
