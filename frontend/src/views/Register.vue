<template>
  <div class="register-container">
    <el-card class="register-card" style="max-width: 480px; margin: 40px auto;">
      <template #header>
        <div class="card-header">
          <span>用户注册</span>
        </div>
      </template>
      
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="请输入用户名"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="form.email" 
            placeholder="请输入邮箱"
            prefix-icon="Message"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码"
            show-password
            prefix-icon="Lock"
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="form.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            show-password
            prefix-icon="Lock"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="onSubmit" 
            style="width: 100%;"
            :loading="loading"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-link">
        <span>已有账号？</span>
        <el-link type="primary" href="/login">立即登录</el-link>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';

export default {
  name: 'Register',
  setup() {
    const router = useRouter();
    const formRef = ref();
    const loading = ref(false);
    
    const form = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    });
    
    const validatePassword = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'));
      } else if (value !== form.password) {
        callback(new Error('两次输入的密码不一致'));
      } else {
        callback();
      }
    };
    
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 15, message: '用户名长度应在3-15个字符之间', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
      ],
      confirmPassword: [
        { validator: validatePassword, trigger: 'blur' }
      ]
    };
    
    const onSubmit = async () => {
      try {
        await formRef.value.validate();
        
        loading.value = true;
        
        // 这里应该调用实际的注册API
        // 模拟注册过程
        setTimeout(() => {
          loading.value = false;
          ElMessage.success('注册成功，请登录');
          router.push('/login');
        }, 1500);
      } catch (error) {
        console.error('表单验证失败:', error);
      }
    };
    
    return {
      formRef,
      form,
      rules,
      loading,
      onSubmit
    };
  }
};
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.register-card {
  width: 100%;
  max-width: 480px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  text-align: center;
  font-size: 18px;
  font-weight: bold;
}

.login-link {
  text-align: center;
  margin-top: 20px;
}
</style>