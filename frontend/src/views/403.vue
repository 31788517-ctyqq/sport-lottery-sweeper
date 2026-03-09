<template>
  <div class="error-page">
    <div class="error-container">
      <div class="error-code">403</div>
      <div class="error-title">访问被拒绝</div>
      <div class="error-message">
        抱歉，您没有权限访问此页面
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="goBack">返回上一页</el-button>
        <el-button @click="goHome">回到首页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.go(-1)
}

const goHome = () => {
  router.push('/admin/dashboard')
}
</script>

<style scoped>
.error-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
}

.error-container {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #f56c6c;
  line-height: 1;
  margin-bottom: 20px;
}

.error-title {
  font-size: 24px;
  color: #303133;
  margin-bottom: 16px;
}

.error-message {
  font-size: 16px;
  color: #606266;
  margin-bottom: 30px;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>