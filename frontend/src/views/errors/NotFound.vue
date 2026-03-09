<template>
  <div class="error-container">
    <div class="error-content">
      <div class="error-code">404</div>
      <div class="error-title">页面未找到</div>
      <div class="error-description">
        抱歉，您访问的页面不存在
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="goBack">返回上一页</el-button>
        <el-button @click="goHome">返回首页</el-button>
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
  router.push('/')
}
</script>

<style scoped>
.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.error-content {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #909399;
  line-height: 1;
  margin-bottom: 20px;
}

.error-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 16px;
}

.error-description {
  font-size: 16px;
  color: #666;
  margin-bottom: 30px;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
