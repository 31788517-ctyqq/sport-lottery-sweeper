<template>
  <el-dialog
    title="缂栬緫涓汉淇℃伅"
    v-model="visible"
    width="500px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
      <el-form-item label="鐢ㄦ埛鍚? prop="username">
        <el-input v-model="formData.username" placeholder="璇疯緭鍏ョ敤鎴峰悕" disabled />
      </el-form-item>
      
      <el-form-item label="鏄电О" prop="nickname">
        <el-input v-model="formData.nickname" placeholder="璇疯緭鍏ユ樀绉? />
      </el-form-item>
      
      <el-form-item label="閭" prop="email">
        <el-input v-model="formData.email" placeholder="璇疯緭鍏ラ偖绠卞湴鍧€" />
      </el-form-item>
      
      <el-form-item label="鎵嬫満鍙? prop="phone">
        <el-input v-model="formData.phone" placeholder="璇疯緭鍏ユ墜鏈哄彿" />
      </el-form-item>
      
      <el-form-item label="鎬у埆" prop="gender">
        <el-radio-group v-model="formData.gender">
          <el-radio :value="1">鐢?/el-radio>
          <el-radio :value="2">濂?/el-radio>
          <el-radio :value="0">淇濆瘑</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="鐢熸棩" prop="birthday">
        <el-date-picker
          v-model="formData.birthday"
          type="date"
          placeholder="閫夋嫨鐢熸棩"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="涓汉绠€浠?>
        <el-input
          v-model="formData.bio"
          type="textarea"
          :rows="3"
          placeholder="璇疯緭鍏ヤ釜浜虹畝浠?
          maxlength="200"
          show-word-limit
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">鍙栨秷</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          淇濆瓨
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

// 鍝嶅簲寮忔暟鎹?const visible = ref(false)
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
    { required: true, message: '璇疯緭鍏ユ樀绉?, trigger: 'blur' },
    { min: 2, max: 20, message: '闀垮害鍦?2 鍒?20 涓瓧绗?, trigger: 'blur' }
  ],
  email: [
    { required: true, message: '璇疯緭鍏ラ偖绠卞湴鍧€', trigger: 'blur' },
    { type: 'email', message: '璇疯緭鍏ユ纭殑閭鍦板潃', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '璇疯緭鍏ユ纭殑鎵嬫満鍙?, trigger: 'blur' }
  ]
}

// 鐩戝惉鍣?watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.userData) {
    loadUserData()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 鏂规硶
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
    
    // 璋冪敤API鏇存柊鐢ㄦ埛淇℃伅
    const response = await updateProfile(submitData)
    if (response.code === 200 || response.status === 200) {
      ElMessage.success('涓汉淇℃伅鏇存柊鎴愬姛')
      emit('updated', { ...formData }) // 浼犻€掓洿鏂板悗鐨勬暟鎹?      visible.value = false
    } else {
      ElMessage.error(response.message || '鏇存柊澶辫触')
    }
  } catch (error) {
    console.error('鏇存柊涓汉淇℃伅澶辫触:', error)
    ElMessage.error('鏇存柊澶辫触锛岃绋嶅悗閲嶈瘯')
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  visible.value = false
}

// 鏆撮湶鏂规硶
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
