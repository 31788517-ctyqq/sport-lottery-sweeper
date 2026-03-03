<template>
  <div class="conversation-assistant">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>💬 对话助手</h3>
            <p class="subtitle">集成多个AI助手（体育分析师、赔率计算器、数据洞察）</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="createNewConversation">新建对话</el-button>
            <el-button @click="clearCurrentConversation">清空对话</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20" style="height: 600px;">
        <el-col :span="6" class="assistant-list-container">
          <el-card class="assistant-list-card">
            <template #header>
              <div class="assistant-list-header">
                <span>助手列表</span>
              </div>
            </template>
            <div class="assistant-list">
              <div 
                v-for="assistant in assistants" 
                :key="assistant.id"
                class="assistant-item"
                :class="{ active: currentAssistant.id === assistant.id }"
                @click="selectAssistant(assistant)"
              >
                <div class="assistant-info">
                  <i :class="assistant.icon" class="assistant-icon" />
                  <div class="assistant-details">
                    <span class="assistant-name">{{ assistant.name }}</span>
                    <span class="assistant-desc">{{ assistant.description }}</span>
                    <span v-if="assistant.model" class="assistant-model">{{ assistant.model }}</span>
                  </div>
                </div>
                <el-tag size="small" :type="getAssistantStatusTag(assistant.status)">
                  {{ assistant.status }}
                </el-tag>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="18" class="conversation-container">
          <el-card class="conversation-card">
            <template #header>
              <div class="conversation-header">
                <div class="current-assistant-info">
                  <i :class="currentAssistant.icon" class="assistant-icon" />
                  <span>{{ currentAssistant.name }}</span>
                  <el-tag v-if="currentAssistant.model" size="small" type="info">{{ currentAssistant.model }}</el-tag>
                </div>
                <div class="conversation-actions">
                  <el-button size="small" @click="clearCurrentConversation">清空对话</el-button>
                  <el-button size="small" @click="exportConversation">导出对话</el-button>
                </div>
              </div>
            </template>
            
            <div class="messages-container">
              <div 
                v-for="(msg, index) in currentAssistant.conversation" 
                :key="index"
                class="message"
                :class="msg.sender"
              >
                <div class="message-content">
                  <i 
                    :class="msg.sender === 'user' ? 'el-icon-user' : currentAssistant.icon" 
                    class="message-icon"
                  />
                  <div class="message-bubble">
                    <pre class="message-text">{{ msg.text }}</pre>
                    <div class="message-meta">
                      {{ msg.timestamp }}
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-if="isLoading" class="message ai">
                <div class="message-content">
                  <i :class="currentAssistant.icon" class="message-icon" />
                  <div class="message-bubble">
                    <div class="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="input-area">
              <el-input
                v-model="inputMessage"
                type="textarea"
                :rows="4"
                placeholder="输入您的问题..."
                @keydown.enter="sendMessage"
                :disabled="isLoading"
              />
              <div class="input-controls">
                <el-button 
                  type="primary" 
                  @click="sendMessage" 
                  :disabled="!inputMessage.trim() || isLoading"
                  :loading="isLoading"
                >
                  发送
                </el-button>
                <el-button @click="clearInput">清空</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { API_ENDPOINTS } from '@/config/api.js'

// 助手数据
const assistants = ref([
  {
    id: 1,
    name: '体育分析师助手',
    description: '专业体育赛事分析',
    icon: 'el-icon-football',
    status: 'online',
    provider: 'zhipuai',
    model: 'glm-4',
    conversation: [
      { 
        sender: 'ai', 
        text: '您好！我是体育分析师助手，我可以帮助您分析比赛数据、预测结果、评估球队表现等。请问您想了解什么？', 
        timestamp: new Date().toLocaleString('zh-CN') 
      }
    ]
  },
  {
    id: 2,
    name: '赔率计算器',
    description: '赔率分析与计算',
    icon: 'el-icon-wallet',
    status: 'online',
    provider: 'zhipuai',
    model: 'glm-4',
    conversation: [
      { 
        sender: 'ai', 
        text: '您好！我是赔率计算器，可以帮助您计算各种投注策略的预期收益、分析赔率变化趋势等。请告诉我您的需求。', 
        timestamp: new Date().toLocaleString('zh-CN') 
      }
    ]
  },
  {
    id: 3,
    name: '数据洞察助手',
    description: '数据分析与洞察',
    icon: 'el-icon-data-analysis',
    status: 'online',
    provider: 'zhipuai',
    model: 'glm-4',
    conversation: [
      { 
        sender: 'ai', 
        text: '您好！我是数据洞察助手，专注于体育数据的深度分析，提供有价值的洞察和趋势分析。您想分析哪些数据？', 
        timestamp: new Date().toLocaleString('zh-CN') 
      }
    ]
  },
  {
    id: 4,
    name: '策略规划师',
    description: '投注策略制定',
    icon: 'el-icon-guide',
    status: 'offline',
    provider: 'zhipuai',
    model: 'glm-4',
    conversation: []
  },
  {
    id: 5,
    name: 'MY_ZP_BIGMODLE 助手',
    description: '智谱大模型服务接入',
    icon: 'el-icon-cpu',
    status: 'online',
    provider: 'zhipuai',
    model: 'MY_ZP_BIGMODLE',
    conversation: [
      {
        sender: 'ai',
        text: '您好！我是 MY_ZP_BIGMODLE 助手，当前通过智谱AI服务提供对话能力。请告诉我您的问题。',
        timestamp: new Date().toLocaleString('zh-CN')
      }
    ]
  }
])

const currentAssistant = ref(assistants.value[0])
const inputMessage = ref('')
const isLoading = ref(false)

// 方法
const getAssistantStatusTag = (status) => {
  return status === 'online' ? 'success' : 'danger'
}

const selectAssistant = (assistant) => {
  if (assistant.status !== 'online') {
    ElMessage.warning('该助手当前不在线')
    return
  }
  currentAssistant.value = assistant
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return
  
  // 添加用户消息
  const userMessage = {
    sender: 'user',
    text: inputMessage.value,
    timestamp: new Date().toLocaleString('zh-CN', { hour12: false })
  }
  
  currentAssistant.value.conversation.push(userMessage)
  const inputCopy = inputMessage.value
  inputMessage.value = ''
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  // 显示加载状态
  isLoading.value = true
  
  try {
    // 调用后端LLM API，根据当前助手动态选择 provider / model
    const response = await axios.post(API_ENDPOINTS.LLM.CHAT, {
      user_input: inputCopy,
      provider: currentAssistant.value.provider || 'zhipuai',
      model: currentAssistant.value.model || undefined,
      user_id: `assistant_${currentAssistant.value.id}`
    })
    
    const aiResponse = {
      sender: 'ai',
      text: response.data.response,
      timestamp: new Date().toLocaleString('zh-CN', { hour12: false })
    }
    
    currentAssistant.value.conversation.push(aiResponse)
  } catch (error) {
    console.error('AI对话失败:', error)
    let errorMessage = '抱歉，AI服务暂时不可用，请稍后再试。'
    
    if (error.response) {
      if (error.response.status === 401) {
        errorMessage = '认证已过期，请重新登录。'
        // 可以在这里添加自动跳转到登录页的逻辑
      } else if (error.response.status === 500) {
        errorMessage = `AI服务错误: ${error.response.data?.detail || '未知错误'}`
      } else if (error.response.status === 400) {
        errorMessage = '请求参数错误，请检查输入内容。'
      }
    }
    
    const aiResponse = {
      sender: 'ai',
      text: errorMessage,
      timestamp: new Date().toLocaleString('zh-CN', { hour12: false })
    }
    
    currentAssistant.value.conversation.push(aiResponse)
    ElMessage.error(errorMessage)
  } finally {
    isLoading.value = false
    
    // 滚动到底部
    nextTick(() => {
      scrollToBottom()
    })
  }
}

const scrollToBottom = () => {
  const container = document.querySelector('.messages-container')
  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

const clearCurrentConversation = () => {
  // 保留初始欢迎消息
  currentAssistant.value.conversation = [
    { 
      sender: 'ai', 
      text: `您好！我是${currentAssistant.value.name}，${currentAssistant.value.description}。请问您需要什么帮助？`, 
      timestamp: new Date().toLocaleString('zh-CN', { hour12: false }) 
    }
  ]
  ElMessage.success('对话已清空')
}

const createNewConversation = () => {
  ElMessage.info('新建对话功能将在后续版本中实现')
}

const exportConversation = () => {
  ElMessage.info('导出对话功能将在后续版本中实现')
}

const clearInput = () => {
  inputMessage.value = ''
}
</script>

<style scoped>
.card-container {
  margin: 20px;
  height: calc(100vh - 160px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-header > div:first-child h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.assistant-list-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.assistant-list-card {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.assistant-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.assistant-list {
  flex: 1;
  overflow-y: auto;
  max-height: 500px;
}

.assistant-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 10px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s;
}

.assistant-item:hover {
  border-color: #c6e2ff;
  background-color: #ecf5ff;
}

.assistant-item.active {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.assistant-info {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 10px;
}

.assistant-icon {
  font-size: 18px;
  color: #409eff;
}

.assistant-details {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.assistant-name {
  font-weight: bold;
  margin-bottom: 4px;
}

.assistant-desc {
  font-size: 12px;
  color: #909399;
}

.assistant-model {
  margin-top: 4px;
  font-size: 11px;
  color: #607d8b;
  word-break: break-all;
}

.conversation-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.conversation-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.current-assistant-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  background-color: #f5f7fa;
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  display: flex;
  margin-bottom: 10px;
}

.message.user {
  justify-content: flex-end;
}

.message-content {
  display: flex;
  max-width: 80%;
  gap: 8px;
}

.message.user .message-content {
  flex-direction: row-reverse;
}

.message-icon {
  font-size: 18px;
  color: #409eff;
  align-self: flex-start;
}

.message-bubble {
  display: flex;
  flex-direction: column;
}

.message-text {
  padding: 12px 16px;
  border-radius: 18px;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
}

.message.user .message-text {
  background-color: #409eff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.ai .message-text {
  background-color: white;
  color: #303133;
  border-bottom-left-radius: 4px;
}

.message-meta {
  font-size: 12px;
  color: #909399;
  text-align: right;
  margin-top: 4px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: #409eff;
  border-radius: 50%;
  display: inline-block;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}

.input-area {
  margin-top: auto;
}

.input-controls {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}
</style>
