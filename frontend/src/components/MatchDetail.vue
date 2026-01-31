<template>
  <div class="match-detail">
    <el-descriptions :column="2" border v-if="matchData">
      <el-descriptions-item label="比赛ID">{{ matchData.id }}</el-descriptions-item>
      <el-descriptions-item label="数据类型">
        <el-tag :type="getTypeColor(matchData.type)">{{ getTypeText(matchData.type) }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="数据源">{{ matchData.sourceName }}</el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="getStatusColor(matchData.status)">{{ getStatusText(matchData.status) }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="数据质量" span="2">
        <el-progress :percentage="matchData.quality" :color="getQualityColor(matchData.quality)" />
      </el-descriptions-item>
      <el-descriptions-item label="记录数量">{{ matchData.recordCount }}</el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ matchData.createdAt }}</el-descriptions-item>
      <el-descriptions-item label="更新时间">{{ matchData.updatedAt }}</el-descriptions-item>
      <el-descriptions-item label="标题" span="2">{{ matchData.title }}</el-descriptions-item>
      
      <!-- 比赛特定信息 -->
      <template v-if="matchData.matchInfo">
        <el-descriptions-item label="主队" v-if="matchData.matchInfo.homeTeam">{{ matchData.matchInfo.homeTeam }}</el-descriptions-item>
        <el-descriptions-item label="客队" v-if="matchData.matchInfo.awayTeam">{{ matchData.matchInfo.awayTeam }}</el-descriptions-item>
        <el-descriptions-item label="比赛时间" v-if="matchData.matchInfo.matchTime">{{ matchData.matchInfo.matchTime }}</el-descriptions-item>
        <el-descriptions-item label="联赛" v-if="matchData.matchInfo.league">{{ matchData.matchInfo.league }}</el-descriptions-item>
        <el-descriptions-item label="比分" v-if="matchData.matchInfo.score">{{ matchData.matchInfo.score }}</el-descriptions-item>
        <el-descriptions-item label="场地" v-if="matchData.matchInfo.venue">{{ matchData.matchInfo.venue }}</el-descriptions-item>
      </template>
    </el-descriptions>

    <!-- 详细信息标签页 -->
    <el-tabs v-model="activeTab" class="detail-tabs" v-if="matchData">
      <el-tab-pane label="基本信息" name="basic">
        <el-form :model="matchData" label-width="120px" class="detail-form">
          <el-form-item label="数据完整性">
            <el-progress :percentage="calculateCompleteness()" status="success" />
          </el-form-item>
          <el-form-item label="验证状态">
            <el-tag :type="matchData.quality >= 90 ? 'success' : matchData.quality >= 70 ? 'warning' : 'danger'">
              {{ matchData.quality >= 90 ? '通过' : matchData.quality >= 70 ? '部分通过' : '未通过' }}
            </el-tag>
          </el-form-item>
          <el-form-item label="错误信息" v-if="matchData.errors && matchData.errors.length > 0">
            <el-alert
              v-for="error in matchData.errors"
              :key="error.id"
              :title="error.message"
              type="error"
              :description="error.details"
              show-icon
              class="error-alert"
            />
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="字段详情" name="fields">
        <el-table :data="fieldDetails" border style="width: 100%">
          <el-table-column prop="fieldName" label="字段名" width="150" />
          <el-table-column prop="fieldValue" label="字段值" />
          <el-table-column prop="dataType" label="数据类型" width="100" />
          <el-table-column prop="nullable" label="可空" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.nullable ? 'info' : 'success'">
                {{ scope.row.nullable ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="valid" label="有效性" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.valid ? 'success' : 'danger'">
                {{ scope.row.valid ? '有效' : '无效' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="历史记录" name="history">
        <el-timeline>
          <el-timeline-item
            v-for="record in historyRecords"
            :key="record.id"
            :timestamp="record.timestamp"
            :type="record.type"
          >
            <div class="timeline-content">
              <h4>{{ record.action }}</h4>
              <p>{{ record.description }}</p>
              <div class="timeline-meta" v-if="record.user">
                操作者: {{ record.user }}
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </el-tab-pane>

      <el-tab-pane label="关联数据" name="related">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card header="相关比赛">
              <el-tree
                :data="relatedMatches"
                :props="treeProps"
                node-key="id"
                :highlight-current="true"
              />
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card header="相关数据">
              <el-table :data="relatedData" border size="small">
                <el-table-column prop="type" label="类型" width="80" />
                <el-table-column prop="title" label="标题" />
                <el-table-column prop="relation" label="关系" width="100" />
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>

    <!-- 操作按钮 -->
    <div class="detail-actions">
      <el-button @click="handleEdit">编辑</el-button>
      <el-button type="primary" @click="handleAnalyze">数据分析</el-button>
      <el-button type="success" @click="handleExport">导出详情</el-button>
      <el-button type="warning" @click="handleRefresh">刷新数据</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  matchData: {
    type: Object,
    default: null
  }
})

// 响应式数据
const activeTab = ref('basic')

// 树形控件配置
const treeProps = {
  children: 'children',
  label: 'title'
}

// 字段详情数据
const fieldDetails = ref([])

// 历史记录数据
const historyRecords = ref([])

// 相关比赛数据
const relatedMatches = ref([])

// 相关数据
const relatedData = ref([])

// 初始化详情数据
onMounted(() => {
  if (props.matchData) {
    initFieldDetails()
    initHistoryRecords()
    initRelatedData()
  }
})

// 初始化字段详情
const initFieldDetails = () => {
  if (!props.matchData) return
  
  // 模拟字段详情数据
  fieldDetails.value = [
    { fieldName: 'id', fieldValue: props.matchData.id, dataType: 'Number', nullable: false, valid: true },
    { fieldName: 'title', fieldValue: props.matchData.title, dataType: 'String', nullable: false, valid: true },
    { fieldName: 'type', fieldValue: props.matchData.type, dataType: 'String', nullable: false, valid: true },
    { fieldName: 'sourceName', fieldValue: props.matchData.sourceName, dataType: 'String', nullable: false, valid: true },
    { fieldName: 'status', fieldValue: props.matchData.status, dataType: 'String', nullable: false, valid: true },
    { fieldName: 'quality', fieldValue: props.matchData.quality + '%', dataType: 'Number', nullable: false, valid: props.matchData.quality >= 70 },
    { fieldName: 'recordCount', fieldValue: props.matchData.recordCount, dataType: 'Number', nullable: false, valid: true },
    { fieldName: 'createdAt', fieldValue: props.matchData.createdAt, dataType: 'DateTime', nullable: false, valid: true },
    { fieldName: 'updatedAt', fieldValue: props.matchData.updatedAt, dataType: 'DateTime', nullable: false, valid: true }
  ]
}

// 初始化历史记录
const initHistoryRecords = () => {
  // 模拟历史记录数据
  historyRecords.value = [
    {
      id: 1,
      timestamp: new Date(Date.now() - 86400000).toLocaleString(),
      action: '数据创建',
      description: '数据记录首次创建',
      type: 'primary',
      user: '系统'
    },
    {
      id: 2,
      timestamp: new Date(Date.now() - 43200000).toLocaleString(),
      action: '数据更新',
      description: '更新了比赛信息和赔率数据',
      type: 'success',
      user: 'admin'
    },
    {
      id: 3,
      timestamp: new Date(Date.now() - 21600000).toLocaleString(),
      action: '质量检查',
      description: '数据质量检查通过，质量评分提升至94%',
      type: 'info',
      user: '质检系统'
    }
  ]
}

// 初始化相关数据
const initRelatedData = () => {
  // 模拟相关比赛数据
  relatedMatches.value = [
    {
      id: 1,
      title: '相关比赛 1',
      children: [
        { id: 11, title: '同联赛比赛' },
        { id: 12, title: '相同球队比赛' }
      ]
    },
    {
      id: 2,
      title: '相关比赛 2'
    }
  ]
  
  // 模拟相关数据
  relatedData.value = [
    { type: '赔率', title: '主要赔率数据', relation: '关联' },
    { type: '事件', title: '比赛事件记录', relation: '包含' },
    { type: '统计', title: '数据统计信息', relation: '衍生' }
  ]
}

// 计算数据完整性
const calculateCompleteness = () => {
  if (!props.matchData) return 0
  
  let totalFields = fieldDetails.value.length
  let validFields = fieldDetails.value.filter(field => field.valid).length
  
  return Math.round((validFields / totalFields) * 100)
}

// 获取类型颜色
const getTypeColor = (type) => {
  const colors = {
    matches: 'primary',
    odds: 'success',
    events: 'warning',
    statistics: 'info'
  }
  return colors[type] || 'info'
}

// 获取类型文本
const getTypeText = (type) => {
  const texts = {
    matches: '比赛',
    odds: '赔率',
    events: '事件',
    statistics: '统计'
  }
  return texts[type] || type
}

// 获取状态颜色
const getStatusColor = (status) => {
  const colors = {
    normal: 'success',
    error: 'danger',
    warning: 'warning'
  }
  return colors[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    normal: '正常',
    error: '异常',
    warning: '警告'
  }
  return texts[status] || status
}

// 获取质量颜色
const getQualityColor = (quality) => {
  if (quality >= 90) return '#67C23A'
  if (quality >= 70) return '#E6A23C'
  return '#F56C6C'
}

// 事件处理
const handleEdit = () => {
  ElMessage.info('打开编辑模式')
}

const handleAnalyze = () => {
  ElMessage.info('开始数据分析')
}

const handleExport = () => {
  ElMessage.info('导出详情数据')
}

const handleRefresh = () => {
  ElMessage.success('刷新任务已提交')
}
</script>

<style scoped lang="scss">
.match-detail {
  padding: 20px;

  .detail-tabs {
    margin-top: 20px;
  }

  .detail-form {
    .error-alert {
      margin-bottom: 10px;
    }
  }

  .timeline-content {
    h4 {
      margin: 0 0 8px 0;
      color: #303133;
    }

    p {
      margin: 0 0 8px 0;
      color: #606266;
    }

    .timeline-meta {
      font-size: 12px;
      color: #909399;
    }
  }

  .detail-actions {
    margin-top: 30px;
    text-align: center;
    padding-top: 20px;
    border-top: 1px solid #eee;
  }

  // 响应式设计
  @media (max-width: 768px) {
    padding: 10px;

    .detail-actions {
      .el-button {
        margin-bottom: 10px;
        width: 100%;
      }
    }
  }
}
</style>