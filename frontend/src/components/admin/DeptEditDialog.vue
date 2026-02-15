<template>
  <el-dialog
    :title="dialogTitle"
    v-model="visible"
    width="500px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
      <el-form-item label="部门名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入部门名称" />
      </el-form-item>
      
      <el-form-item label="部门编码" prop="code">
        <el-input v-model="formData.code" placeholder="请输入部门编码" :disabled="isEdit" />
      </el-form-item>
      
      <el-form-item label="上级部门" prop="parentId">
        <el-tree-select
          v-model="formData.parentId"
          :data="departmentTree"
          :props="treeProps"
          placeholder="请选择上级部门"
          check-strictly
          clearable
        />
      </el-form-item>
      
      <el-form-item label="部门经理" prop="managerId">
        <el-select
          v-model="formData.managerId"
          placeholder="请选择部门经理"
          clearable
          filterable
        >
          <el-option
            v-for="user in managers"
            :key="user.id"
            :label="user.realName"
            :value="user.id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="排序" prop="sort">
        <el-input-number
          v-model="formData.sort"
          :min="0"
          :max="999"
          controls-position="right"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="3"
          placeholder="请输入部门描述"
        />
      </el-form-item>
      
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="formData.status">
          <el-radio :value="1">启用</el-radio>
          <el-radio :value="0">禁用</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  modelValue: Boolean,
  deptData: Object,
  departmentTree: Array,
  managers: Array
})

// Emits
const emit = defineEmits(['update:modelValue', 'submit'])

// 响应式数据
const visible = ref(false)
const submitting = ref(false)
const formRef = ref()

const formData = reactive({
  id: null,
  name: '',
  code: '',
  parentId: null,
  managerId: null,
  sort: 0,
  description: '',
  status: 1
})

const treeProps = {
  children: 'children',
  label: 'name',
  value: 'id'
}

const rules = {
  name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入部门编码', trigger: 'blur' },
    { pattern: /^[A-Z0-9_]+$/, message: '只能包含大写字母、数字和下划线', trigger: 'blur' }
  ],
  sort: [
    { required: true, message: '请输入排序值', trigger: 'blur' }
  ]
}

// 计算属性
const isEdit = computed(() => !!formData.id)

const dialogTitle = computed(() => {
  return isEdit.value ? '编辑部门' : '新增部门'
})

// 监听器
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    resetForm()
    if (props.deptData) {
      loadDeptData()
    }
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 方法
const resetForm = () => {
  Object.assign(formData, {
    id: null,
    name: '',
    code: '',
    parentId: null,
    managerId: null,
    sort: 0,
    description: '',
    status: 1
  })
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

const loadDeptData = () => {
  Object.assign(formData, {
    id: props.deptData.id,
    name: props.deptData.name,
    code: props.deptData.code,
    parentId: props.deptData.parentId,
    managerId: props.deptData.managerId,
    sort: props.deptData.sort,
    description: props.deptData.description,
    status: props.deptData.status
  })
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    emit('submit', { ...formData })
    
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  visible.value = false
}

// 暴露方法
defineExpose({
  visible
})
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>