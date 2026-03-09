<template>
  <div class="not-found-container">
    <!-- Animated Background -->
    <div class="not-found-bg">
      <div class="floating-element element-1"></div>
      <div class="floating-element element-2"></div>
      <div class="floating-element element-3"></div>
      <div class="floating-element element-4"></div>
    </div>

    <!-- Main Content -->
    <div class="not-found-content">
      <!-- Error Code -->
      <div class="error-code">
        <span class="digit">4</span>
        <span class="digit">0</span>
        <span class="digit">4</span>
      </div>

      <!-- Error Message -->
      <div class="error-message">
        <h1>页面走丢了</h1>
        <p class="error-desc">抱歉，您访问的页面不存在或已被移除</p>
        <p class="error-suggestion">请检查URL是否正确，或返回首页继续浏览</p>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button 
          type="primary" 
          size="large" 
          :icon="House" 
          @click="goHome"
          class="btn-home"
        >
          返回首页
        </el-button>
        <el-button 
          size="large" 
          :icon="ArrowLeft" 
          @click="goBack"
          class="btn-back"
        >
          返回上页
        </el-button>
      </div>

      <!-- Quick Links -->
      <div class="quick-links">
        <p class="links-title">快速访问：</p>
        <div class="links-grid">
          <el-button 
            v-for="link in quickLinks" 
            :key="link.path"
            :icon="link.icon"
            @click="goToPage(link.path)"
            class="quick-link-btn"
          >
            {{ link.title }}
          </el-button>
        </div>
      </div>

      <!-- Search Box -->
      <div class="search-box">
        <p class="search-title">或者搜索您需要的内容：</p>
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索页面或功能..."
          size="large"
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
          <template #append>
            <el-button :icon="Search" @click="handleSearch" />
          </template>
        </el-input>
      </div>
    </div>

    <!-- Footer Info -->
    <div class="not-found-footer">
      <p>如果问题持续存在，请联系系统管理员</p>
      <div class="contact-info">
        <el-icon><Phone /></el-icon>
        <span>技术支持：400-888-8888</span>
      </div>
    </div>

    <!-- Animated Illustration -->
    <div class="illustration">
      <div class="astronaut">
        <div class="helmet">
          <div class="helmet-reflection"></div>
        </div>
        <div class="body">
          <div class="backpack"></div>
        </div>
        <div class="arm arm-left"></div>
        <div class="arm arm-right"></div>
        <div class="leg leg-left"></div>
        <div class="leg leg-right"></div>
      </div>
      <div class="planet">
        <div class="crater crater-1"></div>
        <div class="crater crater-2"></div>
        <div class="crater crater-3"></div>
      </div>
      <div class="stars">
        <div class="star star-1">★</div>
        <div class="star star-2">★</div>
        <div class="star star-3">★</div>
        <div class="star star-4">★</div>
        <div class="star star-5">★</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  House, ArrowLeft, Search, Phone, 
  Collection, User, Setting, Trophy 
} from '@element-plus/icons-vue'

const router = useRouter()
const searchKeyword = ref('')

// Quick links for navigation
const quickLinks = ref([
  { title: '管理仪表板', path: '/admin/dashboard', icon: House },
  { title: '情报管理', path: '/admin/intelligence/dashboard', icon: Collection },
  { title: '用户管理', path: '/admin/users', icon: User },
  { title: '系统设置', path: '/admin/settings', icon: Setting },
  { title: '数据分析', path: '/admin/dashboard', icon: Trophy }
])

// Navigation methods
const goHome = () => {
  router.push('/admin/dashboard')
}

const goBack = () => {
  router.go(-1)
}

const goToPage = (path) => {
  router.push(path)
}

const handleSearch = () => {
  if (!searchKeyword.value.trim()) return
  
  // Simple search logic - in real app, this would search through available pages
  const keyword = searchKeyword.value.toLowerCase()
  const foundLink = quickLinks.value.find(link => 
    link.title.toLowerCase().includes(keyword) ||
    link.path.toLowerCase().includes(keyword)
  )
  
  if (foundLink) {
    router.push(foundLink.path)
  } else {
    // Show search suggestions or redirect to search results
    console.log('Search for:', keyword)
    // You could implement a global search here
  }
}
</script>

<style scoped>
.not-found-container {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  overflow: hidden;
}

.not-found-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.floating-element {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: floatAround 8s ease-in-out infinite;
}

.element-1 {
  width: 80px;
  height: 80px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.element-2 {
  width: 120px;
  height: 120px;
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.element-3 {
  width: 60px;
  height: 60px;
  bottom: 30%;
  left: 20%;
  animation-delay: 4s;
}

.element-4 {
  width: 100px;
  height: 100px;
  top: 10%;
  right: 30%;
  animation-delay: 6s;
}

@keyframes floatAround {
  0%, 100% { 
    transform: translateY(0px) rotate(0deg); 
    opacity: 0.7;
  }
  25% { 
    transform: translateY(-30px) rotate(90deg); 
    opacity: 1;
  }
  50% { 
    transform: translateY(-60px) rotate(180deg); 
    opacity: 0.8;
  }
  75% { 
    transform: translateY(-30px) rotate(270deg); 
    opacity: 0.9;
  }
}

.not-found-content {
  position: relative;
  z-index: 2;
  text-align: center;
  max-width: 800px;
  width: 100%;
}

.error-code {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

.digit {
  font-size: 120px;
  font-weight: 900;
  color: white;
  text-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
  animation: bounce 2s ease-in-out infinite;
  position: relative;
}

.digit:nth-child(1) { animation-delay: 0s; }
.digit:nth-child(2) { animation-delay: 0.2s; }
.digit:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-20px); }
  60% { transform: translateY(-10px); }
}

.error-message {
  margin-bottom: 40px;
}

.error-message h1 {
  margin: 0 0 16px 0;
  color: white;
  font-size: 32px;
  font-weight: 600;
}

.error-desc {
  margin: 0 0 8px 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
}

.error-suggestion {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.btn-home {
  height: 48px;
  padding: 0 32px;
  font-size: 16px;
  border-radius: 24px;
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  border: none;
  box-shadow: 0 8px 25px rgba(238, 90, 36, 0.3);
}

.btn-home:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(238, 90, 36, 0.4);
}

.btn-back {
  height: 48px;
  padding: 0 32px;
  font-size: 16px;
  border-radius: 24px;
  border: 2px solid white;
  color: white;
  background: transparent;
}

.btn-back:hover {
  background: white;
  color: #667eea;
  transform: translateY(-2px);
}

.quick-links {
  margin-bottom: 40px;
}

.links-title {
  margin: 0 0 16px 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
}

.links-grid {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.quick-link-btn {
  height: 40px;
  padding: 0 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  backdrop-filter: blur(10px);
}

.quick-link-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.search-box {
  margin-bottom: 40px;
}

.search-title {
  margin: 0 0 16px 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
}

.search-input {
  max-width: 400px;
  margin: 0 auto;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.search-input :deep(.el-input__inner) {
  color: #333;
}

.not-found-footer {
  position: relative;
  z-index: 2;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
}

.not-found-footer p {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.contact-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
}

/* Illustration Styles */
.illustration {
  position: absolute;
  top: 50%;
  right: 5%;
  transform: translateY(-50%);
  z-index: 1;
  opacity: 0.6;
}

.astronaut {
  position: relative;
  width: 100px;
  height: 120px;
  animation: astronautFloat 4s ease-in-out infinite;
}

@keyframes astronautFloat {
  0%, 100% { transform: translateY(0px) rotate(-5deg); }
  50% { transform: translateY(-15px) rotate(5deg); }
}

.helmet {
  width: 60px;
  height: 60px;
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 0;
  left: 20px;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.1);
}

.helmet-reflection {
  width: 20px;
  height: 20px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  position: absolute;
  top: 15px;
  left: 15px;
}

.body {
  width: 50px;
  height: 40px;
  background: white;
  border-radius: 25px;
  position: absolute;
  top: 50px;
  left: 25px;
}

.backpack {
  width: 20px;
  height: 25px;
  background: #ddd;
  border-radius: 10px;
  position: absolute;
  top: 5px;
  right: 5px;
}

.arm {
  width: 15px;
  height: 30px;
  background: white;
  border-radius: 10px;
  position: absolute;
  top: 60px;
}

.arm-left {
  left: 10px;
  transform: rotate(-20deg);
}

.arm-right {
  right: 10px;
  transform: rotate(20deg);
}

.leg {
  width: 12px;
  height: 25px;
  background: white;
  border-radius: 8px;
  position: absolute;
  top: 85px;
}

.leg-left {
  left: 30px;
}

.leg-right {
  right: 30px;
}

.planet {
  width: 80px;
  height: 80px;
  background: linear-gradient(45deg, #ff9a9e, #fecfef);
  border-radius: 50%;
  position: absolute;
  bottom: -40px;
  left: -40px;
  animation: planetRotate 10s linear infinite;
}

@keyframes planetRotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.crater {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  position: absolute;
}

.crater-1 {
  width: 15px;
  height: 15px;
  top: 20px;
  left: 20px;
}

.crater-2 {
  width: 10px;
  height: 10px;
  top: 40px;
  left: 50px;
}

.crater-3 {
  width: 8px;
  height: 8px;
  top: 15px;
  right: 20px;
}

.stars {
  position: absolute;
  top: -50px;
  left: -50px;
}

.star {
  position: absolute;
  color: white;
  font-size: 12px;
  animation: twinkle 2s ease-in-out infinite;
}

.star-1 { top: 10px; left: 20px; animation-delay: 0s; }
.star-2 { top: 30px; left: 60px; animation-delay: 0.4s; }
.star-3 { top: 50px; left: 10px; animation-delay: 0.8s; }
.star-4 { top: 70px; left: 70px; animation-delay: 1.2s; }
.star-5 { top: 20px; left: 80px; animation-delay: 1.6s; }

@keyframes twinkle {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .error-code {
    gap: 10px;
  }
  
  .digit {
    font-size: 80px;
  }
  
  .error-message h1 {
    font-size: 24px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .btn-home, .btn-back {
    width: 200px;
  }
  
  .illustration {
    display: none;
  }
  
  .links-grid {
    flex-direction: column;
    align-items: center;
  }
  
  .quick-link-btn {
    width: 200px;
  }
}
</style>