<template>
  <el-dialog
    class="um-dialog"
    title="编辑个人信息"
    v-model="visible"
    width="500px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="头像">
            <div class="avatar-upload">
              <el-avatar :size="60" :src="formData.avatar || defaultAvatar">
                {{ (formData.realName || formData.username || 'U').charAt(0) }}
              </el-avatar>
              <el-upload
                class="upload-btn"
                :show-file-list="false"
                accept="image/*"
                :before-upload="beforeAvatarUpload"
              >
                <el-button size="small" type="primary">更换</el-button>
              </el-upload>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="用户名">
            <el-input v-model="formData.username" name="username" disabled />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="真实姓名" prop="realName">
        <el-input v-model="formData.realName" name="real_name" placeholder="请输入真实姓名" />
      </el-form-item>

      <el-form-item label="邮箱" prop="email">
        <el-input v-model="formData.email" name="email" placeholder="请输入邮箱地址" />
      </el-form-item>

      <el-form-item label="手机号" prop="phone">
        <el-input v-model="formData.phone" name="phone" placeholder="请输入手机号" />
      </el-form-item>

      <el-form-item label="性别" prop="gender">
        <el-radio-group v-model="formData.gender" name="gender">
          <el-radio :value="1">男</el-radio>
          <el-radio :value="2">女</el-radio>
          <el-radio :value="0">保密</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="生日" prop="birthday">
        <el-date-picker
          v-model="formData.birthday"
          name="birthday"
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
          name="bio"
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
import http from '@/utils/http'

const props = defineProps({
  modelValue: Boolean,
  userInfo: Object
})

const emit = defineEmits(['update:modelValue', 'saved'])

const visible = ref(false)
const submitting = ref(false)
const formRef = ref()

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const formData = reactive({
  id: null,
  username: '',
  realName: '',
  email: '',
  phone: '',
  gender: 0,
  birthday: '',
  avatar: '',
  bio: ''
})

const rules = {
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
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

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.userInfo) {
    loadUserData()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const loadUserData = () => {
  const prefs = props.userInfo?.preferences || {}
  Object.assign(formData, {
    id: props.userInfo?.id || null,
    username: props.userInfo?.username || '',
    realName: props.userInfo?.realName || props.userInfo?.real_name || '',
    email: props.userInfo?.email || '',
    phone: props.userInfo?.phone || '',
    gender: props.userInfo?.gender ?? prefs.gender ?? 0,
    birthday: props.userInfo?.birthday || prefs.birthday || '',
    avatar: props.userInfo?.avatar || prefs.avatar || '',
    bio: props.userInfo?.bio || prefs.bio || ''
  })

  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB')
    return false
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    formData.avatar = e.target?.result
  }
  reader.readAsDataURL(file)

  return false
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    const submitData = {
      real_name: formData.realName,
      email: formData.email,
      phone: formData.phone,
      preferences: {
        avatar: formData.avatar,
        bio: formData.bio,
        gender: formData.gender,
        birthday: formData.birthday
      }
    }

    await http.put('/api/v1/admin/admin-users/current-user', submitData)

    ElMessage.success('个人信息更新成功')
    emit('saved', submitData)
    visible.value = false
  } catch (error) {
    console.error('更新个人信息失败:', error)
    ElMessage.error(error?.message || '更新失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  visible.value = false
}

defineExpose({
  visible
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

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.upload-btn {
  margin-left: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
