

爬虫管理模下的   爬虫系统监控页面按照以下布局设计帮我生成页面：

1、在系统架构参考其布局和代码
2、页面布局在数据源管理页面，对应在整个页面的在右边页面区域；
3、功能和布局设计以代码里面的为主；
4、在不和项目系统发生冲突的基础上计量去设计。
5、这个页面包含以下部分：监控指标设计、监控前端界面

以下是包含部分的页面代码布局参考：


1监控指标设计：
1.1监控数据模型
# models/monitor.py
class MonitorMetric(Base):
    __tablename__ = "monitor_metrics"
    
    id = Column(UUID, primary_key=True)
    metric_name = Column(String(100), nullable=False)      # 指标名称
    metric_type = Column(String(50), nullable=False)       # 指标类型
    
    # 维度信息
    source_id = Column(UUID, ForeignKey('data_sources.id'))
    task_id = Column(UUID, ForeignKey('crawl_tasks.id'))
    league = Column(String(50))                            # 联赛维度
    
    # 指标值
    value = Column(Float, nullable=False)                  # 指标值
    unit = Column(String(20))                              # 单位
    
    # 时间信息
    timestamp = Column(DateTime, nullable=False, index=True)
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    # 标签（用于筛选）
    tags = Column(JSON, default=dict)

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(UUID, primary_key=True)
    name = Column(String(100), nullable=False)             # 规则名称
    
    # 规则条件
    metric_name = Column(String(100), nullable=False)      # 监控指标
    condition_type = Column(String(20), nullable=False)    # 条件类型
    threshold = Column(Float, nullable=False)              # 阈值
    
    # 持续时间
    duration = Column(Integer, default=0)                  # 持续秒数
    
    # 告警配置
    severity = Column(String(20), default="warning")       # 严重程度
    notification_channels = Column(JSON, default=list)     # 通知渠道
    enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AlertHistory(Base):
    __tablename__ = "alert_history"
    
    id = Column(UUID, primary_key=True)
    rule_id = Column(UUID, ForeignKey('alert_rules.id'))
    metric_name = Column(String(100))
    
    # 告警详情
    triggered_value = Column(Float)                        # 触发时的值
    threshold = Column(Float)                              # 阈值
    message = Column(Text)                                 # 告警消息
    
    # 状态
    status = Column(String(20), default="active")          # active, resolved, acknowledged
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    1.2监控指标定义：

# services/monitoring/metrics.py
class SystemMetrics:
    """系统监控指标定义"""
    
    # 采集相关指标
    CRAWL_METRICS = [
        {
            "name": "crawl_request_total",
            "description": "总采集请求数",
            "type": "counter",
            "labels": ["source_id", "task_id", "league", "status"]
        },
        {
            "name": "crawl_request_duration_seconds",
            "description": "采集请求耗时",
            "type": "histogram",
            "labels": ["source_id", "task_id", "league"]
        },
        {
            "name": "crawl_success_rate",
            "description": "采集成功率",
            "type": "gauge",
            "labels": ["source_id", "task_id", "league"]
        },
        {
            "name": "crawl_data_items_total",
            "description": "采集数据条目数",
            "type": "counter",
            "labels": ["source_id", "task_id", "league", "data_type"]
        }
    ]
    
    # 数据质量指标
    DATA_QUALITY_METRICS = [
        {
            "name": "data_completeness",
            "description": "数据完整度",
            "type": "gauge",
            "labels": ["league", "match_id", "field"]
        },
        {
            "name": "data_accuracy",
            "description": "数据准确度",
            "type": "gauge",
            "labels": ["league", "match_id", "field"]
        },
        {
            "name": "data_freshness",
            "description": "数据新鲜度（最后更新时间）",
            "type": "gauge",
            "labels": ["league", "match_id"]
        }
    ]
    
    # 系统资源指标
    SYSTEM_METRICS = [
        {
            "name": "system_cpu_usage",
            "description": "CPU使用率",
            "type": "gauge",
            "labels": ["host", "core"]
        },
        {
            "name": "system_memory_usage",
            "description": "内存使用率",
            "type": "gauge",
            "labels": ["host"]
        },
        {
            "name": "system_disk_usage",
            "description": "磁盘使用率",
            "type": "gauge",
            "labels": ["host", "mount"]
        },
        {
            "name": "database_connections",
            "description": "数据库连接数",
            "type": "gauge",
            "labels": ["database"]
        }
    ]

2、前端监控界面

<!-- components/SystemMonitor.vue -->
<template>
  <div class="system-monitor">
    <!-- 全局健康状态 -->
    <div class="health-status">
      <el-row :gutter="20">
        <el-col :span="6" v-for="status in healthStatuses" :key="status.name">
          <el-card shadow="hover">
            <template #header>
              <div class="status-header">
                <span>{{ status.name }}</span>
                <el-tag :type="status.type" size="small">
                  {{ status.value }}
                </el-tag>
              </div>
            </template>
            <div class="status-body">
              <el-progress 
                :percentage="status.percentage" 
                :status="status.progressStatus"
                :stroke-width="10"
              />
              <div class="status-detail">
                <span>{{ status.detail }}</span>
                <el-icon v-if="status.trend === 'up'" color="#67c23a">
                  <Top />
                </el-icon>
                <el-icon v-else-if="status.trend === 'down'" color="#f56c6c">
                  <Bottom />
                </el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 实时监控图表 -->
    <div class="monitor-charts">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>采集成功率趋势</span>
              <el-select v-model="successRateRange" size="small" style="width: 120px;">
                <el-option label="24小时" value="24h" />
                <el-option label="7天" value="7d" />
                <el-option label="30天" value="30d" />
              </el-select>
            </template>
            <div style="height: 300px;">
              <LineChart 
                :data="successRateData" 
                :x-axis="successRateXAxis"
                :series="successRateSeries"
              />
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>数据采集量分布</span>
            </template>
            <div style="height: 300px;">
              <PieChart 
                :data="dataDistribution" 
                :legend="true"
              />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 实时告警 -->
    <div class="alerts-section">
      <el-card shadow="hover">
        <template #header>
          <div class="alert-header">
            <span>实时告警</span>
            <div>
              <el-tag type="danger" size="small">紧急: {{ criticalAlerts }}</el-tag>
              <el-tag type="warning" size="small">警告: {{ warningAlerts }}</el-tag>
              <el-tag type="info" size="small">信息: {{ infoAlerts }}</el-tag>
            </div>
          </div>
        </template>
        
        <el-table :data="activeAlerts" v-loading="alertsLoading">
          <el-table-column prop="severity" label="级别" width="80">
            <template #default="{row}">
              <el-tag :type="row.severity" size="small">
                {{ formatSeverity(row.severity) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="metric_name" label="指标" width="150" />
          
          <el-table-column prop="message" label="告警信息" min-width="300">
            <template #default="{row}">
              <div class="alert-message">
                <span>{{ row.message }}</span>
                <br />
                <small class="alert-detail">
                  当前值: {{ row.current_value }} | 阈值: {{ row.threshold }}
                </small>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="triggered_at" label="触发时间" width="180">
            <template #default="{row}">
              {{ formatTime(row.triggered_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="150">
            <template #default="{row}">
              <el-button size="small" @click="handleAcknowledge(row)">
                确认
              </el-button>
              <el-button size="small" @click="handleViewDetail(row)">
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
    
    <!-- 系统资源监控 -->
    <div class="resource-monitor">
      <el-card shadow="hover">
        <template #header>
          <span>系统资源监控</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <ResourceGauge 
              title="CPU使用率" 
              :value="cpuUsage" 
              :thresholds="[70, 90]"
            />
          </el-col>
          <el-col :span="6">
            <ResourceGauge 
              title="内存使用率" 
              :value="memoryUsage" 
              :thresholds="[80, 95]"
            />
          </el-col>
          <el-col :span="6">
            <ResourceGauge 
              title="磁盘使用率" 
              :value="diskUsage" 
              :thresholds="[85, 95]"
            />
          </el-col>
          <el-col :span="6">
            <ResourceGauge 
              title="数据库连接" 
              :value="dbConnections" 
              :max="dbMaxConnections"
            />
          </el-col>
        </el-row>
      </el-card>
    </div>
    
    <!-- 告警规则管理对话框 -->
    <AlertRuleDialog 
      v-model="ruleDialogVisible"
      :rule="currentRule"
      @success="handleRuleUpdated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useWebSocket } from '@vueuse/core'
import LineChart from './charts/LineChart.vue'
import PieChart from './charts/PieChart.vue'
import ResourceGauge from './charts/ResourceGauge.vue'
import AlertRuleDialog from './AlertRuleDialog.vue'

// WebSocket实时数据
const { data: wsMetrics } = useWebSocket('ws://localhost:8000/ws/metrics')

// 监控数据
const healthStatuses = ref([
  {
    name: '系统健康度',
    value: '健康',
    type: 'success',
    percentage: 98.5,
    progressStatus: 'success',
    detail: '较昨日 +0.5%',
    trend: 'up'
  },
  // ... 其他状态
])

const activeAlerts = ref([])
const alertsLoading = ref(false)

// 系统资源数据
const cpuUsage = ref(45.2)
const memoryUsage = ref(67.8)
const diskUsage = ref(32.1)
const dbConnections = ref(24)
const dbMaxConnections = ref(100)

// 加载告警数据
const loadAlerts = async () => {
  alertsLoading.value = true
  try {
    const response = await api.get('/monitor/alerts/active')
    activeAlerts.value = response.data
  } catch (error) {
    ElMessage.error('加载告警数据失败')
  } finally {
    alertsLoading.value = false
  }
}

// 处理告警
const handleAcknowledge = async (alert) => {
  try {
    await api.post(`/monitor/alerts/${alert.id}/acknowledge`)
    ElMessage.success('告警已确认')
    loadAlerts()
  } catch (error) {
    ElMessage.error('确认告警失败')
  }
}

// 定时刷新
onMounted(() => {
  loadAlerts()
  // 每30秒刷新一次
  setInterval(loadAlerts, 30000)
})
</script>