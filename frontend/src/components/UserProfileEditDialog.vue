<template>
  <el-dialog
    v-model="visible"
    title="编辑个人信息"
    width="500px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="formData.username" disabled />
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
          <el-radio :value="1">男</el-radio>
          <el-radio :value="2">女</el-radio>
          <el-radio :value="0">保密</el-radio>
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
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          保存
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { nextTick, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { updateProfile } from '@/api/modules/user-profile'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  userData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'updated'])

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
    { min: 2, max: 20, message: '昵称长度需在 2 到 20 个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

watch(
  () => props.modelValue,
  (val) => {
    visible.value = val
    if (val) {
      loadUserData()
    }
  },
  { immediate: true }
)

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const loadUserData = () => {
  const user = props.userData || {}
  Object.assign(formData, {
    id: user.userId || user.id || null,
    username: user.username || '',
    nickname: user.nickname || user.username || '',
    email: user.email || '',
    phone: user.phone || '',
    gender: Number(user.gender ?? 0),
    birthday: user.birthday || '',
    bio: user.bio || user.description || ''
  })
  nextTick(() => formRef.value?.clearValidate())
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true

    const payload = {
      nickname: formData.nickname,
      email: formData.email,
      phone: formData.phone,
      gender: formData.gender,
      birthday: formData.birthday,
      bio: formData.bio
    }

    const response = await updateProfile(payload)
    const success = response?.code === 200 || response?.status === 200
    if (!success) {
      throw new Error(response?.message || '更新失败')
    }

    ElMessage.success('个人信息更新成功')
    emit('updated', { ...formData })
    visible.value = false
  } catch (error) {
    const message = error?.message || '更新失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
