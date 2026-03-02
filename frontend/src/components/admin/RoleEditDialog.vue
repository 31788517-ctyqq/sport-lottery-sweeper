<template>
  <el-dialog
    :title="dialogTitle"
    v-model="visible"
    width="650px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="formData" :rules="rules" label-width="120px">
      <el-form-item label="角色名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入角色名称" />
      </el-form-item>

      <el-form-item label="角色等级" prop="level">
        <el-select v-model="formData.level" placeholder="请选择角色等级">
          <el-option label="超级管理员 (L5)" :value="5" />
          <el-option label="管理员 (L4)" :value="4" />
          <el-option label="审计员 (L3)" :value="3" />
          <el-option label="运营员 (L2)" :value="2" />
          <el-option label="观察者 (L1)" :value="1" />
        </el-select>
      </el-form-item>

      <el-form-item label="角色描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="3"
          placeholder="请输入角色描述"
        />
      </el-form-item>

      <el-form-item label="系统内置角色" prop="is_system">
        <el-checkbox v-model="formData.is_system" label="是否为系统内置角色（勾选后无法删除）" />
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
            @check="handlePermissionCheck"
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <span>{{ node.label }}</span>
                <el-tag v-if="data.code" size="small" type="info">{{ data.code }}</el-tag>
                <span v-if="data.description" class="desc-text">{{ data.description }}</span>
              </span>
            </template>
          </el-tree>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  roleData: { type: Object, default: () => ({}) },
  permissionTree: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const visible = ref(false)
const submitting = ref(false)
const formRef = ref()
const permissionTreeRef = ref()

const formData = reactive({
  id: null,
  name: '',
  description: '',
  level: 2,
  is_system: false,
  permissions: []
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
  level: [{ required: true, message: '请选择角色等级', trigger: 'change' }],
  description: [{ max: 200, message: '长度不能超过 200 个字符', trigger: 'blur' }]
}

const isEdit = computed(() => !!formData.id)
const dialogTitle = computed(() => (isEdit.value ? '编辑角色' : '新增角色'))

watch(
  () => props.modelValue,
  (val) => {
    visible.value = val
    if (!val) return
    resetForm()
    if (props.roleData && Object.keys(props.roleData).length > 0) {
      loadRoleData()
    }
  }
)

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const normalizePermissions = (input) => (input || []).map((p) => (typeof p === 'object' ? p.id : p))

const resetForm = () => {
  Object.assign(formData, {
    id: null,
    name: '',
    description: '',
    level: 2,
    is_system: false,
    permissions: []
  })
  nextTick(() => {
    formRef.value?.clearValidate()
    permissionTreeRef.value?.setCheckedKeys([])
  })
}

const loadRoleData = () => {
  Object.assign(formData, {
    id: props.roleData.id ?? null,
    name: props.roleData.name ?? '',
    description: props.roleData.description ?? '',
    level: props.roleData.level ?? 2,
    is_system: props.roleData.is_system ?? false,
    permissions: normalizePermissions(props.roleData.permissions)
  })
  nextTick(() => {
    permissionTreeRef.value?.setCheckedKeys(formData.permissions)
  })
}

const handlePermissionCheck = () => {
  const checkedKeys = permissionTreeRef.value?.getCheckedKeys?.() || []
  const halfCheckedKeys = permissionTreeRef.value?.getHalfCheckedKeys?.() || []
  formData.permissions = [...checkedKeys, ...halfCheckedKeys]
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    emit('submit', {
      ...formData,
      permissions: normalizePermissions(formData.permissions)
    })
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.permission-tree-container {
  border: 1px solid var(--el-border-color-light);
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.desc-text {
  color: #909399;
  font-size: 12px;
  margin-left: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
