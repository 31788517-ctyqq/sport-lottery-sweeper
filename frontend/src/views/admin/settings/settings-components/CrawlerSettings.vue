<template>
  <div class="crawler-settings">
    <el-form 
      :model="form" 
      :rules="rules" 
      ref="crawlerSettingsFormRef"
      label-width="180px"
      class="settings-form"
    >
      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>爬虫基础配置</span>
          </div>
        </template>
        
        <el-form-item label="爬虫并发数" prop="concurrency">
          <el-slider 
            v-model="form.concurrency" 
            :min="1" 
            :max="50" 
            show-input
            input-size="small"
          />
          <div class="setting-description">同时运行的爬虫任务数量</div>
        </el-form-item>
        
        <el-form-item label="请求间隔(毫秒)" prop="requestInterval">
          <el-input-number 
            v-model="form.requestInterval" 
            :min="100" 
            :max="10000"
            controls-position="right"
          />
          <div class="setting-description">每次请求之间的最小间隔时间</div>
        </el-form-item>
        
        <el-form-item label="超时时间(秒)" prop="timeout">
          <el-input-number 
            v-model="form.timeout" 
            :min="5" 
            :max="60"
            controls-position="right"
          />
          <div class="setting-description">单次请求的超时时间</div>
        </el-form-item>
        
        <el-form-item label="重试次数" prop="retryTimes">
          <el-input-number 
            v-model="form.retryTimes" 
            :min="0" 
            :max="10"
            controls-position="right"
          />
          <div class="setting-description">请求失败后的重试次数</div>
        </el-form-item>
      </el-card>

      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>代理配置</span>
          </div>
        </template>
        
        <el-form-item label="启用代理">
          <el-switch
            v-model="form.useProxy"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
          <div class="setting-description">使用代理IP进行数据抓取</div>
        </el-form-item>
        
        <el-form-item 
          v-if="form.useProxy" 
          label="代理IP池更新频率(小时)" 
          prop="proxyUpdateFrequency"
        >
          <el-input-number 
            v-model="form.proxyUpdateFrequency" 
            :min="1" 
            :max="24"
            controls-position="right"
          />
        </el-form-item>
        
        <el-form-item 
          v-if="form.useProxy" 
          label="代理IP验证间隔(分钟)" 
          prop="proxyValidationInterval"
        >
          <el-input-number 
            v-model="form.proxyValidationInterval" 
            :min="1" 
            :max="60"
            controls-position="right"
          />
        </el-form-item>
      </el-card>

      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>浏览器配置</span>
          </div>
        </template>
        
        <el-form-item label="启用无头模式">
          <el-switch
            v-model="form.headless"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
          <div class="setting-description">是否以无头模式运行浏览器</div>
        </el-form-item>
        
        <el-form-item label="浏览器窗口大小">
          <el-input 
            v-model="form.browserWindowSize" 
            placeholder="例如: 1920x1080"
          />
          <div class="setting-description">浏览器窗口尺寸，格式: 宽x高</div>
        </el-form-item>
        
        <el-form-item label="用户代理(User Agent)">
          <el-input 
            v-model="form.userAgent" 
            type="textarea" 
            :rows="3"
            placeholder="留空使用默认UA"
          />
        </el-form-item>
      </el-card>

      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>数据处理配置</span>
          </div>
        </template>
        
        <el-form-item label="数据验证规则">
          <el-checkbox-group v-model="form.validationRules">
            <el-checkbox label="check_data_integrity">检查数据完整性</el-checkbox>
            <el-checkbox label="validate_format">验证数据格式</el-checkbox>
            <el-checkbox label="detect_anomalies">异常数据检测</el-checkbox>
            <el-checkbox label="duplicate_filter">重复数据过滤</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="数据存储路径">
          <el-input v-model="form.storagePath" placeholder="请输入数据存储路径" />
          <div class="setting-description">爬取数据的存储位置</div>
        </el-form-item>
        
        <el-form-item label="数据清理周期(天)" prop="cleanupInterval">
          <el-input-number 
            v-model="form.cleanupInterval" 
            :min="1" 
            :max="365"
            controls-position="right"
          />
          <div class="setting-description">自动清理过期数据的周期</div>
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
  name: 'CrawlerSettings',
  setup() {
    // 表单数据
    const form = ref({
      concurrency: 5,
      requestInterval: 1000,
      timeout: 15,
      retryTimes: 3,
      useProxy: false,
      proxyUpdateFrequency: 2,
      proxyValidationInterval: 10,
      headless: true,
      browserWindowSize: '1920x1080',
      userAgent: '',
      validationRules: ['check_data_integrity', 'validate_format'],
      storagePath: './data/crawled',
      cleanupInterval: 30
    })

    // 表单验证规则
    const rules = {
      concurrency: [
        { required: true, message: '请输入爬虫并发数', trigger: 'blur' }
      ],
      requestInterval: [
        { required: true, message: '请输入请求间隔', trigger: 'blur' }
      ],
      timeout: [
        { required: true, message: '请输入超时时间', trigger: 'blur' }
      ],
      retryTimes: [
        { required: true, message: '请输入重试次数', trigger: 'blur' }
      ],
      proxyUpdateFrequency: [
        { required: true, message: '请输入代理IP池更新频率', trigger: 'blur' }
      ],
      proxyValidationInterval: [
        { required: true, message: '请输入代理IP验证间隔', trigger: 'blur' }
      ],
      cleanupInterval: [
        { required: true, message: '请输入数据清理周期', trigger: 'blur' }
      ]
    }

    // 方法
    const saveSettings = () => {
      // 这里应该是保存设置的逻辑
      ElMessage.success('爬虫设置保存成功')
    }

    const resetForm = () => {
      // 重置表单到初始值
      form.value = {
        concurrency: 5,
        requestInterval: 1000,
        timeout: 15,
        retryTimes: 3,
        useProxy: false,
        proxyUpdateFrequency: 2,
        proxyValidationInterval: 10,
        headless: true,
        browserWindowSize: '1920x1080',
        userAgent: '',
        validationRules: ['check_data_integrity', 'validate_format'],
        storagePath: './data/crawled',
        cleanupInterval: 30
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
.crawler-settings {
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