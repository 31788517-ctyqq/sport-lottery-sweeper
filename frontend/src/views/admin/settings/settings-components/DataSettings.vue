<template>
  <div class="data-settings">
    <el-form 
      :model="form" 
      :rules="rules" 
      ref="dataSettingsFormRef"
      label-width="160px"
      class="settings-form"
    >
      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>数据源配置</span>
          </div>
        </template>
        
        <el-form-item label="数据源类型" prop="dataSourceType">
          <el-radio-group v-model="form.dataSourceType">
            <el-radio value="primary">主数据源</el-radio>
            <el-radio value="backup">备用数据源</el-radio>
            <el-radio value="combined">组合数据源</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="数据同步频率(分钟)" prop="syncInterval">
          <el-input-number 
            v-model="form.syncInterval" 
            :min="1" 
            :max="1440"
            controls-position="right"
          />
          <div class="setting-description">数据同步的频率，影响数据更新的及时性</div>
        </el-form-item>
        
        <el-form-item label="最大连接数" prop="maxConnections">
          <el-input-number 
            v-model="form.maxConnections" 
            :min="1" 
            :max="100"
            controls-position="right"
          />
          <div class="setting-description">数据库的最大连接数</div>
        </el-form-item>
        
        <el-form-item label="连接超时时间(秒)" prop="connectionTimeout">
          <el-input-number 
            v-model="form.connectionTimeout" 
            :min="1" 
            :max="300"
            controls-position="right"
          />
          <div class="setting-description">数据库连接超时时间</div>
        </el-form-item>
      </el-card>

      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>数据处理配置</span>
          </div>
        </template>
        
        <el-form-item label="数据清洗规则">
          <el-checkbox-group v-model="form.cleaningRules">
            <el-checkbox value="remove_duplicates">去重</el-checkbox>
            <el-checkbox value="validate_format">格式验证</el-checkbox>
            <el-checkbox value="fill_missing">缺失值填充</el-checkbox>
            <el-checkbox value="outlier_detection">异常值检测</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="数据压缩">
          <el-switch
            v-model="form.dataCompression"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
          <div class="setting-description">对历史数据进行压缩存储</div>
        </el-form-item>
        
        <el-form-item label="数据备份策略" prop="backupStrategy">
          <el-radio-group v-model="form.backupStrategy">
            <el-radio value="daily">每日备份</el-radio>
            <el-radio value="weekly">每周备份</el-radio>
            <el-radio value="monthly">每月备份</el-radio>
          </el-radio-group>
          <div class="setting-description">数据备份的频率策略</div>
        </el-form-item>
        
        <el-form-item label="备份保留天数" prop="backupRetentionDays">
          <el-input-number 
            v-model="form.backupRetentionDays" 
            :min="1" 
            :max="365"
            controls-position="right"
          />
          <div class="setting-description">备份文件的保留天数</div>
        </el-form-item>
      </el-card>

      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>缓存配置</span>
          </div>
        </template>
        
        <el-form-item label="启用内存缓存">
          <el-switch
            v-model="form.enableCache"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
          <div class="setting-description">启用内存缓存以提高数据访问速度</div>
        </el-form-item>
        
        <el-form-item 
          v-if="form.enableCache" 
          label="缓存过期时间(分钟)" 
          prop="cacheExpiration"
        >
          <el-input-number 
            v-model="form.cacheExpiration" 
            :min="1" 
            :max="1440"
            controls-position="right"
          />
          <div class="setting-description">缓存数据的过期时间</div>
        </el-form-item>
        
        <el-form-item 
          v-if="form.enableCache" 
          label="缓存大小限制(MB)" 
          prop="cacheSizeLimit"
        >
          <el-input-number 
            v-model="form.cacheSizeLimit" 
            :min="1" 
            :max="10240"
            controls-position="right"
          />
          <div class="setting-description">内存缓存的最大容量</div>
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
  name: 'DataSettings',
  setup() {
    // 表单数据
    const form = ref({
      dataSourceType: 'primary',
      syncInterval: 30,
      maxConnections: 10,
      connectionTimeout: 30,
      cleaningRules: ['remove_duplicates', 'validate_format'],
      dataCompression: true,
      backupStrategy: 'daily',
      backupRetentionDays: 30,
      enableCache: true,
      cacheExpiration: 60,
      cacheSizeLimit: 1024
    })

    // 表单验证规则
    const rules = {
      dataSourceType: [
        { required: true, message: '请选择数据源类型', trigger: 'change' }
      ],
      syncInterval: [
        { required: true, message: '请输入数据同步频率', trigger: 'blur' }
      ],
      maxConnections: [
        { required: true, message: '请输入最大连接数', trigger: 'blur' }
      ],
      connectionTimeout: [
        { required: true, message: '请输入连接超时时间', trigger: 'blur' }
      ],
      backupStrategy: [
        { required: true, message: '请选择备份策略', trigger: 'change' }
      ],
      backupRetentionDays: [
        { required: true, message: '请输入备份保留天数', trigger: 'blur' }
      ],
      cacheExpiration: [
        { required: true, message: '请输入缓存过期时间', trigger: 'blur' }
      ],
      cacheSizeLimit: [
        { required: true, message: '请输入缓存大小限制', trigger: 'blur' }
      ]
    }

    // 方法
    const saveSettings = () => {
      // 这里应该是保存设置的逻辑
      ElMessage.success('数据设置保存成功')
    }

    const resetForm = () => {
      // 重置表单到初始值
      form.value = {
        dataSourceType: 'primary',
        syncInterval: 30,
        maxConnections: 10,
        connectionTimeout: 30,
        cleaningRules: ['remove_duplicates', 'validate_format'],
        dataCompression: true,
        backupStrategy: 'daily',
        backupRetentionDays: 30,
        enableCache: true,
        cacheExpiration: 60,
        cacheSizeLimit: 1024
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
.data-settings {
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