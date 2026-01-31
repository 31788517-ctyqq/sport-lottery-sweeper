<template>
  <div class="page-container">
    <el-row :gutter="20" class="kpi-row">
      <el-col :span="6" v-for="item in kpiData" :key="item.label">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-label">{{ item.label }}</div>
          <div class="kpi-value">{{ item.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card header="抓取量趋势" class="chart-card">
          <div ref="lineChart" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="错误类型分布" class="chart-card">
          <div ref="pieChart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="box-card">
      <template #header>
        <span class="card-header">数据明细</span>
        <div>
          <el-button type="primary" size="small" @click="handleExport" style="margin-left: 10px;">导出CSV</el-button>
          <el-button type="danger" size="small" @click="batchMarkInvalid" style="margin-left: 10px;" :disabled="!multipleSelection.length">批量标记无效</el-button>
          <el-button type="warning" size="small" @click="batchRecrawl" style="margin-left: 10px;" :disabled="!multipleSelection.length">批量重抓</el-button>
        </div>
      </template>

      <el-table 
        :data="tableData" 
        border 
        style="width: 100%" 
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="source_id" label="数据源ID" width="100" />
        <el-table-column prop="total_count" label="抓取总数" width="100" />
        <el-table-column prop="success_count" label="成功数" width="100" />
        <el-table-column prop="failed_count" label="失败数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" type="warning" @click="markAsInvalid(scope.row.id)">标记无效</el-button>
            <el-button size="small" type="primary" @click="recrawlData(scope.row.id)">重新抓取</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { getStats, getData, exportData, markAsInvalid as apiMarkAsInvalid, recrawlData as apiRecrawlData, batchMarkData } from '@/api/crawlerIntelligence'

const kpiData = ref([])
const tableData = ref([])
const lineChart = ref(null)
const pieChart = ref(null)
const multipleSelection = ref([])

let lineInstance = null
let pieInstance = null

const getStatusType = (status) => {
  if (status === 'valid') return 'success'
  if (status === 'invalid') return 'danger'
  if (status === 'pending') return 'info'
  return 'warning'
}

const renderCharts = (stats) => {
  // 抓取量趋势（模拟最近 7 天）
  const dates = Array.from({ length: 7 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (6 - i))
    return d.toISOString().slice(5, 10)
  })
  const values = Array.from({ length: 7 }, () => Math.floor(Math.random() * 300 + 700))

  lineInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: dates },
    yAxis: { type: 'value' },
    series: [{ data: values, type: 'line', smooth: true }]
  })

  // 错误类型分布
  pieInstance.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: '60%',
      data: [
        { value: stats.today_failed, name: '失败' },
        { value: stats.today_success, name: '成功' }
      ],
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
    }]
  })
}

const loadData = async () => {
  const statsRes = await getStats()
  const stats = statsRes.data || {}
  kpiData.value = [
    { label: '今日抓取总数', value: stats.today_total || 0 },
    { label: '今日成功', value: stats.today_success || 0 },
    { label: '今日失败', value: stats.today_failed || 0 },
    { label: '总成功率(%)', value: stats.overall_success_rate ? stats.overall_success_rate.toFixed(2) : '0.00' }
  ]

  const dataRes = await getData()
  tableData.value = dataRes.data || []

  renderCharts(stats)
}

const handleExport = async () => {
  try {
    const res = await exportData()
    // 真实场景会触发文件下载
    ElMessage.success(`导出链接：${res.data.download_url || '已开始导出'}`)
  } catch (err) {
    ElMessage.error('导出失败')
  }
}

const handleSelectionChange = (val) => {
  multipleSelection.value = val
}

const batchMarkInvalid = async () => {
  if (!multipleSelection.value.length) {
    ElMessage.warning('请至少选择一项')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要将 ${multipleSelection.value.length} 项标记为无效吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const ids = multipleSelection.value.map(item => item.id)
    await batchMarkData(ids, 'invalid')
    ElMessage.success('批量标记成功')
    loadData()
  } catch (err) {
    // 用户取消操作
  }
}

const batchRecrawl = async () => {
  if (!multipleSelection.value.length) {
    ElMessage.warning('请至少选择一项')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要重新抓取 ${multipleSelection.value.length} 项数据吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const ids = multipleSelection.value.map(item => item.id)
    await batchMarkData(ids, 'pending') // 设置为待抓取状态
    ElMessage.success('已加入重抓队列')
    loadData()
  } catch (err) {
    // 用户取消操作
  }
}

const markAsInvalid = async (id) => {
  try {
    await ElMessageBox.confirm('确定要将此数据标记为无效吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await apiMarkAsInvalid(id)
    ElMessage.success('标记成功')
    loadData()
  } catch (err) {
    // 用户取消操作
  }
}

const recrawlData = async (id) => {
  try {
    await ElMessageBox.confirm('确定要重新抓取此数据吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await apiRecrawlData(id)
    ElMessage.success('已加入重抓队列')
    loadData()
  } catch (err) {
    // 用户取消操作
  }
}

onMounted(() => {
  lineInstance = echarts.init(lineChart.value)
  pieInstance = echarts.init(pieChart.value)
  loadData()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}
.kpi-row {
  margin-bottom: 20px;
}
.kpi-card {
  text-align: center;
}
.kpi-label {
  font-size: 14px;
  color: #666;
}
.kpi-value {
  font-size: 24px;
  font-weight: bold;
  margin-top: 10px;
}
.chart-row {
  margin-bottom: 20px;
}
.chart-card {
  height: 300px;
}
.chart {
  width: 100%;
  height: 240px;
}
.box-card {
  margin-bottom: 20px;
}
.card-header {
  font-weight: bold;
  font-size: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>