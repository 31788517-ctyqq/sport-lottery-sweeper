<template>
  <div class="system-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>⚙️ 系统管理</h3>
            <p class="subtitle">系统配置、监控和维护</p>
          </div>
        </div>
      </template>

      <!-- 系统概览 -->
      <el-row :gutter="20" class="overview-stats">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-blue">
                <i class="el-icon-monitor" />
              </div>
              <div class="stat-info">
                <div class="stat-label">服务器状态</div>
                <div class="stat-value">正常</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-green">
                <i class="el-icon-timer" />
              </div>
              <div class="stat-info">
                <div class="stat-label">运行时间</div>
                <div class="stat-value">{{ uptime }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-orange">
                <i class="el-icon-data-analysis" />
              </div>
              <div class="stat-info">
                <div class="stat-label">CPU使用率</div>
                <div class="stat-value">{{ cpuUsage }}%</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-purple">
                <i class="el-icon-files" />
              </div>
              <div class="stat-info">
                <div class="stat-label">内存使用率</div>
                <div class="stat-value">{{ memoryUsage }}%</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 系统配置选项卡 -->
      <el-tabs v-model="activeTab" class="system-tabs" type="border-card">
        <el-tab-pane label="系统配置" name="config">
          <el-form :model="configForm" label-width="150px" style="max-width: 800px; margin-top: 20px;">
            <el-form-item label="系统名称">
              <el-input v-model="configForm.systemName" placeholder="输入系统名称" />
            </el-form-item>
            
            <el-form-item label="最大并发数">
              <el-input-number v-model="configForm.maxConcurrency" :min="1" :max="100" />
            </el-form-item>
            
            <el-form-item label="数据保留天数">
              <el-input-number v-model="configForm.dataRetentionDays" :min="1" :max="365" />
            </el-form-item>
            
            <el-form-item label="API请求频率限制">
              <el-input-number v-model="configForm.apiRateLimit" :min="1" :max="10000" />
            </el-form-item>
            
            <el-form-item label="日志级别">
              <el-select v-model="configForm.logLevel" placeholder="选择日志级别">
                <el-option label="DEBUG" value="debug" />
                <el-option label="INFO" value="info" />
                <el-option label="WARNING" value="warning" />
                <el-option label="ERROR" value="error" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveConfig">保存配置</el-button>
              <el-button @click="resetConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="系统监控" name="monitoring">
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="12">
              <el-card header="CPU使用率">
                <div ref="cpuChart" class="chart-container" style="height: 300px;"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card header="内存使用率">
                <div ref="memoryChart" class="chart-container" style="height: 300px;"></div>
              </el-card>
            </el-col>
          </el-row>
          
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="12">
              <el-card header="API请求统计">
                <div ref="apiChart" class="chart-container" style="height: 300px;"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card header="数据库连接">
                <div ref="dbChart" class="chart-container" style="height: 300px;"></div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="系统日志" name="logs">
          <div style="margin-top: 20px;">
            <el-row :gutter="20" style="margin-bottom: 20px;">
              <el-col :span="6">
                <el-select v-model="logLevelFilter" placeholder="日志级别" style="width: 100%;">
                  <el-option label="ALL" value="" />
                  <el-option label="DEBUG" value="debug" />
                  <el-option label="INFO" value="info" />
                  <el-option label="WARNING" value="warning" />
                  <el-option label="ERROR" value="error" />
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-date-picker
                  v-model="logDateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  style="width: 100%;"
                />
              </el-col>
              <el-col :span="6">
                <el-button type="primary" @click="fetchLogs">查询日志</el-button>
              </el-col>
            </el-row>

            <el-table :data="logEntries" style="width: 100%" stripe height="400">
              <el-table-column prop="timestamp" label="时间" width="180" />
              <el-table-column prop="level" label="级别" width="100">
                <template #default="scope">
                  <el-tag :type="getLogLevelType(scope.row.level)">
                    {{ scope.row.level.toUpperCase() }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="消息" show-overflow-tooltip />
              <el-table-column prop="module" label="模块" width="150" />
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane label="维护工具" name="maintenance">
          <div style="margin-top: 20px;">
            <el-card header="系统维护工具">
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="maintenance-tool">
                    <h4>清理缓存</h4>
                    <p>清除系统缓存数据，释放内存空间</p>
                    <el-button type="warning" @click="clearCache">执行</el-button>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="maintenance-tool">
                    <h4>备份数据</h4>
                    <p>创建系统数据的完整备份</p>
                    <el-button type="primary" @click="backupData">执行</el-button>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="maintenance-tool">
                    <h4>清理日志</h4>
                    <p>删除过期的日志文件</p>
                    <el-button type="danger" @click="cleanupLogs">执行</el-button>
                  </div>
                </el-col>
              </el-row>
              
              <el-divider />
              
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="maintenance-tool">
                    <h4>重启服务</h4>
                    <p>重启系统服务（谨慎操作）</p>
                    <el-button type="danger" @click="restartService">执行</el-button>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="maintenance-tool">
                    <h4>更新配置</h4>
                    <p>重新加载系统配置文件</p>
                    <el-button type="info" @click="reloadConfig">执行</el-button>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="maintenance-tool">
                    <h4>健康检查</h4>
                    <p>执行系统健康状态检查</p>
                    <el-button type="success" @click="performHealthCheck">执行</el-button>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// 响应式数据
const activeTab = ref('config')
const uptime = ref('7天 12小时 34分钟')
const cpuUsage = ref(45)
const memoryUsage = ref(62)

// 配置表单
const configForm = ref({
  systemName: '体育彩票AI分析系统',
  maxConcurrency: 50,
  dataRetentionDays: 90,
  apiRateLimit: 1000,
  logLevel: 'info'
})

// 日志相关
const logLevelFilter = ref('')
const logDateRange = ref([])
const logEntries = ref([
  { id: 1, timestamp: '2023-05-01 10:30:15', level: 'info', message: '系统启动成功', module: 'core' },
  { id: 2, timestamp: '2023-05-01 10:31:22', level: 'warning', message: '数据库连接池接近上限', module: 'database' },
  { id: 3, timestamp: '2023-05-01 10:35:08', level: 'error', message: 'API请求超时', module: 'api' },
  { id: 4, timestamp: '2023-05-01 10:40:12', level: 'info', message: '数据同步完成', module: 'sync' },
  { id: 5, timestamp: '2023-05-01 10:45:33', level: 'debug', message: '调试信息输出', module: 'debug' },
])

// 图表引用
const cpuChart = ref(null)
const memoryChart = ref(null)
const apiChart = ref(null)
const dbChart = ref(null)

// 方法
const saveConfig = () => {
  ElMessage.success('系统配置保存成功')
  console.log('保存配置:', configForm.value)
}

const resetConfig = () => {
  configForm.value = {
    systemName: '体育彩票AI分析系统',
    maxConcurrency: 50,
    dataRetentionDays: 90,
    apiRateLimit: 1000,
    logLevel: 'info'
  }
  ElMessage.info('配置已重置为默认值')
}

const fetchLogs = () => {
  ElMessage.info('查询日志功能将在正式版本中实现')
}

const getLogLevelType = (level) => {
  switch (level.toLowerCase()) {
    case 'debug': return 'info'
    case 'info': return 'primary'
    case 'warning': return 'warning'
    case 'error': return 'danger'
    default: return 'info'
  }
}

// 维护工具方法
const clearCache = () => {
  ElMessage.warning('清理缓存功能将在正式版本中实现')
}

const backupData = () => {
  ElMessage.info('数据备份功能将在正式版本中实现')
}

const cleanupLogs = () => {
  ElMessage.warning('清理日志功能将在正式版本中实现')
}

const restartService = () => {
  ElMessageBox.confirm(
    '确定要重启系统服务吗？这将暂时中断所有服务！',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('服务重启指令已发送')
  }).catch(() => {
    ElMessage.info('操作已取消')
  })
}

const reloadConfig = () => {
  ElMessage.success('配置重载成功')
}

const performHealthCheck = () => {
  ElMessage.success('健康检查正在执行...')
}

// 初始化图表
const initCharts = async () => {
  await nextTick()
  
  // CPU使用率图表
  if (cpuChart.value) {
    const chart = echarts.init(cpuChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'] },
      yAxis: { type: 'value', name: '%' },
      series: [{ data: [20, 35, 40, 60, 55, 45, 30], type: 'line', smooth: true }]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // 内存使用率图表
  if (memoryChart.value) {
    const chart = echarts.init(memoryChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'] },
      yAxis: { type: 'value', name: '%' },
      series: [{ data: [45, 50, 65, 70, 68, 55, 50], type: 'line', smooth: true, itemStyle: { color: '#e74c3c' } }]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // API请求统计图表
  if (apiChart.value) {
    const chart = echarts.init(apiChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['请求次数', '错误次数'] },
      xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
      yAxis: { type: 'value' },
      series: [
        { name: '请求次数', type: 'bar', data: [1200, 1320, 1010, 1340, 900, 2300, 2100] },
        { name: '错误次数', type: 'bar', data: [10, 15, 8, 12, 5, 20, 18] }
      ]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // 数据库连接图表
  if (dbChart.value) {
    const chart = echarts.init(dbChart.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', left: 'left' },
      series: [
        {
          name: '连接状态',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 45, name: '活跃连接' },
            { value: 5, name: '等待连接' },
            { value: 2, name: '错误连接' },
            { value: 8, name: '空闲连接' }
          ],
          emphasis: {
            itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
          }
        }
      ]
    })
    window.addEventListener('resize', () => chart.resize())
  }
}

onMounted(() => {
  initCharts()
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

.overview-stats {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content {
  display: flex;
  align-items: center;
  width: 100%;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 15px;
}

.bg-blue { background: #409eff; }
.bg-green { background: #67c23a; }
.bg-orange { background: #e6a23c; }
.bg-purple { background: #9013fe; }

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.system-tabs {
  margin-top: 20px;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.maintenance-tool {
  padding: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  text-align: center;
}

.maintenance-tool h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
}

.maintenance-tool p {
  color: #909399;
  font-size: 14px;
  margin: 0 0 15px 0;
}
</style>
```