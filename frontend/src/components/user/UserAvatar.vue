<template>
  <div class="user-avatar" :class="avatarClasses" :style="avatarStyles">
    <!-- 头像图片 -->
    <img
      v-if="src && !hasError"
      :src="src"
      :alt="altText"
      @error="handleImageError"
      class="avatar-image"
    />
    
    <!-- 默认头像（字母或图标） -->
    <div v-else class="avatar-default">
      <span v-if="!useIcon" class="avatar-initial">
        {{ initial }}
      </span>
      <i v-else class="avatar-icon fas fa-user"></i>
    </div>

    <!-- 上传控件 -->
    <input
      v-if="editable"
      ref="fileInput"
      type="file"
      accept="image/*"
      class="avatar-upload-input"
      @change="handleFileSelect"
    />
    
    <!-- 状态指示器 -->
    <div
      v-if="showStatus && status"
      class="avatar-status"
      :class="`status-${status}`"
      :title="statusText"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

// Props
interface Props {
  src?: string
  username?: string
  size?: number
  shape?: 'circle' | 'square' | 'rounded'
  status?: 'online' | 'offline' | 'busy' | 'away'
  showStatus?: boolean
  editable?: boolean
  useIcon?: boolean
  border?: boolean
  clickable?: boolean
  uploadSizeLimit?: number // MB
}

const props = withDefaults(defineProps<Props>(), {
  src: undefined,
  username: '用户',
  size: 40,
  shape: 'circle',
  status: 'offline',
  showStatus: false,
  editable: false,
  useIcon: false,
  border: false,
  clickable: false,
  uploadSizeLimit: 2
})

// Emits
const emit = defineEmits<{
  'avatar-click': []
  'avatar-change': [file: File]
  'upload-error': [error: string]
}>()

// Refs
const hasError = ref(false)
const fileInput = ref<HTMLInputElement>()

// Computed
const avatarClasses = computed(() => ({
  [`avatar-${props.shape}`]: true,
  'avatar-border': props.border,
  'avatar-clickable': props.clickable,
  'avatar-editable': props.editable
}))

const avatarStyles = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  fontSize: `${props.size * 0.4}px`
}))

const altText = computed(() => `${props.username}的头像`)

const initial = computed(() => {
  if (!props.username) return 'U'
  
  // 中文取最后一个字符，英文取第一个字母
  const char = props.username.trim()
  const lastChar = char[char.length - 1]
  
  // 判断是否是中文字符
  const isChinese = /[\u4e00-\u9fff]/.test(lastChar)
  
  if (isChinese) {
    return lastChar
  } else {
    return char.charAt(0).toUpperCase()
  }
})

const statusText = computed(() => {
  const statusMap = {
    online: '在线',
    offline: '离线',
    busy: '忙碌',
    away: '离开'
  }
  return statusMap[props.status]
})

// Methods
const handleImageError = () => {
  hasError.value = true
}

const handleClick = () => {
  if (props.clickable) {
    emit('avatar-click')
  }
  
  if (props.editable && fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  
  if (!file) return
  
  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    emit('upload-error', '请选择图片文件')
    resetFileInput()
    return
  }
  
  // 验证文件大小
  if (file.size > props.uploadSizeLimit * 1024 * 1024) {
    emit('upload-error', `图片大小不能超过 ${props.uploadSizeLimit}MB`)
    resetFileInput()
    return
  }
  
  // 验证图片尺寸
  validateImageDimensions(file)
}

const validateImageDimensions = (file: File) => {
  const reader = new FileReader()
  
  reader.onload = (e) => {
    const img = new Image()
    
    img.onload = () => {
      // 检查最小尺寸
      const minSize = 100
      if (img.width < minSize || img.height < minSize) {
        emit('upload-error', `图片尺寸过小，建议至少 ${minSize}x${minSize} 像素`)
        resetFileInput()
        return
      }
      
      // 检查宽高比
      const aspectRatio = img.width / img.height
      if (aspectRatio < 0.8 || aspectRatio > 1.2) {
        emit('upload-error', '建议使用接近正方形（1:1）的图片')
        resetFileInput()
        return
      }
      
      // 验证通过
      emit('avatar-change', file)
      resetFileInput()
    }
    
    img.onerror = () => {
      emit('upload-error', '图片加载失败，请重试')
      resetFileInput()
    }
    
    img.src = e.target?.result as string
  }
  
  reader.onerror = () => {
    emit('upload-error', '文件读取失败')
    resetFileInput()
  }
  
  reader.readAsDataURL(file)
}

const resetFileInput = () => {
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Lifecycle
onMounted(() => {
  hasError.value = !props.src
})

// Watch
watch(() => props.src, (newSrc) => {
  hasError.value = !newSrc
})
</script>

<style scoped>
.user-avatar {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  user-select: none;
  flex-shrink: 0;
}

.avatar-circle {
  border-radius: 50%;
}

.avatar-square {
  border-radius: 4px;
}

.avatar-rounded {
  border-radius: 20%;
}

.avatar-border {
  border: 2px solid var(--border-color);
}

.avatar-clickable {
  cursor: pointer;
}

.avatar-clickable:hover {
  opacity: 0.9;
  transform: scale(1.05);
  transition: transform 0.2s ease;
}

.avatar-editable {
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.avatar-editable:hover::after {
  content: '更换头像';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  border-radius: inherit;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: inherit;
}

.avatar-default {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  border-radius: inherit;
}

.avatar-initial {
  font-weight: 600;
  color: var(--primary);
  text-transform: uppercase;
}

.avatar-icon {
  font-size: 60%;
  color: var(--text-secondary);
}

.avatar-upload-input {
  display: none;
}

.avatar-status {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 30%;
  height: 30%;
  border: 2px solid var(--bg-primary);
  border-radius: 50%;
}

.status-online {
  background-color: var(--success);
}

.status-offline {
  background-color: var(--text-secondary);
}

.status-busy {
  background-color: var(--error);
}

.status-away {
  background-color: var(--warning);
}

/* 尺寸变体 */
:global(.avatar-xs) {
  width: 24px !important;
  height: 24px !important;
  font-size: 10px !important;
}

:global(.avatar-sm) {
  width: 32px !important;
  height: 32px !important;
  font-size: 13px !important;
}

:global(.avatar-md) {
  width: 40px !important;
  height: 40px !important;
  font-size: 16px !important;
}

:global(.avatar-lg) {
  width: 56px !important;
  height: 56px !important;
  font-size: 22px !important;
}

:global(.avatar-xl) {
  width: 80px !important;
  height: 80px !important;
  font-size: 32px !important;
}
</style>