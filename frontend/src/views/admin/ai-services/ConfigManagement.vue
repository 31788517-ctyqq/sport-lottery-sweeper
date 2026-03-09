<template>
  <div class="config-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>⚙️ 配置管理</h3>
            <p class="subtitle">AI服务配置管理（优先级设置、故障转移、健康检查等）</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="saveConfig">保存配置</el-button>
            <el-button @click="resetConfig">重置为默认</el-button>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="config-tabs">
        <el-tab-pane label="基础配置" name="basic">
          <el-form :model="config.basic" label-width="180px" style="max-width: 800px; margin-top: 20px;">
            <el-form-item label="服务优先级策略">
              <el-select v-model="config.basic.priority" placeholder="选择优先级策略" style="width: 100%;">
                <el-option label="优先使用本地服务" value="local_first" />
                <el-option label="优先使用远程服务" value="remote_first" />
                <el-option label="平衡使用（根据响应时间）" value="balanced" />
              </el-select>
              <div class="form-help">
                控制AI请求的路由策略，决定优先使用本地还是远程服务
              </div>
            </el-form-item>
            
            <el-form-item label="故障转移">
              <el-switch 
                v-model="config.basic.fallbackEnabled" 
                active-text="启用"
                inactive-text="禁用"
              />
              <div class="form-help">
                当首选服务不可用时，是否自动切换到备用服务
              </div>
            </el-form-item>
            
            <el-form-item label="最大并发数">
              <el-input-number 
                v-model="config.basic.maxConcurrency" 
                :min="1" 
                :max="100" 
                style="width: 200px;"
              />
              <div class="form-help">
                同时处理的最大AI请求并发数
              </div>
            </el-form-item>
            
            <el-form-item label="请求超时时间（秒）">
              <el-input-number 
                v-model="config.basic.timeout" 
                :min="5" 
                :max="120" 
                style="width: 200px;"
              />
              <div class="form-help">
                AI服务请求的超时时间设置
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="健康检查" name="health">
          <el-form :model="config.health" label-width="180px" style="max-width: 800px; margin-top: 20px;">
            <el-form-item label="健康检查间隔（秒）">
              <el-input-number 
                v-model="config.health.checkInterval" 
                :min="10" 
                :max="3600" 
                style="width: 200px;"
              />
              <div class="form-help">
                定期检查AI服务健康状态的时间间隔
              </div>
            </el-form-item>
            
            <el-form-item label="连续错误阈值">
              <el-input-number 
                v-model="config.health.errorThreshold" 
                :min="1" 
                :max="20" 
                style="width: 200px;"
              />
              <div class="form-help">
                服务被标记为不健康所需的连续错误次数
              </div>
            </el-form-item>
            
            <el-form-item label="服务恢复时间（分钟）">
              <el-input-number 
                v-model="config.health.recoveryTime" 
                :min="1" 
                :max="1440" 
                style="width: 200px;"
              />
              <div class="form-help">
                服务在被标记为不健康后，需要等待多久才重新尝试
              </div>
            </el-form-item>
            
            <el-form-item label="健康检查方法">
              <el-radio-group v-model="config.health.checkMethod">
                <el-radio value="ping">Ping测试</el-radio>
                <el-radio value="full">完整请求测试</el-radio>
              </el-radio-group>
              <div class="form-help">
                选择健康检查的方式：简单ping或完整API请求
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="成本控制" name="cost">
          <el-form :model="config.cost" label-width="180px" style="max-width: 800px; margin-top: 20px;">
            <el-form-item label="月度成本预算（元）">
              <el-input-number 
                v-model="config.cost.monthlyBudget" 
                :min="0" 
                :max="100000" 
                :precision="2"
                style="width: 200px;"
              />
              <div class="form-help">
                设置月度AI服务使用成本预算上限
              </div>
            </el-form-item>
            
            <el-form-item label="预算警告阈值（%）">
              <el-slider 
                v-model="config.cost.budgetWarningThreshold" 
                :min="0" 
                :max="100" 
                style="width: 200px;"
              />
              <div class="form-help">
                达到预算百分之多少时发出警告
              </div>
            </el-form-item>
            
            <el-form-item label="请求速率限制（每分钟）">
              <el-input-number 
                v-model="config.cost.rateLimit" 
                :min="1" 
                :max="10000" 
                style="width: 200px;"
              />
              <div class="form-help">
                每分钟最大请求数，超过则排队或拒绝
              </div>
            </el-form-item>
            
            <el-form-item label="昂贵请求警告阈值（元）">
              <el-input-number 
                v-model="config.cost.expensiveRequestThreshold" 
                :min="0" 
                :max="100" 
                :precision="2"
                style="width: 200px;"
              />
              <div class="form-help">
                单次请求费用超过此值时发出警告
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="高级配置" name="advanced">
          <el-form :model="config.advanced" label-width="180px" style="max-width: 800px; margin-top: 20px;">
            <el-form-item label="缓存启用">
              <el-switch 
                v-model="config.advanced.cacheEnabled" 
                active-text="启用"
                inactive-text="禁用"
              />
              <div class="form-help">
                是否启用AI响应缓存以减少重复请求和成本
              </div>
            </el-form-item>
            
            <el-form-item label="缓存过期时间（小时）">
              <el-input-number 
                v-model="config.advanced.cacheExpiry" 
                :min="1" 
                :max="168" 
                style="width: 200px;"
              />
              <div class="form-help">
                缓存的AI响应在多长时间后过期
              </div>
            </el-form-item>
            
            <el-form-item label="负载均衡策略">
              <el-select v-model="config.advanced.loadBalanceStrategy" placeholder="选择负载均衡策略" style="width: 100%;">
                <el-option label="轮询" value="round_robin" />
                <el-option label="最少连接" value="least_connections" />
                <el-option label="响应时间加权" value="response_time_weighted" />
              </el-select>
              <div class="form-help">
                多个AI服务实例之间的负载分配策略
              </div>
            </el-form-item>
            
            <el-form-item label="日志级别">
              <el-select v-model="config.advanced.logLevel" placeholder="选择日志级别" style="width: 100%;">
                <el-option label="错误" value="error" />
                <el-option label="警告" value="warn" />
                <el-option label="信息" value="info" />
                <el-option label="调试" value="debug" />
              </el-select>
              <div class="form-help">
                AI服务的日志记录详细程度
              </div>
            </el-form-item>
            
            <el-form-item label="调试模式">
              <el-switch 
                v-model="config.advanced.debugMode" 
                active-text="启用"
                inactive-text="禁用"
              />
              <div class="form-help">
                启用详细调试信息，仅用于开发环境
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 响应式数据
const activeTab = ref('basic')

// 配置数据
const config = reactive({
  basic: {
    priority: 'local_first',
    fallbackEnabled: true,
    maxConcurrency: 10,
    timeout: 30
  },
  health: {
    checkInterval: 30,
    errorThreshold: 3,
    recoveryTime: 5,
    checkMethod: 'full'
  },
  cost: {
    monthlyBudget: 500.00,
    budgetWarningThreshold: 80,
    rateLimit: 1000,
    expensiveRequestThreshold: 5.00
  },
  advanced: {
    cacheEnabled: true,
    cacheExpiry: 24,
    loadBalanceStrategy: 'response_time_weighted',
    logLevel: 'info',
    debugMode: false
  }
})

// 方法
const saveConfig = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要保存这些配置吗？某些更改可能需要重启服务才能生效。',
      '确认保存',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里应该调用API保存配置
    console.log('保存配置:', config)
    ElMessage.success('配置保存成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('保存配置失败')
    }
  }
}

const resetConfig = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置为默认配置吗？这将丢失所有自定义设置。',
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 重置为默认配置
    Object.assign(config, {
      basic: {
        priority: 'local_first',
        fallbackEnabled: true,
        maxConcurrency: 10,
        timeout: 30
      },
      health: {
        checkInterval: 30,
        errorThreshold: 3,
        recoveryTime: 5,
        checkMethod: 'full'
      },
      cost: {
        monthlyBudget: 500.00,
        budgetWarningThreshold: 80,
        rateLimit: 1000,
        expensiveRequestThreshold: 5.00
      },
      advanced: {
        cacheEnabled: true,
        cacheExpiry: 24,
        loadBalanceStrategy: 'response_time_weighted',
        logLevel: 'info',
        debugMode: false
      }
    })
    
    ElMessage.success('配置已重置为默认值')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重置配置失败')
    }
  }
}

// 初始化数据
onMounted(() => {
  // 从API加载当前配置
  // loadCurrentConfig()
})
</script>

<style scoped>
.card-container {
  margin: 20px;
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

.config-tabs {
  margin-top: 20px;
}

.form-help {
  color: #909399;
  font-size: 13px;
  margin-top: 5px;
}
</style>