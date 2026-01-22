<template>
  <div class="sp-record-management">
    <!-- 搜索和操作栏 -->
    <div class="toolbar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="比赛">
          <el-input 
            v-model="searchForm.match_search" 
            placeholder="比赛ID/主队/客队" 
            clearable
            style="width: 200px"
            @input="handleMatchSearch"
          />
          <el-select 
            v-if="matchOptions.length > 0"
            v-model="searchForm.match_id"
            placeholder="选择比赛"
            clearable
            filterable
            remote
            :remote-method="searchMatches"
            :loading="matchLoading"
            style="width: 200px; margin-left: 10px"
          >
            <el-option 
              v-for="match in matchOptions"
              :key="match.id"
              :label="`${match.home_team} vs ${match.away_team}`"
              :value="match.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="公司">
          <el-select v-model="searchForm.company_id" placeholder="请选择公司" clearable style="width: 150px">
            <el-option 
              v-for="company in companyOptions"
              :key="company.id"
              :label="company.name"
              :value="company.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="盘口类型">
          <el-select v-model="searchForm.handicap_type" placeholder="请选择" clearable style="width: 120px">
            <el-option label="不让球" value="no_handicap" />
            <el-option label="让球" value="handicap" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="SP值范围">
          <el-input-number 
            v-model="searchForm.sp_min" 
            :min="0" 
            :max="100" 
            placeholder="最小值"
            style="width: 100px"
          />
          <span style="margin: 0 5px">-</span>
          <el-input-number 
            v-model="searchForm.sp_max" 
            :min="0" 
            :max="100" 
            placeholder="最大值"
            style="width: 100px"
          />
        </el-form-item>
        
        <el-form-item label="记录时间">
          <el-date-picker
            v-model="searchForm.timeRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 350px"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      
      <div class="action-buttons">
        <el-button type="primary" @click="handleManualEntry">
          <el-icon><Plus /></el-icon>
          手动录入
        </el-button>
        <el-button type="success" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
        <el-button type="warning" @click="handleBatchModify">
          <el-icon><Edit /></el-icon>
          批量修正
        </el-button>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="tableData"
      v-loading="loading"
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column label="比赛信息" min-width="200">
        <template #default="scope">
          <div class="match-info">
            <div class="match-id">ID: {{ scope.row.match?.match_id }}</div>
            <div class="teams">
              <span class="home-team">{{ scope.row.match?.home_team }}</span>
              <span class="vs">VS</span>
              <span class="away-team">{{ scope.row.match?.away_team }}</span>
            </div>
            <div class="league">{{ scope.row.match?.league }}</div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="公司" width="120">
        <template #default="scope">
          <el-tag v-if="scope.row.company">{{ scope.row.company.name }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="盘口" width="100">
        <template #default="scope">
          <span v-if="scope.row.handicap_type === 'no_handicap'">不让球</span>
          <span v-else>{{ scope.row.handicap_value > 0 ? `-${scope.row.handicap_value}` : `+${Math.abs(scope.row.handicap_value)}` }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="sp_value" label="SP值" width="100">
        <template #default="scope">
          <span class="sp-value" :class="{'sp-high': scope.row.sp_value > 3, 'sp-low': scope.row.sp_value < 1.5}">
            {{ scope.row.sp_value }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="recorded_at" label="记录时间" width="160">
        <template #default="scope">
          {{ formatDateTime(scope.row.recorded_at) }}
        </template>
      </el-table-column>
      <el-table-column label="修改次数" width="100">
        <template #default="scope">
          <el-badge :value="scope.row.modification_logs?.length || 0" :hidden="!scope.row.modification_logs?.length">
            <el-tag type="info" size="small">已修改</el-tag>
          </el-badge>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="handleViewTrend(scope.row)">
            走势图
          </el-button>
          <el-button size="small" type="primary" @click="handleEdit(scope.row)">
            编辑
          </el-button>
          <el-button 
            size="small" 
            type="info" 
            @click="handleViewLogs(scope.row)"
          >
            修改日志
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="handleDelete(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 手动录入对话框 -->
    <el-dialog
      title="手动录入SP值"
      v-model="entryDialogVisible"
      width="500px"
      @close="resetEntryForm"
    >
      <el-form
        ref="entryFormRef"
        :model="entryForm"
        :rules="entryRules"
        label-width="100px"
      >
        <el-form-item label="比赛" prop="match_id">
          <el-select
            v-model="entryForm.match_id"
            placeholder="请选择比赛"
            filterable
            remote
            :remote-method="searchMatches"
            :loading="matchLoading"
            style="width: 100%"
          >
            <el-option 
              v-for="match in matchOptions"
              :key="match.id"
              :label="`${match.home_team} vs ${match.away_team} (${match.match_time})`"
              :value="match.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="公司" prop="company_id">
          <el-select v-model="entryForm.company_id" placeholder="请选择公司" style="width: 100%">
            <el-option 
              v-for="company in companyOptions"
              :key="company.id"
              :label="company.name"
              :value="company.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="盘口类型" prop="handicap_type">
          <el-radio-group v-model="entryForm.handicap_type">
            <el-radio label="no_handicap">不让球</el-radio>
            <el-radio label="handicap">让球</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="让球数值" prop="handicap_value" v-if="entryForm.handicap_type === 'handicap'">
          <el-input-number 
            v-model="entryForm.handicap_value" 
            :min="-5" 
            :max="5" 
            :step="0.5"
            style="width: 100%"
            placeholder="请输入让球数值"
          />
        </el-form-item>
        
        <el-form-item label="SP值" prop="sp_value">
          <el-input-number 
            v-model="entryForm.sp_value" 
            :min="0.01" 
            :max="100" 
            :precision="2"
            :step="0.1"
            style="width: 100%"
            placeholder="请输入SP值"
          />
        </el-form-item>
        
        <el-form-item label="记录时间" prop="recorded_at">
          <el-date-picker
            v-model="entryForm.recorded_at"
            type="datetime"
            placeholder="请选择记录时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="entryDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEntrySubmit" :loading="entryLoading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 走势图对话框 -->
    <el-dialog
      title="SP值走势图"
      v-model="trendDialogVisible"
      width="800px"
    >
      <div v-if="trendData.length > 0" class="trend-chart-container">
        <div class="chart-info">
          <h4>{{ trendMatchInfo }}</h4>
          <p>{{ trendCompanyInfo }}</p>
          <p>盘口: {{ trendHandicapInfo }}</p>
        </div>
        <div ref="chartContainer" style="height: 400px;"></div>
      </div>
      <div v-else class="no-data">
        <el-empty description="暂无走势数据" />
      </div>
      <template #footer>
        <el-button @click="trendDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Edit } from '@element-plus/icons-vue'
import { getSPRecordList, createSPRecord, updateSPRecord, deleteSPRecord, getSPRecordTrend } from '@/api/sp'
import * as echarts from 'echarts'

// 响应式数据
const loading = ref(false)
const entryLoading = ref(false)
const matchLoading = ref(false)
const entryDialogVisible = ref(false)
const trendDialogVisible = ref(false)
const entryFormRef = ref()
const tableData = ref([])
const selectedRows = ref([])
const matchOptions = ref([])
const companyOptions = ref([])
let chartInstance = null

// 搜索表单
const searchForm = reactive({
  match_search: '',
  match_id: null,
  company_id: null,
  handicap_type: '',
  sp_min: null,
  sp_max: null,
  timeRange: []
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 录入表单
const entryForm = reactive({
  match_id: null,
  company_id: null,
  handicap_type: 'no_handicap',
  handicap_value: null,
  sp_value: null,
  recorded_at: new Date().toISOString().slice(0, 19).replace('T', ' ')
})

// 录入表单验证规则
const entryRules = {
  match_id: [{ required: true, message: '请选择比赛', trigger: 'change' }],
  company_id: [{ required: true, message: '请选择公司', trigger: 'change' }],
  sp_value: [{ required: true, message: '请输入SP值', trigger: 'blur' }],
  recorded_at: [{ required: true, message: '请选择记录时间', trigger: 'change' }]
}

// 走势图数据
const trendData = ref([])
const trendMatchInfo = ref('')
const trendCompanyInfo = ref('')
const trendHandicapInfo = ref('')

// 方法
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      size: pagination.size
    }
    // 处理时间范围
    if (params.timeRange && params.timeRange.length === 2) {
      params.start_time = params.timeRange[0]
      params.end_time = params.timeRange[1]
      delete params.timeRange
    }
    
    const response = await getSPRecordList(params)
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadCompanies = async () => {
  try {
    // 这里应该调用获取公司列表的API
    // const response = await getOddsCompanyList()
    // companyOptions.value = response.data.items
    // 模拟数据
    companyOptions.value = [
      { id: 1, name: '竞彩官方' },
      { id: 2, name: '威廉希尔' },
      { id: 3, name: '立博' },
      { id: 4, name: 'Bet365' }
    ]
  } catch (error) {
    ElMessage.error('加载公司数据失败')
  }
}

const searchMatches = async (query) => {
  if (!query) {
    matchOptions.value = []
    return
  }
  
  matchLoading.value = true
  try {
    // 这里应该调用搜索比赛的API
    // const response = await searchMatchesApi(query)
    // matchOptions.value = response.data.items
    // 模拟延迟
    setTimeout(() => {
      matchOptions.value = [
        { id: 1, match_id: 'M001', home_team: '北京国安', away_team: '上海申花', match_time: '2024-01-15 15:30:00' },
        { id: 2, match_id: 'M002', home_team: '广州恒大', away_team: '山东鲁能', match_time: '2024-01-16 19:00:00' }
      ].filter(match => 
        match.match_id.includes(query) ||
        match.home_team.includes(query) ||
        match.away_team.includes(query)
      )
      matchLoading.value = false
    }, 500)
  } catch (error) {
    ElMessage.error('搜索比赛失败')
    matchLoading.value = false
  }
}

const handleMatchSearch = (value) => {
  if (!value) {
    searchForm.match_id = null
    matchOptions.value = []
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    match_search: '',
    match_id: null,
    company_id: null,
    handicap_type: '',
    sp_min: null,
    sp_max: null,
    timeRange: []
  })
  matchOptions.value = []
  handleSearch()
}

const handleManualEntry = () => {
  resetEntryForm()
  entryDialogVisible.value = true
}

const handleEntrySubmit = async () => {
  if (!entryFormRef.value) return
  
  try {
    await entryFormRef.value.validate()
    entryLoading.value = true
    
    await createSPRecord(entryForm)
    ElMessage.success('录入成功')
    entryDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('录入失败')
  } finally {
    entryLoading.value = false
  }
}

const handleEdit = (row) => {
  ElMessage.info('编辑功能开发中...')
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确认删除该SP记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteSPRecord(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleViewTrend = async (row) => {
  try {
    const response = await getSPRecordTrend(row.match_id, row.company_id, row.handicap_type, row.handicap_value)
    trendData.value = response.data.trend
    trendMatchInfo.value = `${row.match?.home_team} vs ${row.match?.away_team}`
    trendCompanyInfo.value = row.company?.name
    trendHandicapInfo.value = row.handicap_type === 'no_handicap' ? '不让球' : `${row.handicap_value > 0 ? '-' : '+'}${Math.abs(row.handicap_value)}`
    
    trendDialogVisible.value = true
    
    await nextTick()
    initChart()
  } catch (error) {
    ElMessage.error('加载走势数据失败')
  }
}

const handleViewLogs = (row) => {
  ElMessage.info(`查看SP记录 ${row.id} 的修改日志`)
}

const handleExport = () => {
  ElMessage.info('导出功能开发中...')
}

const handleBatchModify = () => {
  ElMessage.info('批量修正功能开发中...')
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadData()
}

const resetEntryForm = () => {
  Object.assign(entryForm, {
    match_id: null,
    company_id: null,
    handicap_type: 'no_handicap',
    handicap_value: null,
    sp_value: null,
    recorded_at: new Date().toISOString().slice(0, 19).replace('T', ' ')
  })
  if (entryFormRef.value) {
    entryFormRef.value.resetFields()
  }
}

const formatDateTime = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString()
}

// 图表相关方法
const initChart = () => {
  if (!trendData.value.length) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  const chartDom = document.querySelector('.trend-chart-container .chart-container')
  if (!chartDom) return
  
  chartInstance = echarts.init(chartDom)
  
  const dates = trendData.value.map(item => new Date(item.recorded_at).toLocaleString())
  const spValues = trendData.value.map(item => parseFloat(item.sp_value))
  
  const option = {
    title: {
      text: 'SP值走势图',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        return `${params[0].name}<br/>SP值: ${params[0].value}`
      }
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: 'SP值'
    },
    series: [{
      name: 'SP值',
      type: 'line',
      data: spValues,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        color: '#409EFF',
        width: 2
      },
      itemStyle: {
        color: '#409EFF'
      }
    }]
  }
  
  chartInstance.setOption(option)
}

// 生命周期
onMounted(() => {
  loadData()
  loadCompanies()
})
</script>

<style scoped>
.sp-record-management {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 20px;
}

.search-form {
  flex: 1;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.match-info {
  line-height: 1.4;
}

.match-id {
  font-size: 12px;
  color: #909399;
}

.teams {
  margin: 4px 0;
  font-weight: 500;
}

.home-team {
  color: #409EFF;
}

.away-team {
  color: #E6A23C;
}

.vs {
  margin: 0 8px;
  color: #909399;
  font-size: 12px;
}

.league {
  font-size: 12px;
  color: #909399;
}

.sp-value {
  font-weight: bold;
  font-size: 16px;
}

.sp-high {
  color: #E6A23C;
}

.sp-low {
  color: #67C23A;
}

.trend-chart-container {
  height: 500px;
}

.chart-info {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.chart-info h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.chart-info p {
  margin: 5px 0;
  color: #606266;
}

.no-data {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-date-editor) {
  width: 100%;
}
</style>