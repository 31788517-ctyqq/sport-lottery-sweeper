<template>
  <div class="notification-settings">
    <el-form 
      :model="form" 
      :rules="rules" 
      ref="notificationSettingsFormRef"
      label-width="180px"
      class="settings-form"
    >
      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>邮件通知配置</span>
          </div>
        </template>
        
        <el-form-item label="SMTP服务器地址" prop="smtpHost">
          <el-input v-model="form.smtpHost" placeholder="例如: smtp.gmail.com" />
        </el-form-item>
        
        <el-form-item label="SMTP端口" prop="smtpPort">
          <el-input-number 
            v-model="form.smtpPort" 
            :min="1" 
            :max="65535"
            controls-position="right"
          />
        </el-form-item>
        
        <el-form-item label="启用SSL/TLS">
          <el-switch
            v-model="form.smtpSecure"
            inline-prompt
            active-text="SSL"
            inactive-text="TLS"
          />
        </el-form-item>
        
        <el-form-item label="发件人邮箱" prop="senderEmail">
          <el-input v-model="form.senderEmail" placeholder="请输入发件人邮箱地址" />
        </el-form-item>
        
        <el-form-item label="发件人名称" prop="senderName">
          <el-input v-model="form.senderName" placeholder="请输入发件人名称" />
        </el-form-item>
        
        <el-form-item label="邮箱用户名" prop="emailUsername">
          <el-input v-model="form.emailUsername" placeholder="请输入邮箱用户名" />
        </el-form-item>
        
        <el-form-item label="邮箱密码" prop="emailPassword">
          <el-input 
            v-model="form.emailPassword" 
            type="password" 
            show-password
            placeholder="请输入邮箱密码或授权码" 
          />
        </el-form-item>
      </el-card>

      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>通知类型配置</span>
          </div>
        </template>
        
        <el-form-item label="系统告警通知">
          <el-switch
            v-model="form.alertNotifications"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
          <div class="setting-description">当系统出现异常时发送通知</div>
        </el-form-item>
        
        <el-form-item label="数据更新通知">
          <el-switch
            v-model="form.dataUpdateNotifications"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
          <div class="setting-description">当数据更新时发送通知</div>
        </el-form-item>
        
        <el-form-item label="爬虫任务通知">
          <el-switch
            v-model="form.crawlerNotifications"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
          <div class="setting-description">爬虫任务开始/结束时发送通知</div>
        </el-form-item>
        
        <el-form-item label="安全事件通知">
          <el-switch
            v-model="form.securityNotifications"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
          <div class="setting-description">发生安全事件时发送通知</div>
        </el-form-item>
      </el-card>

      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>接收者配置</span>
          </div>
        </template>
        
        <el-form-item label="系统管理员邮箱">
          <el-input 
            v-model="form.adminEmails" 
            type="textarea" 
            :rows="3"
            placeholder="每行一个邮箱地址，用于接收系统通知" 
          />
        </el-form-item>
        
        <el-form-item label="运维团队邮箱">
          <el-input 
            v-model="form.opsEmails" 
            type="textarea" 
            :rows="3"
            placeholder="每行一个邮箱地址，用于接收运维相关通知" 
          />
        </el-form-item>
      </el-card>

      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>短信通知配置</span>
          </div>
        </template>
        
        <el-form-item label="启用短信通知">
          <el-switch
            v-model="form.smsEnabled"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
          <div class="setting-description">是否启用短信通知功能</div>
        </el-form-item>
        
        <el-form-item 
          v-if="form.smsEnabled" 
          label="短信服务商" 
          prop="smsProvider"
        >
          <el-select v-model="form.smsProvider" placeholder="请选择短信服务商">
            <el-option label="阿里云" value="aliyun" />
            <el-option label="腾讯云" value="tencent" />
            <el-option label="华为云" value="huawei" />
          </el-select>
        </el-form-item>
        
        <el-form-item 
          v-if="form.smsEnabled" 
          label="API密钥" 
          prop="smsApiKey"
        >
          <el-input 
            v-model="form.smsApiKey" 
            type="password" 
            show-password
            placeholder="请输入短信服务API密钥" 
          />
        </el-form-item>
        
        <el-form-item 
          v-if="form.smsEnabled" 
          label="API密钥Secret" 
          prop="smsApiSecret"
        >
          <el-input 
            v-model="form.smsApiSecret" 
            type="password" 
            show-password
            placeholder="请输入短信服务API密钥Secret" 
          />
        </el-form-item>
      </el-card>

      <div class="form-actions">
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
        <el-button @click="resetForm">重置</el-button>
      </div>
    </el-form>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'NotificationSettings',
  setup() {
    // 表单数据
    const form = ref({
      smtpHost: 'smtp.gmail.com',
      smtpPort: 587,
      smtpSecure: false, // false for TLS, true for SSL
      senderEmail: 'noreply@yoursystem.com',
      senderName: '竞彩足球扫盘系统',
      emailUsername: '',
      emailPassword: '',
      alertNotifications: true,
      dataUpdateNotifications: true,
      crawlerNotifications: true,
      securityNotifications: true,
      adminEmails: 'admin@yoursystem.com',
      opsEmails: 'ops@yoursystem.com',
      smsEnabled: false,
      smsProvider: 'aliyun',
      smsApiKey: '',
      smsApiSecret: ''
    })

    // 表单验证规则
    const rules = {
      smtpHost: [
        { required: true, message: '请输入SMTP服务器地址', trigger: 'blur' }
      ],
      smtpPort: [
        { required: true, message: '请输入SMTP端口', trigger: 'blur' }
      ],
      senderEmail: [
        { required: true, message: '请输入发件人邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
      ],
      senderName: [
        { required: true, message: '请输入发件人名称', trigger: 'blur' }
      ],
      emailUsername: [
        { required: true, message: '请输入邮箱用户名', trigger: 'blur' }
      ],
      emailPassword: [
        { required: true, message: '请输入邮箱密码', trigger: 'blur' }
      ],
      smsProvider: [
        { required: true, message: '请选择短信服务商', trigger: 'change' }
      ],
      smsApiKey: [
        { required: true, message: '请输入短信服务API密钥', trigger: 'blur' }
      ],
      smsApiSecret: [
        { required: true, message: '请输入短信服务API密钥Secret', trigger: 'blur' }
      ]
    }

    // 方法
    const saveSettings = () => {
      // 这里应该是保存设置的逻辑
      ElMessage.success('通知设置保存成功')
    }

    const resetForm = () => {
      // 重置表单到初始值
      form.value = {
        smtpHost: 'smtp.gmail.com',
        smtpPort: 587,
        smtpSecure: false,
        senderEmail: 'noreply@yoursystem.com',
        senderName: '竞彩足球扫盘系统',
        emailUsername: '',
        emailPassword: '',
        alertNotifications: true,
        dataUpdateNotifications: true,
        crawlerNotifications: true,
        securityNotifications: true,
        adminEmails: 'admin@yoursystem.com',
        opsEmails: 'ops@yoursystem.com',
        smsEnabled: false,
        smsProvider: 'aliyun',
        smsApiKey: '',
        smsApiSecret: ''
      }
    }

    return {
      form,
      rules,
      saveSettings,
      resetForm
    }
  }
}
</script>

<style scoped>
.notification-settings {
  padding: 20px 0;
}

.settings-form {
  max-width: 900px;
}

.setting-group {
  margin-bottom: 20px;
}

.group-header {
  font-weight: bold;
  font-size: 16px;
}

.setting-description {
  color: #909399;
  font-size: 13px;
  margin-top: 5px;
}

.form-actions {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  text-align: center;
}
</style>