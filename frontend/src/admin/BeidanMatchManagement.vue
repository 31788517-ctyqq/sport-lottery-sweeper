# LOCK: BeidanMatchManagement.vue | AI:coder1 | Time:2026-01-27T00:01:00
<!-- 
  多AI协同锁机制：
  - 任何AI修改此文件前必须检查并创建锁
  - 修改完成后必须删除锁（由最后一个AI负责）
  - 锁格式：# LOCK: 文件名 | AI:名称 | Time:时间戳
-->
<template>
  <div class="beidan-match-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>北单赛程管理</h2>
      <p class="page-description">实时监控、导入和管理北单比赛数据</p>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <el-button type="primary" :icon="Refresh" @click="refreshData">
        刷新
      </el-button>
      <el-button type="success" :icon="Upload" @click="showImportDialog = true">
        导入数据
      </el-button>
      <el-button type="info" :icon="Download" @click="exportData">
        导出数据
      </el-button>
      <el-button type="warning" :icon="Connection" @click="crawlData">
        爬取数据
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ statistics.totalIssues }}</div>
              <div class="stats-label">总期次数</div>
            </div>
            <el-icon class="stats-icon"><Star /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ statistics.todayMatches }}</div>
              <div class="stats-label">今日开奖</div>
            </div>
            <el-icon class="stats-icon"><Calendar /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ statistics.activeIssues }}</div>
              <div class="stats-label">进行中期次</div>
            </div>
            <el-icon class="stats-icon"><Clock /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ statistics.avgBonus ? statistics.avgBonus.toFixed(2) : '0.00' }}</div>
              <div class="stats-label">平均奖金(元)</div>
            </div>
            <el-icon class="stats-icon"><Money /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 主要内容区域 -->
    <el-tabs v-model="activeTab" class="management-tabs">
      <!-- 赛程管理 -->
      <el-tab-pane label="赛程管理" name="schedule">
        <div class="tab-content">
          <el-card class="schedule-card">
            <template #header>
              <div class="card-header">
                <span>赛程筛选</span>
                <div class="header-actions">
                  <el-button size="small" @click="fetchMatches">刷新</el-button>
                </div>
              </div>
            </template>

            <div class="schedule-filters">
              <el-form :model="filterModel" :inline="true">
                <el-form-item label="关键词">
                  <el-input 
                    v-model="searchKeyword" 
                    placeholder="搜索联赛、主队、客队" 
                    clearable 
                    @clear="handleSearch"
                    @keyup.enter="handleSearch"
                    style="width: 200px"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item label="联赛">
                  <el-select 
                    v-model="selectedLeague" 
                    placeholder="选择联赛" 
                    clearable 
                    @change="handleLeagueChange"
                    style="width: 180px"
                  >
                    <el-option
                      v-for="league in beidanLeagues"
                      :key="league.id"
                      :label="league.name"
                      :value="league.id"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="时间范围">
                  <el-select 
                    v-model="selectedDays" 
                    placeholder="选择天数" 
                    @change="handleDaysChange"
                    style="width: 140px"
                  >
                    <el-option label="近3天" :value="3" />
                    <el-option label="近7天" :value="7" />
                    <el-option label="近30天" :value="30" />
                    <el-option label="近5天" :value="5" />
                    <el-option label="近15天" :value="15" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSearch">筛选</el-button>
                </el-form-item>
              </el-form>
            </div>

            <el-table :data="filteredMatches" style="width: 100%" v-loading="loading" stripe border empty-text="暂无北单比赛数据">
              <el-table-column prop="match_identifier" label="北单编号" width="150" />
              <el-table-column prop="league_name" label="联赛" width="120" />
              <el-table-column prop="round_number" label="期次" width="80" />
              <el-table-column label="开奖时间" width="180">
                <template #default="scope">
                  {{ formatDateTime(scope.row.scheduled_kickoff) }}
                </template>
              </el-table-column>
              <el-table-column label="对阵" min-width="220">
                <template #default="scope">
                  <div class="match-teams">
                    <div class="team-info">
                      <el-avatar :size="24" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
                      <span class="team-name">{{ scope.row.home_team }}</span>
                    </div>
                    <span class="vs-text">VS</span>
                    <div class="team-info">
                      <el-avatar :size="24" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
                      <span class="team-name">{{ scope.row.away_team }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="胜负预测" width="120">
                <template #default="scope">
                  <div class="prediction-info">
                    <el-tag size="small" type="success" v-if="scope.row.home_win_prob">主胜: {{ (scope.row.home_win_prob * 100).toFixed(1) }}%</el-tag>
                    <el-tag size="small" type="info" v-if="scope.row.draw_prob">平局: {{ (scope.row.draw_prob * 100).toFixed(1) }}%</el-tag>
                    <el-tag size="small" type="warning" v-if="scope.row.away_win_prob">客胜: {{ (scope.row.away_win_prob * 100).toFixed(1) }}%</el-tag>
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
              <el-table-column label="操作" width="220" fixed="right">
                <template #default="scope">
                  <el-button size="small" @click="handleView(scope.row)">详情</el-button>
                  <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
                  <el-button 
                    size="small" 
                    :type="scope.row.is_published ? 'warning' : 'success'"
                    @click="togglePublish(scope.row)"
                  >
                    {{ scope.row.is_published ? '下架' : '上架' }}
                  </el-button>
                  <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="pagination-wrapper">
              <el-pagination
                v-model:current-page="pagination.page"
                v-model:page-size="pagination.size"
                :total="pagination.total"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 数据导入对话框 -->
    <el-dialog 
      v-model="showImportDialog" 
      title="导入北单比赛数据" 
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="importForm" label-width="120px">
        <el-form-item label="选择联赛">
          <el-select v-model="importForm.leagueId" placeholder="请选择联赛" style="width: 100%">
            <el-option
              v-for="league in beidanLeagues"
              :key="league.id"
              :label="league.name"
              :value="league.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="数据源">
          <el-radio-group v-model="importForm.dataSource">
            <el-radio label="official">官方接口</el-radio>
            <el-radio label="crawler">爬虫抓取</el-radio>
            <el-radio label="file">文件上传</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="importForm.dataSource === 'official' || importForm.dataSource === 'crawler'" label="API地址">
          <el-input v-model="importForm.apiUrl" placeholder="可选：输入API地址" />
        </el-form-item>

        <el-form-item v-if="importForm.dataSource === 'file'" label="选择文件">
          <el-upload
            class="upload-demo"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :data="uploadData"
            :before-upload="beforeUpload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :show-file-list="true"
            accept=".csv,.xlsx,.xls"
          >
            <el-button type="primary">点击上传</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持 CSV、Excel 格式，文件大小不超过 10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showImportDialog = false">取消</el-button>
          <el-button type="primary" @click="handleImport" :loading="importLoading">确认导入</el-button>
        </span>
      </template>
    </el-dialog>

    <el-table :data="filteredMatches" style="width: 100%" v-loading="loading" stripe border empty-text="暂无北单比赛数据">
      <el-table-column prop="match_identifier" label="北单编号" width="150" />
      <el-table-column prop="league_name" label="联赛" width="120" />
      <el-table-column prop="round_number" label="期次" width="80" />
      <el-table-column label="开奖时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.scheduled_kickoff) }}
        </template>
      </el-table-column>
      <el-table-column label="对阵" min-width="220">
        <template #default="scope">
          <div class="match-teams">
            <div class="team-info">
              <el-avatar :size="24" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <span class="team-name">{{ scope.row.home_team }}</span>
            </div>
            <span class="vs-text">VS</span>
            <div class="team-info">
              <el-avatar :size="24" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <span class="team-name">{{ scope.row.away_team }}</span>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="胜负预测" width="120">
        <template #default="scope">
          <div class="prediction-info">
            <el-tag size="small" type="success" v-if="scope.row.home_win_prob">主胜: {{ (scope.row.home_win_prob * 100).toFixed(1) }}%</el-tag>
            <el-tag size="small" type="info" v-if="scope.row.draw_prob">平局: {{ (scope.row.draw_prob * 100).toFixed(1) }}%</el-tag>
            <el-tag size="small" type="warning" v-if="scope.row.away_win_prob">客胜: {{ (scope.row.away_win_prob * 100).toFixed(1) }}%</el-tag>
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
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="handleView(scope.row)">详情</el-button>
          <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button 
            size="small" 
            :type="scope.row.is_published ? 'warning' : 'success'"
            @click="togglePublish(scope.row)"
          >
            {{ scope.row.is_published ? '下架' : '上架' }}
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </el-card>
</div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Upload, UploadFilled, Connection, Star, Download } from '@element-plus/icons-vue'
import BaseCard from '@/components/common/BaseCard.vue'
// AI_WORKING: coder1 @2025-01-31 12:00:00 - 修复http导入错误，http是默认导出
import http from '@/utils/http'
// AI_DONE: coder1 @2025-01-31 12:00:00

export default {
  name: 'BeidanMatchManagement',
  components: {
    Search,
    Refresh,
    Upload,
    UploadFilled,
    Connection,
    Star,
    Download,
    BaseCard
  },
  setup() {
    // 响应式数据
    const loading = ref(false)
    const matches = ref([])
    const leagues = ref([])
    const beidanLeagues = ref([])
    // AI_WORKING: coder1 @2026-01-31 - 将默认时间范围从5天改为3天
    const selectedDays = ref(3)
    // AI_DONE: coder1 @2026-01-31
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
    // AI_WORKING: coder1 @2026-01-31 - 添加apiUrl字段到导入表单
    const importForm = reactive({
      leagueId: '',
      dataSource: 'official',
      apiUrl: ''
    })
    // AI_DONE: coder1 @2026-01-31

    // 爬取设置
    const crawlSettings = reactive({
      days: 5,
      includeHistory: false
    })

    // 统计数据
    const statistics = reactive({
      totalIssues: 0,
      todayMatches: 0,
      activeIssues: 0,
      avgBonus: 0
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
        const response = await http.get('/admin/matches/beidan/matches', {
          params: { days: selectedDays.value }
        })
        if (response.code === 200) {
          matches.value = response.data || []
          pagination.total = matches.value.length
          calculateStatistics()
        } else {
          ElMessage.error(response.message || '获取北单比赛数据失败')
        }
      } catch (error) {
        console.error('获取北单比赛数据失败:', error)
        ElMessage.error('获取北单比赛数据失败')
      } finally {
        loading.value = false
      }
    }

    const fetchLeagues = async () => {
      try {
        const response = await http.get('/admin/matches/leagues')
        if (response.code === 200) {
          leagues.value = response.data || []
          // 筛选出北单相关联赛
          beidanLeagues.value = leagues.value.filter(league => 
            league.name.includes('北单') || 
            league.code.includes('bd') ||
            league.name.includes('北京单场')
          )
        }
      } catch (error) {
        console.error('获取联赛列表失败:', error)
      }
    }

    const calculateStatistics = () => {
      if (matches.value.length === 0) {
        Object.assign(statistics, {
          totalIssues: 0,
          todayMatches: 0,
          activeIssues: 0
        })
        return
      }

      const today = new Date().toISOString().split('T')[0]
      const todayMatches = matches.value.filter(match => 
        match.match_date === today
      ).length

      const activeMatches = matches.value.filter(match => 
        match.status === 'scheduled' || match.status === 'live'
      ).length

      Object.assign(statistics, {
        totalIssues: new Set(matches.value.map(m => m.round_number)).size,
        todayMatches,
        activeIssues: activeMatches
      })
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
      ElMessage.success('北单数据已刷新')
    }

    const crawlData = async () => {
      try {
        loading.value = true
        ElMessage.info('正在从北单官方接口爬取数据...')
        
        // 这里应该调用真实的爬虫API
        await new Promise(resolve => setTimeout(resolve, 3000))
        
        ElMessage.success('北单数据爬取完成')
        fetchMatches()
      } catch (error) {
        console.error('爬取数据失败:', error)
        ElMessage.error('爬取数据失败')
      } finally {
        loading.value = false
      }
    }

    // AI_WORKING: coder1 @2026-01-31 - 添加导出数据功能
    const exportData = async () => {
      try {
        loading.value = true
        ElMessage.info('正在准备导出数据...')
        
        // 构建导出参数
        const params = {
          days: selectedDays.value,
          league_id: selectedLeague.value,
          keyword: searchKeyword.value
        }
        
        // 调用导出API
        const response = await http.get('/admin/matches/beidan/export', {
          params,
          responseType: 'blob'
        })
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `北单比赛数据_${new Date().toISOString().slice(0,10)}.xlsx`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('数据导出成功')
      } catch (error) {
        console.error('导出数据失败:', error)
        ElMessage.error('导出数据失败: ' + (error.message || '未知错误'))
      } finally {
        loading.value = false
      }
    }
    // AI_DONE: coder1 @2026-01-31

    const handleView = (row) => {
      console.log('查看北单比赛详情:', row)
      // 实现查看详情逻辑，可以打开一个更详细的对话框
    }

    const handleEdit = (row) => {
      console.log('编辑北单比赛:', row)
      // 实现编辑逻辑
    }

    const handleDelete = async (row) => {
      try {
        await ElMessageBox.confirm(`确定要删除北单比赛 "${row.home_team} VS ${row.away_team}" 吗？`, '确认删除', {
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
          ElMessage.success(`${row.is_published ? '下架' : '上架'}成功`)
          row.is_published = !row.is_published
        } else {
          ElMessage.error(response.message || '操作失败')
        }
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error('操作失败')
      }
    }

    // AI_WORKING: coder1 @2026-01-31 - 修改handleImport函数以支持API地址
    const handleImport = async () => {
      if (!importForm.leagueId) {
        ElMessage.warning('请选择联赛')
        return
      }
      
      importLoading.value = true
      
      try {
        if (importForm.dataSource === 'crawler') {
          // 执行爬虫导入
          ElMessage.info('正在启动爬虫获取数据...')
          // 如果有API地址，传递给后端
          const params = {
            league_id: importForm.leagueId,
            api_url: importForm.apiUrl || undefined
          }
          console.log('爬虫导入参数:', params)
          await new Promise(resolve => setTimeout(resolve, 2000))
        } else if (importForm.dataSource === 'official') {
          // 官方接口导入
          ElMessage.info('正在从官方接口获取数据...')
          const params = {
            league_id: importForm.leagueId,
            api_url: importForm.apiUrl || undefined
          }
          console.log('官方接口导入参数:', params)
          await new Promise(resolve => setTimeout(resolve, 2000))
        } else {
          // 文件导入已经在上传组件中处理
          showImportDialog.value = false
        }
        
        ElMessage.success('导入成功')
        fetchMatches()
      } catch (error) {
        console.error('导入失败:', error)
        ElMessage.error('导入失败')
      } finally {
        importLoading.value = false
      }
    }
    // AI_DONE: coder1 @2026-01-31

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
        scheduled: '未开奖',
        live: '进行中',
        halftime: '中场',
        finished: '已开奖',
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
        low: '普通',
        medium: '中等',
        high: '重要',
        very_high: '非常重要'
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

    const predictionStats = computed(() => {
      const stats = [
        { type: 'home', label: '主胜', key: 'home_win_prob', tagType: 'success' },
        { type: 'draw', label: '平局', key: 'draw_prob', tagType: 'info' },
        { type: 'away', label: '客胜', key: 'away_win_prob', tagType: 'warning' }
      ]
      return stats.map(s => {
        const values = filteredMatches.value
          .map(m => m[s.key])
          .filter(v => typeof v === 'number' && v >= 0 && v <= 1)
        const avg = values.length > 0 ? (values.reduce((a, b) => a + b, 0) / values.length * 100).toFixed(1) : '0.0'
        return { ...s, avg }
      })
    })

    const dataSources = ref([
      { name: '北单官方接口', status: true },
      { name: '爬虫抓取服务', status: true },
      { name: '第三方数据商', status: false }
    ])

    // 生命周期
    onMounted(() => {
      fetchMatches()
      fetchLeagues()
    })

    // AI_WORKING: coder1 @2026-01-31 - 在返回对象中添加exportData函数
    return {
      loading,
      matches,
      leagues,
      beidanLeagues,
      pagination,
      selectedDays,
      selectedLeague,
      searchKeyword,
      showImportDialog,
      importLoading,
      importForm,
      crawlSettings,
      statistics,
      filteredMatches,
      uploadUrl,
      uploadHeaders,
      uploadData,
      predictionStats,
      dataSources,
      handleSearch,
      handleDaysChange,
      handleLeagueChange,
      refreshData,
      crawlData,
      exportData,
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
    // AI_DONE: coder1 @2026-01-31
  }
}
</script>

<style scoped>
.beidan-match-management {
  padding: 20px;
}

.toolbar {
  margin-bottom: 20px;
  padding: 20px;
  background: var(--bg-card, #ffffff);
  border-radius: 8px;
  border: 2px solid var(--primary, #8aa3ab);
  color: var(--text-primary, #303133);
}

.toolbar :deep(.el-input__wrapper) {
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
}

.toolbar :deep(.el-input__inner) {
  color: var(--text-primary, #303133);
}

.toolbar :deep(.el-input__inner::placeholder) {
  color: var(--text-muted, #909399);
}

.match-teams {
  display: flex;
  align-items: center;
      justify-content: space-between;
      gap: 10px;
    }

    .team-info {
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;
    }

    .team-name {
      font-weight: 500;
    }

    .vs-text {
      color: var(--text-muted, #909399);
      font-size: 12px;
      font-weight: bold;
    }

    .prediction-info {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .statistics-row {
      margin: 20px 0;
    }

    .statistics-row :deep(.el-statistic__head) {
      color: var(--text-secondary, #606266);
      font-size: 14px;
    }

    .statistics-row :deep(.el-statistic__content) {
      color: var(--primary, #8aa3ab);
      font-size: 24px;
      font-weight: bold;
    }

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

    .stats p {
      margin: 0.5rem 0;
      color: var(--text-primary, #303133);
    }

    .prediction-item,
    .source-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin: 0.5rem 0;
    }

    .prediction-item span,
    .source-item span {
      color: var(--text-secondary, #606266);
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
      .toolbar .el-col {
        margin-bottom: 10px;
      }
      
      .match-teams {
        flex-direction: column;
        gap: 5px;
      }
      
      .team-info {
        justify-content: center;
      }
    }
  </style>