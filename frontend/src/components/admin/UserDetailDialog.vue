<template>
  <el-dialog
    v-model="visible"
    :title="getDialogTitle()"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form 
      ref="formRef"
      :model="userData" 
      :rules="formRules"
      label-width="100px"
      class="user-form"
    >
      <el-row :gutter="20">
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
            <el-input 
              v-model="userData.realName" 
              placeholder="请输入姓名"
              :disabled="mode === 'view'"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="邮箱" prop="email">
            <el-input 
              v-model="userData.email" 
              placeholder="请输入邮箱"
              :disabled="mode === 'view'"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="手机号" prop="phone">
            <el-input 
              v-model="userData.phone" 
              placeholder="请输入手机号"
              :disabled="mode === 'view'"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="部门" prop="departmentId">
            <el-tree-select
              v-model="userData.departmentId"
              :data="departmentOptions"
              :props="treeProps"
              placeholder="请选择部门"
              check-strictly
              :disabled="mode === 'view'"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="userData.status" :disabled="mode === 'view'">
              <el-radio value="active">正常</el-radio>
              <el-radio value="inactive">禁用</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="角色" prop="roleIds" v-if="mode !== 'create'">
        <el-select
          v-model="userData.roleIds"
          multiple
          placeholder="请选择角色"
          :disabled="mode === 'view'"
          style="width: 100%"
        >
          <el-option 
            v-for="role in roleOptions" 
            :key="role.id"
            :label="role.name" 
            :value="role.id" 
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="备注" v-if="mode !== 'create'">
        <el-input
          v-model="userData.remark"
          type="textarea"
          :rows="3"
          placeholder="请输入备注"
          :disabled="mode === 'view'"
        />
      </el-form-item>
      
      <!-- 查看模式下显示更多信息 -->
      <template v-if="mode === 'view'">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="注册时间">
              <span>{{ formatDate(userData.createdAt) }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最后登录">
              <span>{{ formatDate(userData.lastLoginTime) || '从未登录' }}</span>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="角色">
          <el-tag 
            v-for="role in userData.roleNames" 
            :key="role"
            size="small"
            style="margin-right: 8px; margin-bottom: 4px;"
          >
            {{ role }}
          </el-tag>
        </el-form-item>
      </template>
    </el-form>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">
          {{ mode === 'view' ? '关闭' : '取消' }}
        </el-button>
        <el-button 
          v-if="mode === 'view'"
          type="primary" 
          @click="handleEdit"
        >
          编辑
        </el-button>
        <el-button 
          v-if="mode === 'edit'"
          type="primary" 
          @click="handleSave"
          :loading="saving"
        >
          保存
        </el-button>
        <el-button 
          v-if="mode === 'create'"
          type="primary" 
          @click="handleCreate"
          :loading="creating"
        >
          创建
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { getDepartments } from '@/api/modules/departments'
import { getRoles } from '@/api/modules/roles'
import { getUserDetail, createUser, updateUser } from '@/api/modules/users'

const props = defineProps({
  modelValue: Boolean,
  mode: String, // 'view' | 'edit' | 'create'
  userId: [String, Number]
})

const emit = defineEmits(['update:modelValue', 'saved', 'closed'])

const visible = ref(false)
const saving = ref(false)
const creating = ref(false)
const formRef = ref(null)

const userData = reactive({
  username: '',
  realName: '',
  email: '',
  phone: '',
  departmentId: '',
  status: 'active',
  roleIds: [],
  remark: '',
  createdAt: '',
  lastLoginTime: '',
  roleNames: []
})

const departmentOptions = ref([])
const roleOptions = ref([])

const treeProps = {
  children: 'children',
  label: 'name',
  value: 'id'
}

const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  realName: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '长度在 2 到 10 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ],
  departmentId: [
    { required: true, message: '请选择部门', trigger: 'change' }
  ]
}

// 监听显示状态
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadOptions()
    if (props.mode === 'edit' || props.mode === 'view') {
      loadUserData()
    } else {
      resetForm()
    }
  }
})

// 监听弹窗关闭
watch(() => visible.value, (val) => {
  if (!val) {
    emit('update:modelValue', false)
  }
})

// 加载选项数据
const loadOptions = async () => {
  try {
    // 加载部门选项
    const deptResponse = await getDepartments({ tree: false })
    if (deptResponse && deptResponse.data) {
      departmentOptions.value = Array.isArray(deptResponse.data) ? deptResponse.data : []
    }
    
    // 加载角色选项
    const roleResponse = await getRoles({ status: 'active' })
    if (roleResponse && roleResponse.data) {
      roleOptions.value = Array.isArray(roleResponse.data) ? roleResponse.data : []
    }
  } catch (error) {
    console.error('加载选项失败:', error)
  }
}

// 加载用户数据
const loadUserData = async () => {
  if (!props.userId) return
  
  try {
    const response = await getUserDetail(props.userId)
    const payload = response?.data ?? response
    if (payload) {
      Object.assign(userData, payload)
    }
  } catch (error) {
    console.error('加载用户数据失败:', error)
    ElMessage.error('加载用户数据失败')
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(userData, {
    username: '',
    realName: '',
    email: '',
    phone: '',
    departmentId: '',
    status: 'active',
    roleIds: [],
    remark: '',
    createdAt: '',
    lastLoginTime: '',
    roleNames: []
  })
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

// 获取对话框标题
const getDialogTitle = () => {
  const titles = {
    view: '用户详情',
    edit: '编辑用户',
    create: '创建用户'
  }
  return titles[props.mode] || '用户'
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
  emit('closed')
}

// 编辑用户
const handleEdit = () => {
  emit('update:modelValue', false)
  // 触发父组件切换到编辑模式
  setTimeout(() => {
    emit('update:modelValue', true)
  }, 100)
}

// 保存用户
const handleSave = async () => {
  try {
    await formRef.value.validate()
    saving.value = true
    
    await updateUser(props.userId, userData)
    ElMessage.success('保存成功')
    visible.value = false
    emit('saved')
  } catch (error) {
    if (error !== false) { // 不是表单验证错误
      console.error('保存失败:', error)
      ElMessage.error('保存失败')
    }
  } finally {
    saving.value = false
  }
}

// 创建用户
const handleCreate = async () => {
  try {
    await formRef.value.validate()
    creating.value = true
    
    await createUser(userData)
    ElMessage.success('创建成功')
    visible.value = false
    emit('saved')
  } catch (error) {
    if (error !== false) { // 不是表单验证错误
      console.error('创建失败:', error)
      ElMessage.error('创建失败')
    }
  } finally {
    creating.value = false
  }
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}
</script>

<style scoped>
.user-form {
  max-height: 500px;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
