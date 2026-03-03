<template>
  <el-dialog
    class="um-dialog"
    v-model="visible"
    :title="dialogTitle"
    width="840px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="userData" :rules="formRules" label-width="100px" class="user-form">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="userData.username"
              placeholder="请输入用户名"
              :disabled="mode === 'view' || mode === 'edit'"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="姓名" prop="realName">
            <el-input v-model="userData.realName" placeholder="请输入姓名" :disabled="mode === 'view'" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="userData.email" placeholder="请输入邮箱" :disabled="mode === 'view'" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="userData.phone" placeholder="请输入手机号" :disabled="mode === 'view'" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="部门" prop="departmentId">
            <el-tree-select
              v-model="userData.departmentId"
              :data="departmentOptions"
              :props="treeProps"
              placeholder="可选"
              check-strictly
              clearable
              style="width: 100%"
              :disabled="mode === 'view'"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="角色" prop="role">
            <el-select v-model="userData.role" placeholder="请选择角色" :disabled="mode === 'view'" style="width: 100%">
              <el-option v-for="item in roleOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="userData.status" :disabled="mode === 'view'">
              <el-radio value="active">正常</el-radio>
              <el-radio value="inactive">禁用</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row v-if="mode === 'create'" :gutter="16">
        <el-col :span="12">
          <el-form-item label="登录密码" prop="password">
            <el-input
              v-model="userData.password"
              type="password"
              show-password
              autocomplete="new-password"
              placeholder="请输入登录密码"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="userData.confirmPassword"
              type="password"
              show-password
              autocomplete="new-password"
              placeholder="请再次输入密码"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item v-if="mode !== 'create'" label="备注" prop="remark">
        <el-input
          v-model="userData.remark"
          type="textarea"
          :rows="3"
          placeholder="请输入备注"
          :disabled="mode === 'view'"
        />
      </el-form-item>

      <template v-if="mode === 'view'">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="创建时间">
              <span>{{ formatDate(userData.createdAt) }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最后登录">
              <span>{{ formatDate(userData.lastLoginTime) || '从未登录' }}</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="角色标签">
          <el-tag v-for="role in displayRoleNames" :key="role" size="small" class="mr-8">{{ role }}</el-tag>
        </el-form-item>
      </template>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">{{ mode === 'view' ? '关闭' : '取消' }}</el-button>
        <el-button
          v-if="mode === 'edit'"
          type="primary"
          :loading="saving || loading"
          :disabled="loading"
          @click="handleSave"
        >
          保存
        </el-button>
        <el-button v-if="mode === 'create'" type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getDepartments } from '@/api/modules/departments'
import { getRoles } from '@/api/modules/roles'
import { createUser, getUserDetail, updateUser } from '@/api/modules/users'

const ROLE_OPTIONS_FALLBACK = [
  { label: '超级管理员', value: 'super_admin' },
  { label: '管理员', value: 'admin' },
  { label: '版主', value: 'moderator' },
  { label: '审计员', value: 'auditor' },
  { label: '运营员', value: 'operator' }
]

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  mode: { type: String, default: 'view' },
  userId: { type: [Number, String], default: null }
})

const emit = defineEmits(['update:modelValue', 'saved', 'closed'])

const visible = ref(false)
const saving = ref(false)
const creating = ref(false)
const loading = ref(false)
const formRef = ref(null)

const userData = reactive({
  username: '',
  realName: '',
  email: '',
  phone: '',
  departmentId: null,
  departmentName: '',
  status: 'active',
  role: 'operator',
  roleNames: [],
  remark: '',
  password: '',
  confirmPassword: '',
  createdAt: '',
  lastLoginTime: ''
})

const departmentOptions = ref([])
const roleOptions = ref([...ROLE_OPTIONS_FALLBACK])
const departmentLookup = ref(new Map())

const treeProps = { children: 'children', label: 'name', value: 'id' }

const mode = computed(() => props.mode)
const dialogTitle = computed(() => {
  if (mode.value === 'create') return '新增用户'
  if (mode.value === 'edit') return '编辑用户'
  return '用户详情'
})

const displayRoleNames = computed(() => {
  if (Array.isArray(userData.roleNames) && userData.roleNames.length > 0) return userData.roleNames
  const matched = roleOptions.value.find((item) => item.value === userData.role)
  return matched ? [matched.label] : userData.role ? [userData.role] : ['-']
})

const validatePassword = (_rule, value, callback) => {
  if (mode.value !== 'create') return callback()
  if (!value) return callback(new Error('请输入密码'))
  if (value.length < 8) return callback(new Error('密码长度至少 8 位'))
  if (!/^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$/.test(value)) {
    return callback(new Error('密码需包含大小写字母和数字'))
  }
  callback()
}

const validateUsername = (_rule, value, callback) => {
  // Username is immutable in edit mode, only validate strictly on create.
  if (mode.value !== 'create') return callback()
  if (!value) return callback(new Error('请输入用户名'))
  if (String(value).length < 3 || String(value).length > 20) {
    return callback(new Error('长度在 3 到 20 个字符'))
  }
  callback()
}

const validateConfirmPassword = (_rule, value, callback) => {
  if (mode.value !== 'create') return callback()
  if (!value) return callback(new Error('请确认密码'))
  if (value !== userData.password) return callback(new Error('两次密码输入不一致'))
  callback()
}

const formRules = {
  username: [{ validator: validateUsername, trigger: 'blur' }],
  realName: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

const resetForm = () => {
  Object.assign(userData, {
    username: '',
    realName: '',
    email: '',
    phone: '',
    departmentId: null,
    departmentName: '',
    status: 'active',
    role: 'operator',
    roleNames: [],
    remark: '',
    password: '',
    confirmPassword: '',
    createdAt: '',
    lastLoginTime: ''
  })
  nextTick(() => formRef.value?.clearValidate())
}

const normalizeDepartmentNode = (node) => ({
  id: Number(node.id),
  name: node.name || '',
  children: Array.isArray(node.children) ? node.children.map(normalizeDepartmentNode) : []
})

const buildDepartmentLookup = (nodes, map = new Map()) => {
  nodes.forEach((node) => {
    map.set(node.id, node.name)
    if (node.children?.length) buildDepartmentLookup(node.children, map)
  })
  return map
}

const loadDepartments = async () => {
  try {
    const response = await getDepartments({ tree: true })
    const payload = response?.data ?? response
    const rows = Array.isArray(payload?.data) ? payload.data : Array.isArray(payload) ? payload : []
    const normalized = rows.map(normalizeDepartmentNode)
    departmentOptions.value = normalized
    departmentLookup.value = buildDepartmentLookup(normalized)
  } catch (error) {
    console.error('加载部门失败:', error)
    departmentOptions.value = []
    departmentLookup.value = new Map()
  }
}

const loadRoles = async () => {
  try {
    const response = await getRoles({})
    const payload = response?.data ?? response
    const rows = Array.isArray(payload) ? payload : []
    if (!rows.length) {
      roleOptions.value = [...ROLE_OPTIONS_FALLBACK]
      return
    }
    roleOptions.value = rows.map((item) => ({
      label: item.display_name || item.name || item.code || item.role || '未知角色',
      value: item.role || item.code || item.name
    }))
  } catch (error) {
    console.error('加载角色失败:', error)
    roleOptions.value = [...ROLE_OPTIONS_FALLBACK]
  }
}

const loadUser = async () => {
  if (!props.userId || mode.value === 'create') return
  loading.value = true
  try {
    const response = await getUserDetail(props.userId)
    const row = response?.data || {}
    userData.username = row.username || ''
    userData.realName = row.realName || ''
    userData.email = row.email || ''
    userData.phone = row.phone || ''
    userData.departmentId = row.departmentId ? Number(row.departmentId) : null
    userData.departmentName = row.departmentName || ''
    userData.status = row.status || 'active'
    userData.role = row.role || 'operator'
    userData.roleNames = Array.isArray(row.roleNames) ? row.roleNames : []
    userData.remark = row.remark || row.remarks || ''
    userData.createdAt = row.createdAt || ''
    userData.lastLoginTime = row.lastLoginTime || ''
  } catch (error) {
    console.error('加载用户详情失败:', error)
    ElMessage.error('加载用户详情失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (value) => {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN')
}

const createPayload = () => {
  const departmentName =
    userData.departmentName || (userData.departmentId ? departmentLookup.value.get(Number(userData.departmentId)) : '')

  return {
    username: userData.username,
    password: userData.password,
    realName: userData.realName,
    email: userData.email,
    phone: userData.phone || null,
    departmentName: departmentName || null,
    role: userData.role,
    status: userData.status
  }
}

const updatePayload = () => {
  const departmentName =
    userData.departmentName || (userData.departmentId ? departmentLookup.value.get(Number(userData.departmentId)) : '')

  return {
    realName: userData.realName,
    email: userData.email,
    phone: userData.phone || null,
    departmentName: departmentName || null,
    role: userData.role,
    status: userData.status,
    remark: userData.remark || null
  }
}

const handleCreate = async () => {
  try {
    await formRef.value?.validate()
    creating.value = true
    await createUser(createPayload())
    ElMessage.success('创建成功')
    emit('saved')
    visible.value = false
  } catch (error) {
    if (error !== false) {
      console.error('创建失败:', error)
      ElMessage.error('创建失败')
    }
  } finally {
    creating.value = false
  }
}

const handleSave = async () => {
  try {
    if (loading.value) return
    await formRef.value?.validate()
    saving.value = true
    await updateUser(props.userId, updatePayload())
    ElMessage.success('保存成功')
    emit('saved')
    visible.value = false
  } catch (error) {
    if (error !== false) {
      console.error('保存失败:', error)
      ElMessage.error('保存失败')
    }
  } finally {
    saving.value = false
  }
}

const handleClose = () => {
  visible.value = false
}

const initializeDialog = async () => {
  resetForm()
  await Promise.all([loadDepartments(), loadRoles()])
  await loadUser()
}

watch(
  () => props.modelValue,
  async (val) => {
    visible.value = val
    if (val) {
      await initializeDialog()
    }
  },
  { immediate: true }
)

watch(visible, (val) => {
  emit('update:modelValue', val)
  if (!val) emit('closed')
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

.user-form {
  padding-right: 6px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.mr-8 {
  margin-right: 8px;
}
</style>
