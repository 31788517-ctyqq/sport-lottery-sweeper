<template>
  <div class="jingcai-match-management">
    <!-- 主内容区与边栏 8:4 -->
    <el-row :gutter="20">
      <!-- 左侧主内容区 16/24 -->
      <el-col :xs="24" :sm="24" :md="24" :lg="16">
        <!-- 工具栏卡片 -->
        <BaseCard
          variant="primary"
          headerVariant="toolbar"
          title="筛选条件"
          icon="el-icon-search"
          toolbarAlign="left"
          shadow
          border
          class="mb-4"
        >
          <el-row :gutter="20" align="middle">
            <el-col :span="24" :md="8">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索联赛、主队、客队"
                clearable
                @clear="handleSearch"
                @keyup.enter="handleSearch"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :span="24" :md="4">
              <el-select v-model="selectedDays" placeholder="选择天数" @change="handleDaysChange">
                <el-option label="近3天" :value="3" />
                <el-option label="近5天" :value="5" />
                <el-option label="近7天" :value="7" />
                <el-option label="近15天" :value="15" />
                <el-option label="近30天" :value="30" />
              </el-select>
            </el-col>
            <el-col :span="24" :md="4">
              <el-select v-model="selectedLeague" placeholder="选择联赛" clearable @change="handleLeagueChange">
                <el-option
                  v-for="league in leagues"
                  :key="league.id"
                  :label="league.name"
                  :value="league.id"
                />
              </el-select>
            </el-col>
            <el-col :span="24" :md="8">
              <el-button type="primary" @click="refreshData">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
              <el-button type="success" @click="showImportDialog = true">
                <el-icon><Upload /></el-icon>
                导入数据
              </el-button>
            </el-col>
          </el-row>
        </BaseCard>

        <!-- 数据导入对话框 -->
        <el-dialog
          v-model="showImportDialog"
          title="导入比赛数据"
          width="600px"
          :close-on-click-modal="false"
        >
          <el-form :model="importForm" label-width="120px">
            <el-form-item label="选择联赛">
              <el-select v-model="importForm.leagueId" placeholder="请选择联赛" style="width: 100%">
                <el-option
                  v-for="league in leagues"
                  :key="league.id"
                  :label="league.name"
                  :value="league.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="导入方式">
              <el-radio-group v-model="importForm.importType">
                <el-radio value="file">文件导入</el-radio>
                <el-radio value="crawler">爬虫导入</el-radio>
                <el-radio value="api">外部接口</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item v-if="importForm.importType === 'file'" label="上传文件">
              <el-upload
                class="upload-demo"
                drag
                :action="uploadUrl"
                :headers="uploadHeaders"
                :on-success="handleUploadSuccess"
                :on-error="handleUploadError"
                :before-upload="beforeUpload"
                accept=".csv,.xlsx,.xls"
                :data="uploadData"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
                <template #tip>
                  <div class="el-upload__tip">支持 CSV、Excel 格式文件，文件不超过 10MB</div>
                </template>
              </el-upload>
            </el-form-item>
          </el-form>

          <template #footer>
            <span class="dialog-footer">
              <el-button @click="showImportDialog = false">取消</el-button>
              <el-button type="primary" @click="handleImport" :loading="importLoading">
                开始导入
              </el-button>
            </span>
          </template>
        </el-dialog>

        <!-- 表格卡片 -->
        <BaseCard
          variant="default"
          shadow
          border
          padding="0"
          class="mb-4"
        >
          <el-table
            :data="filteredMatches"
            style="width: 100%"
            v-loading="loading"
            stripe
            border
          >
            <el-table-column prop="match_identifier" label="比赛编号" width="150" />
            <el-table-column prop="league_name" label="联赛" width="120" />
            <el-table-column prop="round_number" label="轮次" width="80" />
            <el-table-column label="比赛时间" width="180">
              <template #default="scope">
                {{ formatDateTime(scope.row.scheduled_kickoff) }}
              </template>
            </el-table-column>
            <el-table-column label="对阵" min-width="200">
              <template #default="scope">
                <div class="match-teams">
                  <span class="home-team">{{ scope.row.home_team }}</span>
                  <span class="vs">VS</span>
                  <span class="away-team">{{ scope.row.away_team }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusTagType(scope.row.status)" size="small">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="重要程度" width="100">
              <template #default="scope">
                <el-tag :type="getImportanceTagType(scope.row.importance)" size="small">
                  {{ getImportanceText(scope.row.importance) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="推荐" width="80">
              <template #default="scope">
                <el-icon v-if="scope.row.is_featured" color="#E6A23C"><Star /></el-icon>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="handleView(scope.row)">查看</el-button>
                <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
                <el-button 
                  size="small" 
                  :type="scope.row.is_published ? 'warning' : 'success'"
                  @click="togglePublish(scope.row)"
                >
                  {{ scope.row.is_published ? '取消发布' : '发布' }}
                </el-button>
                <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </BaseCard>

        <!-- 分页卡片 -->
        <BaseCard
          variant="default"
          shadow
          border
          showHeader="false"
          padding="1rem"
        >
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </BaseCard>
      </el-col>

      <!-- 右侧边栏 8/24 -->
      <el-col :xs="24" :sm="24" :md="24" :lg="8">
        <!-- 统计信息卡片 -->
        <BaseCard
          variant="primary"
          title="数据概览"
          icon="el-icon-data-line"
          shadow
          border
          class="mb-4"
        >
          <div class="stats">
            <p>总期次：{{ new Set(filteredMatches.map(m => m.round_number)).size }}</p>
            <p>今日比赛：{{ filteredMatches.filter(m => isToday(m.scheduled_kickoff)).length }}</p>
            <p>进行中期次：{{ filteredMatches.filter(m => ['live','halftime'].includes(m.status)).length }}</p>
          </div>
        </BaseCard>

        <!-- 快捷操作卡片 -->
        <BaseCard
          variant="info"
          title="快捷操作"
          shadow
          border
          class="mb-4"
        >
          <el-button type="primary" style="width:100%;margin-bottom:8px" @click="refreshData">
            <el-icon><Refresh /></el-icon>刷新
          </el-button>
          <el-button type="success" style="width:100%;margin-bottom:8px" @click="showImportDialog=true">
            <el-icon><Upload /></el-icon>导入数据
          </el-button>
          <el-button type="warning" style="width:100%" @click="fetchCrawlerData">
            <el-icon><Search /></el-icon>爬取数据
          </el-button>
        </BaseCard>

        <!-- 状态分布卡片 -->
        <BaseCard
          variant="secondary"
          title="状态分布"
          icon="el-icon-pie-chart"
          shadow
          border
        >
          <div v-for="stat in statusDistribution" :key="stat.status" class="status-item">
            <el-tag :type="getStatusTagType(stat.status)" size="mini">{{ getStatusText(stat.status) }}</el-tag>
            <span>{{ stat.count }}</span>
          </div>
        </BaseCard>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Upload, UploadFilled, Star } from '@element-plus/icons-vue'
import BaseCard from '@/components/common/BaseCard.vue'
// AI_WORKING: coder1 @2025-01-31 12:00:00 - 修复http导入错误，http是默认导出
import http from '@/utils/http'
// AI_DONE: coder1 @2025-01-31 12:00:00

export default {
  name: 'JingcaiMatchManagement',
  components: {
    Search,
    Refresh,
    Upload,
    UploadFilled,
    Star,
    BaseCard
  },
  setup() {
    // 响应式数据
    const loading = ref(false)
    const matches = ref([])
    const leagues = ref([])
    const activeTab = ref('jingcai')
    const selectedDays = ref(5)
    const selectedLeague = ref('')
    const searchKeyword = ref('')
    const showImportDialog = ref(false)
    const importLoading = ref(false)

    // 分页
    const pagination = reactive({
      page: 1,
      size: 20,
      total: 0
    })

    // 导入表单
    const importForm = reactive({
      leagueId: '',
      importType: 'file'
    })

    // 计算属性
    const filteredMatches = computed(() => {
      let filtered = matches.value
      
      // 联赛筛选
      if (selectedLeague.value) {
        filtered = filtered.filter(match => match.league_id === selectedLeague.value)
      }
      
      // 关键词搜索
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        filtered = filtered.filter(match => 
          match.league_name?.toLowerCase().includes(keyword) ||
          match.home_team?.toLowerCase().includes(keyword) ||
          match.away_team?.toLowerCase().includes(keyword) ||
          match.match_identifier?.toLowerCase().includes(keyword)
        )
      }
      
      return filtered
    })

    // 上传相关
    const uploadUrl = computed(() => `${import.meta.env.VITE_API_BASE_URL}/admin/matches/import/file`)
    const uploadHeaders = computed(() => ({
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }))
    const uploadData = computed(() => ({
      league_id: importForm.leagueId
    }))

    // 方法
    const fetchMatches = async () => {
      loading.value = true
      try {
        const response = await http.get('/admin/matches/jingcai/matches', {
          params: { days: selectedDays.value }
        })
        if (response.code === 200) {
          matches.value = response.data || []
          pagination.total = matches.value.length
        } else {
          ElMessage.error(response.message || '获取比赛数据失败')
        }
      } catch (error) {
        console.error('获取比赛数据失败:', error)
        ElMessage.error('获取比赛数据失败')
      } finally {
        loading.value = false
      }
    }

    const fetchLeagues = async () => {
      try {
        const response = await http.get('/admin/matches/leagues')
        if (response.code === 200) {
          leagues.value = response.data || []
        }
      } catch (error) {
        console.error('获取联赛列表失败:', error)
      }
    }

    const handleSearch = () => {
      pagination.page = 1
    }

    const handleDaysChange = () => {
      pagination.page = 1
      fetchMatches()
    }

    const handleLeagueChange = () => {
      pagination.page = 1
    }

    const refreshData = () => {
      pagination.page = 1
      fetchMatches()
      ElMessage.success('数据已刷新')
    }

    const handleView = (row) => {
      console.log('查看比赛详情:', row)
      // 实现查看详情逻辑
    }

    const handleEdit = (row) => {
      console.log('编辑比赛:', row)
      // 实现编辑逻辑
    }

    const handleDelete = async (row) => {
      try {
        await ElMessageBox.confirm(`确定要删除比赛 "${row.home_team} VS ${row.away_team}" 吗？`, '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const response = await http.delete(`/admin/matches/${row.id}`)
        if (response.code === 200) {
          ElMessage.success('删除成功')
          fetchMatches()
        } else {
          ElMessage.error(response.message || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除失败:', error)
          ElMessage.error('删除失败')
        }
      }
    }

    const togglePublish = async (row) => {
      try {
        const response = await http.put(`/admin/matches/${row.id}/publish`, {
          is_published: !row.is_published
        })
        if (response.code === 200) {
          ElMessage.success(`${row.is_published ? '取消发布' : '发布'}成功`)
          row.is_published = !row.is_published
        } else {
          ElMessage.error(response.message || '操作失败')
        }
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error('操作失败')
      }
    }

    const handleImport = () => {
      if (!importForm.leagueId) {
        ElMessage.warning('请选择联赛')
        return
      }
      importLoading.value = true
      // 模拟导入过程
      setTimeout(() => {
        importLoading.value = false
        showImportDialog.value = false
        ElMessage.success('导入成功')
        fetchMatches()
      }, 2000)
    }

    const beforeUpload = (file) => {
      const isValidType = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'].includes(file.type)
      const isLt10MB = file.size / 1024 / 1024 < 10
      
      if (!isValidType) {
        ElMessage.error('只能上传 CSV、Excel 格式的文件!')
        return false
      }
      if (!isLt10MB) {
        ElMessage.error('文件大小不能超过 10MB!')
        return false
      }
      return true
    }

    const handleUploadSuccess = (response) => {
      if (response.code === 200) {
        ElMessage.success('文件上传成功')
        showImportDialog.value = false
        fetchMatches()
      } else {
        ElMessage.error(response.message || '文件上传失败')
      }
    }

    const handleUploadError = (error) => {
      console.error('文件上传失败:', error)
      ElMessage.error('文件上传失败')
    }

    const formatDateTime = (datetime) => {
      if (!datetime) return '-'
      return new Date(datetime).toLocaleString('zh-CN')
    }

    const getStatusTagType = (status) => {
      const statusMap = {
        scheduled: 'info',
        live: 'success',
        halftime: 'warning',
        finished: 'success',
        postponed: 'warning',
        cancelled: 'danger',
        abandoned: 'danger',
        suspended: 'warning'
      }
      return statusMap[status] || 'info'
    }

    const getStatusText = (status) => {
      const statusMap = {
        scheduled: '未开始',
        live: '进行中',
        halftime: '中场',
        finished: '已结束',
        postponed: '延期',
        cancelled: '取消',
        abandoned: '中止',
        suspended: '暂停'
      }
      return statusMap[status] || status
    }

    const getImportanceTagType = (importance) => {
      const importanceMap = {
        low: 'info',
        medium: '',
        high: 'warning',
        very_high: 'danger'
      }
      return importanceMap[importance] || ''
    }

    const getImportanceText = (importance) => {
      const importanceMap = {
        low: '低',
        medium: '中',
        high: '高',
        very_high: '极高'
      }
      return importanceMap[importance] || importance
    }

    const handleSizeChange = (size) => {
      pagination.size = size
      pagination.page = 1
    }

    const handleCurrentChange = (page) => {
      pagination.page = page
    }

    const isToday = (datetime) => {
      if (!datetime) return false
      const d = new Date(datetime)
      const now = new Date()
      return d.getFullYear() === now.getFullYear() &&
             d.getMonth() === now.getMonth() &&
             d.getDate() === now.getDate()
    }

    const statusDistribution = computed(() => {
      const dist = {}
      filteredMatches.value.forEach(m => {
        dist[m.status] = (dist[m.status] || 0) + 1
      })
      return Object.keys(dist).map(status => ({ status, count: dist[status] }))
    })

    const fetchCrawlerData = () => {
      ElMessage.info('爬取数据功能待实现')
    }

    // 生命周期
    onMounted(() => {
      fetchMatches()
      fetchLeagues()
    })

    return {
      loading,
      matches,
      leagues,
      pagination,
      selectedDays,
      selectedLeague,
      searchKeyword,
      showImportDialog,
      importLoading,
      importForm,
      filteredMatches,
      uploadUrl,
      uploadHeaders,
      uploadData,
      isToday,
      statusDistribution,
      fetchCrawlerData,
      handleSearch,
      handleDaysChange,
      handleLeagueChange,
      refreshData,
      handleView,
      handleEdit,
      handleDelete,
      togglePublish,
      handleImport,
      beforeUpload,
      handleUploadSuccess,
      handleUploadError,
      formatDateTime,
      getStatusTagType,
      getStatusText,
      getImportanceTagType,
      getImportanceText,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style scoped>
.jingcai-match-management {
  padding: 20px;
  background-color: var(--bg-body, #f5f7fa);
}

/* 卡片间距 */
.mb-4 {
  margin-bottom: 1rem;
}

/* 队伍样式 */
.match-teams {
  display: flex;
  align-items: center;
  gap: 10px;
}
.home-team {
  font-weight: bold;
  color: var(--primary, #8aa3ab);
}
.vs {
  color: var(--text-muted, #909399);
  font-size: 12px;
}
.away-team {
  font-weight: bold;
  color: var(--success, #8a9b8f);
}

/* 统计信息 */
.stats p {
  margin: 0.5rem 0;
  color: var(--text-primary, #303133);
}

/* 状态分布 */
.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0.5rem 0;
}

/* 分页居中 */
.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}

.upload-demo {
  width: 100%;
}
.dialog-footer {
  text-align: right;
}

/* 响应式：小屏时左右分栏变为上下堆叠 */
@media (max-width: 1199px) {
  .jingcai-match-management :deep(.el-col.lg-16),
  .jingcai-match-management :deep(.el-col.lg-8) {
    flex: 0 0 100%;
    max-width: 100%;
  }
}
</style>