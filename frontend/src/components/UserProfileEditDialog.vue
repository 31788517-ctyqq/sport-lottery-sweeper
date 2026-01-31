<template>
  <el-dialog
    title="编辑个人信息"
    v-model="visible"
    width="500px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="formData.username" placeholder="请输入用户名" disabled />
      </el-form-item>
      
      <el-form-item label="昵称" prop="nickname">
        <el-input v-model="formData.nickname" placeholder="请输入昵称" />
      </el-form-item>
      
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="formData.email" placeholder="请输入邮箱地址" />
      </el-form-item>
      
      <el-form-item label="手机号" prop="phone">
        <el-input v-model="formData.phone" placeholder="请输入手机号" />
      </el-form-item>
      
      <el-form-item label="性别" prop="gender">
        <el-radio-group v-model="formData.gender">
          <el-radio :label="1">男</el-radio>
          <el-radio :label="2">女</el-radio>
          <el-radio :label="0">保密</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="生日" prop="birthday">
        <el-date-picker
          v-model="formData.birthday"
          type="date"
          placeholder="选择生日"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="个人简介">
        <el-input
          v-model="formData.bio"
          type="textarea"
          :rows="3"
          placeholder="请输入个人简介"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          保存
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { updateProfile } from '@/api/modules/user-profile'

// Props
const props = defineProps({
  modelValue: Boolean,
  userData: Object
})

// Emits
const emit = defineEmits(['update:modelValue', 'updated'])

// 响应式数据
const visible = ref(false)
const submitting = ref(false)
const formRef = ref()

const formData = reactive({
  id: null,
  username: '',
  nickname: '',
  email: '',
  phone: '',
  gender: 0,
  birthday: '',
  bio: ''
})

const rules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

// 监听器
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.userData) {
    loadUserData()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 方法
const loadUserData = () => {
  Object.assign(formData, {
    id: props.userData.userId || props.userData.id,
    username: props.userData.username,
    nickname: props.userData.nickname || props.userData.username,
    email: props.userData.email,
    phone: props.userData.phone,
    gender: props.userData.gender || 0,
    birthday: props.userData.birthday,
    bio: props.userData.bio || props.userData.description || ''
  })
  
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    const submitData = { 
      nickname: formData.nickname,
      email: formData.email,
      phone: formData.phone,
      gender: formData.gender,
      birthday: formData.birthday,
      bio: formData.bio
    }
    
    // 调用API更新用户信息
    const response = await updateProfile(submitData)
    if (response.code === 200 || response.status === 200) {
      ElMessage.success('个人信息更新成功')
      emit('updated', { ...formData }) // 传递更新后的数据
      visible.value = false
    } else {
      ElMessage.error(response.message || '更新失败')
    }
  } catch (error) {
    console.error('更新个人信息失败:', error)
    ElMessage.error('更新失败，请稍后重试')
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