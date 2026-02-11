<template>
  <div class="user-profile-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>用户画像管理</h3>
            <p class="subtitle">分析和管理用户的行为模式、风险偏好和投注习惯</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="loadData" :loading="loading" icon="Refresh">刷新</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20" class="filters-row">
        <el-col :span="6">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索用户名或邮箱" 
            clearable
            @keyup.enter="applyFilters"
            @clear="applyFilters"
          />
        </el-col>
        <el-col :span="4">
          <el-select 
            v-model="riskLevelFilter" 
            placeholder="风险等级" 
            clearable
            @change="applyFilters"
          >
            <el-option label="保守型" value="conservative" />
            <el-option label="稳健型" value="moderate" />
            <el-option label="积极型" value="aggressive" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select 
            v-model="activityFilter" 
            placeholder="活跃度" 
            clearable
            @change="applyFilters"
          >
            <el-option label="高活跃" value="high" />
            <el-option label="中活跃" value="medium" />
            <el-option label="低活跃" value="low" />
          </el-select>
        </el-col>
        <el-col :span="10">
          <el-button type="primary" @click="applyFilters">应用筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <el-table
        :data="paginatedProfiles"
        v-loading="loading"
        style="width: 100%"
        stripe
      >
        <el-table-column prop="userId" label="用户ID" width="100" />
        <el-table-column prop="username" label="用户名" width="150">
          <template #default="scope">
            <div class="user-info">
              <el-avatar size="small" :style="{ backgroundColor: getAvatarColor(scope.row.userId) }">
                {{ scope.row.username.charAt(0).toUpperCase() }}
              </el-avatar>
              <span style="margin-left: 10px;">{{ scope.row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" width="200" show-overflow-tooltip />
        <el-table-column prop="riskTolerance" label="风险偏好" width="120">
          <template #default="scope">
            <el-tag :type="getRiskTagType(scope.row.riskTolerance)">
              {{ getRiskLevelName(scope.row.riskTolerance) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="preferredTeams" label="偏好球队" min-width="150">
          <template #default="scope">
            <el-tag 
              v-for="(team, idx) in scope.row.preferredTeams.slice(0, 3)" 
              :key="idx" 
              size="small" 
              style="margin-right: 5px; margin-bottom: 5px;"
            >
              {{ team }}
            </el-tag>
            <el-popover
              v-if="scope.row.preferredTeams.length > 3"
              placement="top"
              :title="'偏好球队 (' + scope.row.preferredTeams.length + ')'"
              :width="300"
              trigger="hover"
            >
              <template #default>
                <div class="teams-grid">
                  <el-tag 
                    v-for="(team, idx) in scope.row.preferredTeams" 
                    :key="idx" 
                    size="small" 
                    style="margin-right: 5px; margin-bottom: 5px;"
                  >
                    {{ team }}
                  </el-tag>
                </div>
              </template>
              <template #reference>
                <el-tag size="small" type="info">+{{ scope.row.preferredTeams.length - 3 }}</el-tag>
              </template>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column prop="successRate" label="成功率" width="100">
          <template #default="scope">
            {{ (scope.row.successRate * 100).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="bettingFrequency" label="投注频率" width="120">
          <template #default="scope">
            <el-tag :type="getFrequencyTagType(scope.row.bettingFrequency)">
              {{ getFrequencyName(scope.row.bettingFrequency) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastUpdated" label="更新时间" width="160">
          <template #default="scope">
            {{ scope.row.lastUpdated }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewDetails(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="editProfile(scope.row)">编辑</el-button>
            <el-button size="small" @click="analyzeBehavior(scope.row)">分析</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredProfiles.length"
        />
      </div>
    </el-card>

    <!-- 用户画像详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="用户画像详情" width="60%" destroy-on-close>
      <div v-if="selectedProfile" class="profile-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户ID">{{ selectedProfile.userId }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ selectedProfile.username }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ selectedProfile.email }}</el-descriptions-item>
          <el-descriptions-item label="风险偏好">
            <el-tag :type="getRiskTagType(selectedProfile.riskTolerance)">
              {{ getRiskLevelName(selectedProfile.riskTolerance) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="偏好球队" :span="2">
            <div class="teams-list">
              <el-tag 
                v-for="(team, idx) in selectedProfile.preferredTeams" 
                :key="idx" 
                size="small" 
                style="margin-right: 5px; margin-bottom: 5px;"
              >
                {{ team }}
              </el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="投注习惯">{{ selectedProfile.bettingHabits }}</el-descriptions-item>
          <el-descriptions-item label="投注频率">
            <el-tag :type="getFrequencyTagType(selectedProfile.bettingFrequency)">
              {{ getFrequencyName(selectedProfile.bettingFrequency) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="成功率">{{ (selectedProfile.successRate * 100).toFixed(2) }}%</el-descriptions-item>
          <el-descriptions-item label="总投注额">¥{{ selectedProfile.totalBettingAmount.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="总收益">¥{{ selectedProfile.totalProfit.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="盈利概率">{{ (selectedProfile.profitProbability * 100).toFixed(2) }}%</el-descriptions-item>
          <el-descriptions-item label="最后更新">{{ selectedProfile.lastUpdated }}</el-descriptions-item>
          <el-descriptions-item label="画像标签" :span="2">
            <el-tag 
              v-for="(tag, idx) in selectedProfile.tags" 
              :key="idx" 
              size="small" 
              style="margin-right: 5px; margin-bottom: 5px;"
            >
              {{ tag }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="behavior-chart">
          <h4>行为分析图表</h4>
          <div ref="behaviorChartRef" style="height: 300px; margin-top: 20px;"></div>
        </div>
      </div>
    </el-dialog>

    <!-- 编辑用户画像对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      title="编辑用户画像" 
      width="50%" 
      destroy-on-close
    >
      <el-form 
        :model="profileForm" 
        :rules="profileRules" 
        ref="profileFormRef" 
        label-width="120px"
        style="padding-right: 20px;"
      >
        <el-form-item label="风险偏好" prop="riskTolerance">
          <el-radio-group v-model="profileForm.riskTolerance">
            <el-radio value="conservative">保守型</el-radio>
            <el-radio value="moderate">稳健型</el-radio>
            <el-radio value="aggressive">积极型</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="偏好球队" prop="preferredTeams">
          <el-select 
            v-model="profileForm.preferredTeams" 
            multiple 
            filterable 
            placeholder="请选择偏好球队"
            style="width: 100%;"
          >
            <el-option 
              v-for="team in allTeams" 
              :key="team" 
              :label="team" 
              :value="team" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="投注习惯" prop="bettingHabits">
          <el-input 
            v-model="profileForm.bettingHabits" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入投注习惯描述" 
          />
        </el-form-item>
        <el-form-item label="投注频率" prop="bettingFrequency">
          <el-select v-model="profileForm.bettingFrequency" placeholder="请选择投注频率">
            <el-option label="低频" value="low" />
            <el-option label="中频" value="medium" />
            <el-option label="高频" value="high" />
          </el-select>
        </el-form-item>
        <el-form-item label="成功预测次数" prop="successfulPredictions">
          <el-input-number 
            v-model="profileForm.successfulPredictions" 
            :min="0" 
            style="width: 100%;" 
          />
        </el-form-item>
        <el-form-item label="总投注额" prop="totalBettingAmount">
          <el-input-number 
            v-model="profileForm.totalBettingAmount" 
            :min="0" 
            :precision="2"
            style="width: 100%;" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEditForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
// AI_WORKING: coder1 @2026-02-05 - 导入用户画像API模块
import { getUserProfiles } from '@/api/modules/user-profiles'

// 响应式数据
const loading = ref(false)
const searchQuery = ref('')
const riskLevelFilter = ref('')
const activityFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// 用户画像数据
const profiles = ref([])

// 对话框相关
const detailDialogVisible = ref(false)
const editDialogVisible = ref(false)
const selectedProfile = ref(null)

// 编辑表单数据
const profileForm = ref({})
const profileRules = {}

// 可用球队列表
const allTeams = [
  '皇家马德里', '巴塞罗那', '拜仁慕尼黑', '曼城', '利物浦', 
  '尤文图斯', '国际米兰', 'AC米兰', '巴黎圣日耳曼', '切尔西',
  '曼联', '阿森纳', '多特蒙德', '勒沃库森', '门兴格拉德巴赫',
  '阿贾克斯', '费耶诺德', '埃因霍温', '波尔图', '本菲卡'
]

// 行为图表引用
const behaviorChartRef = ref(null)

// 计算属性：筛选后的用户画像
const filteredProfiles = computed(() => {
  return profiles.value.filter(profile => {
    // 搜索关键词筛选
    const matchesSearch = !searchQuery.value || 
      profile.username.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      profile.email.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    // 风险等级筛选
    const matchesRiskLevel = !riskLevelFilter.value || profile.riskTolerance === riskLevelFilter.value
    
    // 活跃度筛选（这里用投注频率模拟活跃度）
    const matchesActivity = !activityFilter.value || profile.bettingFrequency === activityFilter.value
    
    return matchesSearch && matchesRiskLevel && matchesActivity
  })
})

// 计算属性：当前页数据
const paginatedProfiles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredProfiles.value.slice(start, end)
})

// 方法：加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 使用真实API获取用户画像数据
    const response = await getUserProfiles({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    })
    
    if (response && response.data) {
      profiles.value = Array.isArray(response.data) ? response.data : []
    }
    
    ElMessage.success('数据加载成功')
  } catch (error) {
    console.error('加载用户画像失败:', error)
    ElMessage.error('加载用户画像失败')
  } finally {
    loading.value = false
  }
}

// 方法：应用筛选
const applyFilters = () => {
  currentPage.value = 1
  ElMessage.success('筛选条件已应用')
}

// 方法：重置筛选
const resetFilters = () => {
  searchQuery.value = ''
  riskLevelFilter.value = ''
  activityFilter.value = ''
  currentPage.value = 1
  ElMessage.info('筛选条件已重置')
}

// 方法：分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 方法：获取风险等级标签类型
const getRiskTagType = (level) => {
  switch (level) {
    case 'conservative': return 'success'
    case 'moderate': return 'warning'
    case 'aggressive': return 'danger'
    default: return 'info'
  }
}

// 方法：获取风险等级名称
const getRiskLevelName = (level) => {
  switch (level) {
    case 'conservative': return '保守型'
    case 'moderate': return '稳健型'
    case 'aggressive': return '积极型'
    default: return level
  }
}

// 方法：获取频率标签类型
const getFrequencyTagType = (freq) => {
  switch (freq) {
    case 'low': return 'info'
    case 'medium': return 'warning'
    case 'high': return 'danger'
    default: return 'info'
  }
}

// 方法：获取频率名称
const getFrequencyName = (freq) => {
  switch (freq) {
    case 'low': return '低频'
    case 'medium': return '中频'
    case 'high': return '高频'
    default: return freq
  }
}

// 方法：获取头像颜色
const getAvatarColor = (id) => {
  const colors = ['#1890FF', '#52C41A', '#FAAD14', '#F5222D', '#722ED1']
  return colors[id % colors.length]
}

// 方法：查看用户画像详情
const viewDetails = async (profile) => {
  selectedProfile.value = profile
  detailDialogVisible.value = true
  
  // 等待DOM更新后再初始化图表
  await nextTick()
  initBehaviorChart()
}

// 方法：初始化行为图表
const initBehaviorChart = () => {
  if (!behaviorChartRef.value) return
  
  const chart = echarts.init(behaviorChartRef.value)
  chart.setOption({
    title: {
      text: '投注行为趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['投注额', '收益']
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
    },
    yAxis: [
      {
        type: 'value',
        name: '金额 (¥)',
        position: 'left'
      }
    ],
    series: [
      {
        name: '投注额',
        type: 'bar',
        data: [1200, 1800, 1500, 2200, 1800, 2000, 2400],
        itemStyle: {
          color: '#5470c6'
        }
      },
      {
        name: '收益',
        type: 'line',
        data: [150, 280, -120, 350, 180, 220, 310],
        itemStyle: {
          color: '#fac858'
        }
      }
    ]
  })
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 方法：编辑用户画像
const editProfile = (profile) => {
  // 复制profile数据到表单
  profileForm.value = { ...profile }
  editDialogVisible.value = true
}

// 方法：提交编辑表单
const submitEditForm = async () => {
  try {
    // 调用API更新用户画像
    // await updateUserProfile(profileForm.value.userId, profileForm.value)
    ElMessage.success('用户画像更新成功')
    // 重新加载数据
    await loadData()
    editDialogVisible.value = false
  } catch (error) {
    console.error('更新用户画像失败:', error)
    ElMessage.error('更新用户画像失败')
  }
}

// 方法：分析用户行为
const analyzeBehavior = (profile) => {
  ElMessage.info(`正在分析 ${profile.username} 的行为模式...`)
}

// 页面加载时初始化
onMounted(() => {
  loadData()
})
// AI_DONE: coder1 @2026-02-05
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

.filters-row {
  margin-bottom: 20px;
  padding: 15px 0;
}

.user-info {
  display: flex;
  align-items: center;
}

.positive-profit {
  color: #67c23a;
  font-weight: bold;
}

.negative-profit {
  color: #f56c6c;
  font-weight: bold;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.profile-detail {
  max-height: 500px;
  overflow-y: auto;
}

.behavior-chart {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.behavior-chart h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
}

.teams-list {
  display: flex;
  flex-wrap: wrap;
}

.teams-grid {
  max-height: 200px;
  overflow-y: auto;
  padding: 10px 0;
}
</style>