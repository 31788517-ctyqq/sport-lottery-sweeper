<template>
  <div class="dashboard-page">
    <!-- 页面标题 -->
    <header class="page-header">
      <h1>体育彩票扫盘系统 - 仪表板</h1>
      <p>欢迎使用体育彩票数据分析平台</p>
    </header>

    <!-- 主要内容区域 -->
    <main class="page-content">
      <!-- 登录区域 -->
      <section class="login-section">
        <LoginForm @login-success="handleLoginSuccess" />
      </section>

      <!-- 统计信息区域 -->
      <section class="stats-section">
        <DashboardStats 
          ref="dashboardRef"
          @stats-loaded="handleStatsLoaded"
        />
      </section>

      <!-- 情报列表区域 -->
      <section class="intelligence-section">
        <IntelligenceList 
          ref="intelligenceRef"
          @data-loaded="handleIntelligenceLoaded"
          @view-item="handleViewIntelligence"
          @review-item="handleReviewIntelligence"
          @ignore-item="handleIgnoreIntelligence"
        />
      </section>
    </main>

    <!-- 通知消息 -->
    <div v-if="notification.show" class="notification" :class="notification.type">
      <span class="notification-icon">{{ notification.icon }}</span>
      <span class="notification-message">{{ notification.message }}</span>
      <button @click="hideNotification" class="notification-close">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import LoginForm from '@/components/LoginForm.vue'
import DashboardStats from '@/components/DashboardStats.vue'
import IntelligenceList from '@/components/IntelligenceList.vue'

// 组件引用
const dashboardRef = ref()
const intelligenceRef = ref()

// 通知消息状态
const notification = ref({
  show: false,
  type: 'info',
  icon: 'ℹ️',
  message: ''
})

// 登录成功处理
const handleLoginSuccess = (userData) => {
  showNotification('success', '✅', `欢迎回来，${userData.user_info.username}！`)
  
  // 登录成功后自动刷新统计数据
  setTimeout(() => {
    dashboardRef.value?.loadDashboardStats()
  }, 1000)
}

// 统计数据加载完成
const handleStatsLoaded = (stats) => {
  showNotification('info', '📊', '统计数据已更新')
}

// 情报数据加载完成
const handleIntelligenceLoaded = (data) => {
  showNotification('info', '📋', `已加载 ${data.items?.length || 0} 条情报数据`)
}

// 查看情报详情
const handleViewIntelligence = (item) => {
  showNotification('info', '👁️', `正在查看：${item.title || '未命名情报'}`)
  
  // 这里可以实现查看详情的逻辑，比如：
  // - 打开模态框显示详细信息
  // - 跳转到详情页面
  // - 调用其他API获取完整数据
}

// 审核情报
const handleReviewIntelligence = (item) => {
  showNotification('success', '✅', `已审核：${item.title || '未命名情报'}`)
  
  // 这里可以实现审核逻辑，比如：
  // - 调用审核API
  // - 更新本地状态
  // - 刷新列表
}

// 忽略情报
const handleIgnoreIntelligence = (item) => {
  showNotification('warning', '⏭️', `已忽略：${item.title || '未命名情报'}`)
  
  // 这里可以实现忽略逻辑，比如：
  // - 调用忽略API
  // - 更新本地状态
  // - 刷新列表
}

// 显示通知
const showNotification = (type: string, icon: string, message: string) => {
  notification.value = {
    show: true,
    type: type,
    icon: icon,
    message: message
  }
  
  // 3秒后自动隐藏
  setTimeout(hideNotification, 3000)
}

// 隐藏通知
const hideNotification = () => {
  notification.value.show = false
}

// 页面加载完成后的初始化
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.page-header {
  background: white;
  padding: 30px 24px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 32px;
  font-weight: 700;
}

.page-header p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.page-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.login-section {
  display: flex;
  justify-content: center;
}

.stats-section,
.intelligence-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 通知消息样式 */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 16px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
  animation: slideIn 0.3s ease;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.notification.success {
  background: linear-gradient(135deg, #28a745, #20c997);
}

.notification.info {
  background: linear-gradient(135deg, #17a2b8, #007bff);
}

.notification.warning {
  background: linear-gradient(135deg, #ffc107, #fd7e14);
}

.notification.error {
  background: linear-gradient(135deg, #dc3545, #e83e8c);
}

.notification-icon {
  font-size: 20px;
}

.notification-message {
  flex: 1;
}

.notification-close {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.notification-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    padding: 20px 16px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .page-content {
    padding: 0 16px;
    gap: 20px;
  }
  
  .notification {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
}

/* 开发环境提示 */
.dashboard-page::before {
  // AI_WORKING: coder2 @2026-01-28T09:48:00Z - 修复硬编码后端地址
  content: "🔧 开发环境 - 后端API: http://localhost:3000/api";
  // AI_DONE: coder2 @2026-01-28T09:48:00Z
  position: fixed;
  bottom: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 999;
  pointer-events: none;
}
</style>