<template>
  <el-dialog
    :title="dialogTitle"
    v-model="visible"
    width="600px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="formData" :rules="rules" label-width="120px">
      <el-form-item label="角色名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入角色名称" />
      </el-form-item>
      
      <el-form-item label="角色编码" prop="code">
        <el-input v-model="formData.code" placeholder="请输入角色编码" :disabled="isEdit" />
      </el-form-item>
      
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="3"
          placeholder="请输入角色描述"
        />
      </el-form-item>
      
      <el-form-item label="权限配置" prop="permissions">
        <div class="permission-tree-container">
          <el-tree
            ref="permissionTreeRef"
            :data="permissionTree"
            :props="treeProps"
            show-checkbox
            node-key="id"
            :check-strictly="false"
            @check="handlePermissionCheck"n          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <el-icon v-if="data.icon" class="node-icon">
                  <component :is="data.icon" />
                </el-icon>
                <span>{{ node.label }}</span>
                <el-tag v-if="data.type === 'menu'" size="small" type="info">菜单</el-tag>
                <el-tag v-else-if="data.type === 'button'" size="small" type="success">按钮</el-tag>
                <el-tag v-else-if="data.type === 'api'" size="small" type="warning">接口</el-tag>
              </span>
            </template>
          </el-tree>
        </div>
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
  roleData: Object,
  permissionTree: Array
})

// Emits
const emit = defineEmits(['update:modelValue', 'submit'])

// 响应式数据
const visible = ref(false)
const submitting = ref(false)
const formRef = ref()
const permissionTreeRef = ref()

const formData = reactive({
  id: null,
  name: '',
  code: '',
  description: '',
  permissions: [],
  status: 1
})

const treeProps = {
  children: 'children',
  label: 'name'
}

const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { pattern: /^[A-Z_]+$/, message: '只能包含大写字母和下划线', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '长度不能超过 200 个字符', trigger: 'blur' }
  ]
}

// 计算属性
const isEdit = computed(() => !!formData.id)

const dialogTitle = computed(() => {
  return isEdit.value ? '编辑角色' : '新增角色'
})

// 监听器
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    resetForm()
    if (props.roleData) {
      loadRoleData()
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
    description: '',
    permissions: [],
    status: 1
  })
  nextTick(() => {
    formRef.value?.clearValidate()
    permissionTreeRef.value?.setCheckedKeys([])
  })
}

const loadRoleData = () => {
  Object.assign(formData, {
    id: props.roleData.id,
    name: props.roleData.name,
    code: props.roleData.code,
    description: props.roleData.description,
    permissions: props.roleData.permissions?.map(p => p.id) || [],
    status: props.roleData.status
  })
  
  nextTick(() => {
    permissionTreeRef.value?.setCheckedKeys(formData.permissions)
  })
}

const handlePermissionCheck = (data, checked) => {
  const checkedKeys = permissionTreeRef.value.getCheckedKeys()
  const halfCheckedKeys = permissionTreeRef.value.getHalfCheckedKeys()
  formData.permissions = [...checkedKeys, ...halfCheckedKeys]
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    const submitData = {
      ...formData,
      permissions: formData.permissions.map(id => ({ id }))
    }
    
    emit('submit', submitData)
    
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
.permission-tree-container {
  border: 1px solid var(--el-border-color-light);
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.node-icon {
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>