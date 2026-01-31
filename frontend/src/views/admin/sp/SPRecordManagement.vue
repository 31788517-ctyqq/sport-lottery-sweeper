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
    
    <!-- SP记录表格 -->
    <el-table 
      :data="tableData" 
      v-loading="loading"
      @selection-change="handleSelectionChange"
      stripe
    >
      <el-table-column type="selection" width="55" />
      
      <el-table-column prop="id" label="ID" width="80" />
      
      <el-table-column prop="match" label="比赛信息" width="250">
        <template #default="{ row }">
          <div class="match-info">
            <div class="match-id">#{{ row.match_id }}</div>
            <div class="teams">
              <span class="home-team">{{ row.match?.home_team || '-' }}</span>
              <span class="vs">VS</span>
              <span class="away-team">{{ row.match?.away_team || '-' }}</span>
            </div>
            <div class="league">{{ row.match?.league || '-' }}</div>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="company" label="公司" width="150">
        <template #default="{ row }">
          <span>{{ row.company?.name || '-' }}</span>
        </template>
      </el-table-column>
      
      <el-table-column prop="handicap_type" label="盘口类型" width="100">
        <template #default="{ row }">
          <el-tag :type="row.handicap_type === 'no_handicap' ? 'success' : 'warning'">
            {{ row.handicap_type === 'no_handicap' ? '不让球' : '让球' }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="handicap_value" label="让球数" width="100">
        <template #default="{ row }">
          {{ row.handicap_value ? (row.handicap_value > 0 ? `-${row.handicap_value}` : `+${Math.abs(row.handicap_value)}`) : '-' }}
        </template>
      </el-table-column>
      
      <el-table-column prop="sp_value" label="SP值" width="100">
        <template #default="{ row }">
          <span :class="['sp-value', row.sp_value > 50 ? 'sp-high' : 'sp-low']">
            {{ row.sp_value }}%
          </span>
        </template>
      </el-table-column>
      
      <el-table-column prop="recorded_at" label="记录时间" width="160">
        <template #default="{ row }">
          {{ formatDateTime(row.recorded_at) }}
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="primary" @click="handleViewTrend(row)">查看走势</el-button>
          <el-button size="small" type="info" @click="handleViewLogs(row)">修改日志</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <el-pagination
      class="pagination"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      :current-page="pagination.page"
      :page-sizes="[10, 20, 50, 100]"
      :page-size="pagination.size"
      layout="total, sizes, prev, pager, next, jumper"
      :total="pagination.total"
    />
    
    <!-- 手动录入弹窗 -->
    <el-dialog 
      :title="entryForm.id ? '编辑SP记录' : '手动录入SP值'" 
      v-model="entryDialogVisible" 
      width="500px"
    >
      <el-form 
        :model="entryForm" 
        :rules="entryRules" 
        ref="entryFormRef"
        label-width="100px"
      >
        <el-form-item label="比赛" prop="match_id">
          <el-select v-model="entryForm.match_id" placeholder="请选择比赛" filterable>
            <el-option 
              v-for="match in matchOptions"
              :key="match.id"
              :label="`${match.home_team} vs ${match.away_team}`"
              :value="match.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="公司" prop="company_id">
          <el-select v-model="entryForm.company_id" placeholder="请选择公司">
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
        
        <el-form-item 
          v-if="entryForm.handicap_type === 'handicap'" 
          label="让球数" 
          prop="handicap_value"
        >
          <el-input-number 
            v-model="entryForm.handicap_value" 
            :min="-5" 
            :max="5" 
            :step="0.5"
          />
        </el-form-item>
        
        <el-form-item label="SP值(%)" prop="sp_value">
          <el-slider 
            v-model="entryForm.sp_value" 
            :min="0" 
            :max="100" 
            :step="0.1"
            show-input
          />
        </el-form-item>
        
        <el-form-item label="记录时间" prop="recorded_at">
          <el-date-picker
            v-model="entryForm.recorded_at"
            type="datetime"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择时间"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="entryDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEntryForm">确定</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- SP值走势图弹窗 -->
    <el-dialog 
      title="SP值走势图" 
      v-model="trendDialogVisible" 
      width="80%"
      top="5vh"
    >
      <div class="chart-info">
        <h4>比赛信息：{{ trendMatchInfo }}</h4>
        <p>公司：{{ trendCompanyInfo }}</p>
        <p>盘口类型：{{ trendHandicapInfo }}</p>
      </div>
      <div class="trend-chart-container">
        <div class="chart-container" v-if="trendData && trendData.length > 0" style="height: 400px;"></div>
        <div class="no-data" v-else>
          <el-empty description="暂无趋势数据" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { Plus, Download, Edit } from '@element-plus/icons-vue'
import {
  getSPRecords,
  createSPRecord,
  updateSPRecord,
  getMatches,
  getOddsCompanies,
  getSPChartData
} from '@/api/spManagement'

// 从正确的API模块导入deleteSPRecord
import { deleteSPRecord } from '@/api/spManagement'

export default {
  name: 'SPRecordManagement',
  components: {
    Plus, Download, Edit
  },
  setup() {
    // 表格数据
    const tableData = ref([])
    const loading = ref(false)
    
    // 分页数据
    const pagination = reactive({
      page: 1,
      size: 20,
      total: 0
    })
    
    // 搜索表单
    const searchForm = reactive({
      match_id: null,
      match_search: '',
      company_id: null,
      handicap_type: '',
      sp_min: null,
      sp_max: null,
      timeRange: []
    })
    
    // 比赛选择选项
    const matchOptions = ref([])
    const matchLoading = ref(false)
    
    // 公司选择选项
    const companyOptions = ref([])
    
    // 弹窗相关
    const entryDialogVisible = ref(false)
    const entryFormRef = ref(null)
    const entryForm = reactive({
      id: null,
      match_id: null,
      company_id: null,
      handicap_type: 'no_handicap',
      handicap_value: null,
      sp_value: 50,
      recorded_at: new Date().toISOString().slice(0, 19).replace('T', ' ')
    })
    
    // 表单验证规则
    const entryRules = {
      match_id: [{ required: true, message: '请选择比赛', trigger: 'change' }],
      company_id: [{ required: true, message: '请选择公司', trigger: 'change' }],
      sp_value: [
        { required: true, message: '请输入SP值', trigger: 'blur' },
        { type: 'number', min: 0, max: 100, message: 'SP值必须在0-100之间', trigger: 'blur' }
      ]
    }
    
    // 趋势图相关
    const trendDialogVisible = ref(false)
    const trendData = ref([])
    const trendMatchInfo = ref('')
    const trendCompanyInfo = ref('')
    const trendHandicapInfo = ref('')
    let chartInstance = null
    
    // 选中行
    const selectedRows = ref([])
    
    // 加载数据
    const loadData = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.page,
          size: pagination.size,
          match_id: searchForm.match_id || undefined,
          company_id: searchForm.company_id || undefined,
          handicap_type: searchForm.handicap_type || undefined,
          date_from: searchForm.timeRange && searchForm.timeRange[0] ? searchForm.timeRange[0] : undefined,
          date_to: searchForm.timeRange && searchForm.timeRange[1] ? searchForm.timeRange[1] : undefined
        }
        
        if (searchForm.sp_min !== null) params.sp_min = searchForm.sp_min
        if (searchForm.sp_max !== null) params.sp_max = searchForm.sp_max
        
        const response = await getSPRecords(params)
        tableData.value = response.data.items || []
        pagination.total = response.data.total || 0
      } catch (error) {
        ElMessage.error('加载数据失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }
    
    // 加载比赛数据
    const loadMatches = async (keyword = '') => {
      try {
        const params = { size: 100 } // 获取前100场比赛
        if(keyword) params.search = keyword
        const response = await getMatches(params)
        matchOptions.value = response.data.items || []
      } catch (error) {
        console.error('加载比赛数据失败', error)
      }
    }
    
    // 加载公司数据
    const loadCompanies = async () => {
      try {
        const response = await getOddsCompanies({ active_only: true })
        companyOptions.value = response || []
      } catch (error) {
        console.error('加载公司数据失败', error)
      }
    }
    
    // 搜索比赛
    const searchMatches = async (keyword) => {
      if (!keyword) {
        loadMatches()
        return
      }
      matchLoading.value = true
      try {
        const response = await getMatches({ search: keyword, size: 100 })
        matchOptions.value = response.data.items || []
      } catch (error) {
        console.error('搜索比赛失败', error)
      } finally {
        matchLoading.value = false
      }
    }
    
    // 搜索比赛输入事件
    const handleMatchSearch = () => {
      if (searchForm.match_search) {
        searchMatches(searchForm.match_search)
      } else {
        loadMatches()
      }
    }
    
    // 搜索处理
    const handleSearch = () => {
      pagination.page = 1
      loadData()
    }
    
    // 重置搜索
    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = key === 'timeRange' ? [] : null
      })
      handleSearch()
    }
    
    // 手动录入
    const handleManualEntry = () => {
      resetEntryForm()
      entryDialogVisible.value = true
    }
    
    // 编辑记录
    const handleEdit = (row) => {
      Object.assign(entryForm, {
        id: row.id,
        match_id: row.match_id,
        company_id: row.company_id,
        handicap_type: row.handicap_type,
        handicap_value: row.handicap_value,
        sp_value: row.sp_value,
        recorded_at: row.recorded_at
      })
      entryDialogVisible.value = true
    }
    
    // 提交录入表单
    const submitEntryForm = async () => {
      try {
        if (entryForm.id) {
          await updateSPRecord(entryForm.id, {
            match_id: entryForm.match_id,
            company_id: entryForm.company_id,
            handicap_type: entryForm.handicap_type,
            handicap_value: entryForm.handicap_value,
            sp_value: entryForm.sp_value,
            recorded_at: entryForm.recorded_at
          })
          ElMessage.success('更新成功')
        } else {
          await createSPRecord({
            match_id: entryForm.match_id,
            company_id: entryForm.company_id,
            handicap_type: entryForm.handicap_type,
            handicap_value: entryForm.handicap_value,
            sp_value: entryForm.sp_value,
            recorded_at: entryForm.recorded_at
          })
          ElMessage.success('录入成功')
        }
        
        entryDialogVisible.value = false
        loadData()
      } catch (error) {
        ElMessage.error('操作失败')
        console.error(error)
      }
    }
    
    // 删除记录
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

    // 查看趋势
    const handleViewTrend = async (row) => {
      try {
        const response = await getSPChartData(row.match_id, row.company_id)
        trendData.value = response.data.trend || []
        trendMatchInfo.value = `${row.match?.home_team || ''} vs ${row.match?.away_team || ''}`
        trendCompanyInfo.value = row.company?.name || ''
        trendHandicapInfo.value = row.handicap_type === 'no_handicap' ? '不让球' : `${row.handicap_value > 0 ? '-' : '+'}${Math.abs(row.handicap_value)}`

        trendDialogVisible.value = true

        await nextTick()
        initChart()
      } catch (error) {
        ElMessage.error('加载走势数据失败')
      }
    }

    // 查看修改日志
    const handleViewLogs = (row) => {
      ElMessage.info(`查看SP记录 ${row.id} 的修改日志`)
    }

    // 导出功能
    const handleExport = () => {
      ElMessage.info('导出功能开发中...')
    }

    // 批量修正功能
    const handleBatchModify = () => {
      ElMessage.info('批量修正功能开发中...')
    }

    // 选择变化处理
    const handleSelectionChange = (selection) => {
      selectedRows.value = selection
    }

    // 分页大小变化
    const handleSizeChange = (size) => {
      pagination.size = size
      pagination.page = 1
      loadData()
    }

    // 当前页变化
    const handleCurrentChange = (page) => {
      pagination.page = page
      loadData()
    }

    // 重置录入表单
    const resetEntryForm = () => {
      Object.assign(entryForm, {
        id: null,
        match_id: null,
        company_id: null,
        handicap_type: 'no_handicap',
        handicap_value: null,
        sp_value: 50,
        recorded_at: new Date().toISOString().slice(0, 19).replace('T', ' ')
      })
      if (entryFormRef.value) {
        entryFormRef.value.resetFields()
      }
    }

    // 格式化日期时间
    const formatDateTime = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleString()
    }

    // 初始化图表
    const initChart = () => {
      if (!trendData.value || !trendData.value.length) return

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
          name: 'SP값',
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

    // 页面挂载时加载数据
    onMounted(() => {
      loadData()
      loadMatches()
      loadCompanies()
    })

    return {
      tableData,
      loading,
      pagination,
      searchForm,
      matchOptions,
      matchLoading,
      companyOptions,
      entryDialogVisible,
      entryFormRef,
      entryForm,
      entryRules,
      trendDialogVisible,
      trendData,
      trendMatchInfo,
      trendCompanyInfo,
      trendHandicapInfo,
      selectedRows,
      loadData,
      handleMatchSearch,
      searchMatches,
      handleSearch,
      resetSearch,
      handleManualEntry,
      handleEdit,
      submitEntryForm,
      handleDelete,
      handleViewTrend,
      handleViewLogs,
      handleExport,
      handleBatchModify,
      handleSelectionChange,
      handleSizeChange,
      handleCurrentChange,
      resetEntryForm,
      formatDateTime,
      initChart
    }
  }
}
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