<template>
  <div
    style="
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    "
  >
    <el-card style="width: 400px; padding: 20px">
      <div style="text-align: center; margin-bottom: 20px">
        <h2>竞彩扫盘管理后台</h2>
        <p style="color: #666">请登录以继续</p>
      </div>
      <el-form :model="form" :rules="rules" ref="loginForm" label-width="0">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            style="width: 100%"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const form = ref({ username: '', password: '' })
const loading = ref(false)
const loginForm = ref(null)

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  loginForm.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      // 调用后端登录接口
      const data = await request.post('/auth/login', form.value)
      // 假设返回 { token: '...' }
      localStorage.setItem('token', data.token)
      // 如果有 userStore，可同步存储
      // userStore.setToken(data.token)
      ElMessage.success('登录成功')
      router.push('/admin/dashboard')
    } catch (error) {
      ElMessage.error(error.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}
</script>