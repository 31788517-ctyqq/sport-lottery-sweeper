<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" class="settings-tabs">
        <el-tab-pane label="个人信息" name="profile">
          <el-form :model="profileForm" label-width="120px" style="max-width: 600px;">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" />
            </el-form-item>
            
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            
            <el-form-item label="手机号">
              <el-input v-model="profileForm.phone" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updateProfile">保存信息</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="账户安全" name="security">
          <el-form :model="securityForm" label-width="120px" style="max-width: 600px;">
            <el-form-item label="当前密码">
              <el-input v-model="securityForm.currentPassword" type="password" show-password />
            </el-form-item>
            
            <el-form-item label="新密码">
              <el-input v-model="securityForm.newPassword" type="password" show-password />
            </el-form-item>
            
            <el-form-item label="确认新密码">
              <el-input v-model="securityForm.confirmNewPassword" type="password" show-password />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="changePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="偏好设置" name="preferences">
          <el-form :model="preferencesForm" label-width="120px" style="max-width: 600px;">
            <el-form-item label="主题">
              <el-select v-model="preferencesForm.theme">
                <el-option label="浅色主题" value="light" />
                <el-option label="深色主题" value="dark" />
                <el-option label="自动" value="auto" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="语言">
              <el-select v-model="preferencesForm.language">
                <el-option label="中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="时区">
              <el-select v-model="preferencesForm.timezone">
                <el-option label="中国标准时间 (UTC+8)" value="Asia/Shanghai" />
                <el-option label="美国东部时间 (UTC-5)" value="America/New_York" />
                <el-option label="欧洲中部时间 (UTC+1)" value="Europe/Berlin" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="savePreferences">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';

export default {
  name: 'Settings',
  setup() {
    const activeTab = ref('profile');
    
    const profileForm = reactive({
      username: 'admin',
      email: 'admin@example.com',
      phone: '13800138000'
    });
    
    const securityForm = reactive({
      currentPassword: '',
      newPassword: '',
      confirmNewPassword: ''
    });
    
    const preferencesForm = reactive({
      theme: 'light',
      language: 'zh-CN',
      timezone: 'Asia/Shanghai'
    });
    
    const updateProfile = () => {
      ElMessage.success('个人信息已更新');
    };
    
    const changePassword = () => {
      if (securityForm.newPassword !== securityForm.confirmNewPassword) {
        ElMessage.error('两次输入的新密码不一致');
        return;
      }
      
      if (securityForm.newPassword.length < 6) {
        ElMessage.error('新密码长度不能少于6位');
        return;
      }
      
      ElMessage.success('密码修改成功');
      // 清空密码字段
      securityForm.currentPassword = '';
      securityForm.newPassword = '';
      securityForm.confirmNewPassword = '';
    };
    
    const savePreferences = () => {
      ElMessage.success('偏好设置已保存');
    };
    
    return {
      activeTab,
      profileForm,
      securityForm,
      preferencesForm,
      updateProfile,
      changePassword,
      savePreferences
    };
  }
};
</script>

<style scoped>
.settings-container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 100px);
}

.settings-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.settings-tabs {
  margin-top: 20px;
}
</style>