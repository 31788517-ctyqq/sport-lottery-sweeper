<template>
  <div class="security-settings">
    <el-form 
      :model="form" 
      :rules="rules" 
      ref="securitySettingsFormRef"
      label-width="180px"
      class="settings-form"
    >
      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>密码安全策略</span>
          </div>
        </template>
        
        <el-form-item label="密码最小长度" prop="minPasswordLength">
          <el-input-number 
            v-model="form.minPasswordLength" 
            :min="6" 
            :max="30"
            controls-position="right"
          />
        </el-form-item>
        
        <el-form-item label="密码复杂度要求">
          <el-checkbox-group v-model="form.passwordComplexity">
            <el-checkbox value="require_uppercase">包含大写字母</el-checkbox>
            <el-checkbox value="require_lowercase">包含小写字母</el-checkbox>
            <el-checkbox value="require_numbers">包含数字</el-checkbox>
            <el-checkbox value="require_symbols">包含特殊符号</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="密码有效期(天)" prop="passwordExpiryDays">
          <el-input-number 
            v-model="form.passwordExpiryDays" 
            :min="1" 
            :max="365"
            controls-position="right"
          />
          <div class="setting-description">用户必须在此期限内更改密码</div>
        </el-form-item>
        
        <el-form-item label="最大登录尝试次数" prop="maxLoginAttempts">
          <el-input-number 
            v-model="form.maxLoginAttempts" 
            :min="1" 
            :max="10"
            controls-position="right"
          />
          <div class="setting-description">超过此次数后账户将被锁定</div>
        </el-form-item>
        
        <el-form-item label="账户锁定时间(分钟)" prop="accountLockoutDuration">
          <el-input-number 
            v-model="form.accountLockoutDuration" 
            :min="1" 
            :max="1440"
            controls-position="right"
          />
          <div class="setting-description">账户被锁定的时间</div>
        </el-form-item>
      </el-card>

      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>访问控制</span>
          </div>
        </template>
        
        <el-form-item label="启用双因素认证">
          <el-switch
            v-model="form.enable2FA"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
          <div class="setting-description">强制用户启用双因素认证</div>
        </el-form-item>
        
        <el-form-item label="允许IP白名单">
          <el-input 
            v-model="form.ipWhitelist" 
            type="textarea" 
            :rows="4"
            placeholder="每行一个IP地址，例如：192.168.1.100 或 192.168.1.0/24"
          />
          <div class="setting-description">只有来自这些IP地址的请求才被允许</div>
        </el-form-item>
        
        <el-form-item label="会话超时时间(分钟)" prop="sessionTimeout">
          <el-input-number 
            v-model="form.sessionTimeout" 
            :min="5" 
            :max="1440"
            controls-position="right"
          />
          <div class="setting-description">用户无操作后会话超时的时间</div>
        </el-form-item>
      </el-card>

      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>安全日志</span>
          </div>
        </template>
        
        <el-form-item label="记录登录日志">
          <el-switch
            v-model="form.logLoginActivities"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
        </el-form-item>
        
        <el-form-item label="记录敏感操作日志">
          <el-switch
            v-model="form.logSensitiveOperations"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
        </el-form-item>
        
        <el-form-item label="日志保留天数" prop="logRetentionDays">
          <el-input-number 
            v-model="form.logRetentionDays" 
            :min="1" 
            :max="365"
            controls-position="right"
          />
          <div class="setting-description">安全日志的保留时间</div>
        </el-form-item>
      </el-card>

      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>API安全</span>
          </div>
        </template>
        
        <el-form-item label="API速率限制(每分钟)" prop="apiRateLimit">
          <el-input-number 
            v-model="form.apiRateLimit" 
            :min="10" 
            :max="10000"
            controls-position="right"
          />
          <div class="setting-description">每个IP每分钟允许的API请求数量</div>
        </el-form-item>
        
        <el-form-item label="启用API密钥">
          <el-switch
            v-model="form.enableApiKey"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
        </el-form-item>
        
        <el-form-item 
          v-if="form.enableApiKey" 
          label="API密钥有效期(天)" 
          prop="apiKeyExpiryDays"
        >
          <el-input-number 
            v-model="form.apiKeyExpiryDays" 
            :min="1" 
            :max="365"
            controls-position="right"
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
  name: 'SecuritySettings',
  setup() {
    // 表单数据
    const form = ref({
      minPasswordLength: 8,
      passwordComplexity: ['require_uppercase', 'require_lowercase', 'require_numbers'],
      passwordExpiryDays: 90,
      maxLoginAttempts: 5,
      accountLockoutDuration: 30,
      enable2FA: false,
      ipWhitelist: '',
      sessionTimeout: 30,
      logLoginActivities: true,
      logSensitiveOperations: true,
      logRetentionDays: 90,
      apiRateLimit: 100,
      enableApiKey: true,
      apiKeyExpiryDays: 30
    })

    // 表单验证规则
    const rules = {
      minPasswordLength: [
        { required: true, message: '请输入密码最小长度', trigger: 'blur' }
      ],
      passwordExpiryDays: [
        { required: true, message: '请输入密码有效期', trigger: 'blur' }
      ],
      maxLoginAttempts: [
        { required: true, message: '请输入最大登录尝试次数', trigger: 'blur' }
      ],
      accountLockoutDuration: [
        { required: true, message: '请输入账户锁定时间', trigger: 'blur' }
      ],
      sessionTimeout: [
        { required: true, message: '请输入会话超时时间', trigger: 'blur' }
      ],
      logRetentionDays: [
        { required: true, message: '请输入日志保留天数', trigger: 'blur' }
      ],
      apiRateLimit: [
        { required: true, message: '请输入API速率限制', trigger: 'blur' }
      ],
      apiKeyExpiryDays: [
        { required: true, message: '请输入API密钥有效期', trigger: 'blur' }
      ]
    }

    // 方法
    const saveSettings = () => {
      // 这里应该是保存设置的逻辑
      ElMessage.success('安全设置保存成功')
    }

    const resetForm = () => {
      // 重置表单到初始值
      form.value = {
        minPasswordLength: 8,
        passwordComplexity: ['require_uppercase', 'require_lowercase', 'require_numbers'],
        passwordExpiryDays: 90,
        maxLoginAttempts: 5,
        accountLockoutDuration: 30,
        enable2FA: false,
        ipWhitelist: '',
        sessionTimeout: 30,
        logLoginActivities: true,
        logSensitiveOperations: true,
        logRetentionDays: 90,
        apiRateLimit: 100,
        enableApiKey: true,
        apiKeyExpiryDays: 30
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
.security-settings {
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