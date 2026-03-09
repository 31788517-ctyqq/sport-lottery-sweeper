<template>
  <div class="caipiao-data-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h3>竞彩数据管理</h3>
          <div class="button-group">
            <el-button type="primary" @click="syncFromApi">同步API数据</el-button>
            <el-button type="success" @click="loadData">刷新列表</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索过滤器 -->
      <div class="filter-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input 
              v-model="filters.homeTeam" 
              placeholder="主队名称" 
              clearable
              @keyup.enter="handleFilterChange"
            />
          </el-col>
          <el-col :span="6">
            <el-input 
              v-model="filters.guestTeam" 
              placeholder="客队名称" 
              clearable
              @keyup.enter="handleFilterChange"
            />
          </el-col>
          <el-col :span="6">
            <el-input 
              v-model="filters.gameShortName" 
              placeholder="赛事名称" 
              clearable
              @keyup.enter="handleFilterChange"
            />
          </el-col>
          <el-col :span="6">
            <el-button type="primary" @click="handleFilterChange">搜索</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-col>
        </el-row>
      </div>

      <!-- 表格 -->
      <el-table 
        :data="tableData" 
        v-loading="loading"
        style="width: 100%; margin-top: 20px;"
        :default-sort="{ prop: 'matchTimeStr', order: 'ascending' }"
        height="600"
      >
        <el-table-column prop="lineId" label="线路ID" width="100" sortable />
        <el-table-column prop="homeTeam" label="主队" width="120" show-overflow-tooltip />
        <el-table-column prop="guestTeam" label="客队" width="120" show-overflow-tooltip />
        <el-table-column prop="homePower" label="主队实力" width="100" sortable />
        <el-table-column prop="guestPower" label="客队实力" width="100" sortable />
        <el-table-column prop="homeWinAward" label="主胜奖金" width="100" sortable />
        <el-table-column prop="guestWinAward" label="客胜奖金" width="100" sortable />
        <el-table-column prop="drawAward" label="平局奖金" width="100" sortable />
        <el-table-column prop="gameShortName" label="赛事" width="100" />
        <el-table-column prop="matchTimeStr" label="比赛时间" width="120" sortable />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :background="true"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="竞彩数据详情" width="80%" :before-close="closeDetailDialog">
      <div v-if="currentDetail" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="线路ID">{{ currentDetail.lineId }}</el-descriptions-item>
          <el-descriptions-item label="让球数">{{ currentDetail.rq }}</el-descriptions-item>
          <el-descriptions-item label="主队名称">{{ currentDetail.homeTeam }}</el-descriptions-item>
          <el-descriptions-item label="客队名称">{{ currentDetail.guestTeam }}</el-descriptions-item>
          <el-descriptions-item label="主队实力值">{{ currentDetail.homePower }}</el-descriptions-item>
          <el-descriptions-item label="客队实力值">{{ currentDetail.guestPower }}</el-descriptions-item>
          <el-descriptions-item label="主胜盘口">{{ currentDetail.homeWinPan }}</el-descriptions-item>
          <el-descriptions-item label="客胜盘口">{{ currentDetail.guestWinPan }}</el-descriptions-item>
          <el-descriptions-item label="主胜奖金">{{ currentDetail.homeWinAward }}</el-descriptions-item>
          <el-descriptions-item label="客胜奖金">{{ currentDetail.guestWinAward }}</el-descriptions-item>
          <el-descriptions-item label="平局奖金">{{ currentDetail.drawAward }}</el-descriptions-item>
          <el-descriptions-item label="赛事简称">{{ currentDetail.gameShortName }}</el-descriptions-item>
          <el-descriptions-item label="比赛时间">{{ currentDetail.matchTimeStr }}</el-descriptions-item>
          <el-descriptions-item label="主队特点">{{ currentDetail.homeFeature }}</el-descriptions-item>
          <el-descriptions-item label="客队特点">{{ currentDetail.guestFeature }}</el-descriptions-item>
          <el-descriptions-item label="主队进攻效率">{{ currentDetail.homeEnterEfficiency }}</el-descriptions-item>
          <el-descriptions-item label="主队防守效率">{{ currentDetail.homePreventEfficiency }}</el-descriptions-item>
          <el-descriptions-item label="客队进攻效率">{{ currentDetail.guestEnterEfficiency }}</el-descriptions-item>
          <el-descriptions-item label="客队防守效率">{{ currentDetail.guestPreventEfficiency }}</el-descriptions-item>
          <el-descriptions-item label="交锋描述" :span="2">{{ currentDetail.jiaoFenDesc }}</el-descriptions-item>
          <el-descriptions-item label="最近交战记录1" :span="2">{{ currentDetail.jiaoFenMatch1 }}</el-descriptions-item>
          <el-descriptions-item label="最近交战记录2" :span="2">{{ currentDetail.jiaoFenMatch2 }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getCaiPiaoDataList, syncCaiPiaoDataFromApi } from '@/api/caipiao-data';

export default {
  name: 'CaiPiaoDataView',
  setup() {
    // 状态变量
    const tableData = ref([]);
    const loading = ref(false);
    const currentPage = ref(1);
    const pageSize = ref(20);
    const total = ref(0);
    const detailDialogVisible = ref(false);
    const currentDetail = ref(null);
    
    // 过滤器
    const filters = reactive({
      homeTeam: '',
      guestTeam: '',
      gameShortName: ''
    });

    // 获取数据
    const fetchData = async () => {
      loading.value = true;
      try {
        const params = {
          skip: (currentPage.value - 1) * pageSize.value,
          limit: pageSize.value,
          home_team: filters.homeTeam || undefined,
          guest_team: filters.guestTeam || undefined,
          game_short_name: filters.gameShortName || undefined
        };
        
        const response = await getCaiPiaoDataList(params);
        tableData.value = response.data;
        total.value = response.total || response.length;
      } catch (error) {
        console.error('获取竞彩数据失败:', error);
        ElMessage.error('获取竞彩数据失败');
      } finally {
        loading.value = false;
      }
    };

    // 同步API数据
    const syncFromApi = async () => {
      try {
        ElMessageBox.confirm(
          '确定要从API同步最新数据吗？这可能会覆盖现有数据。',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).then(async () => {
          loading.value = true;
          const response = await syncCaiPiaoDataFromApi({ date_time: "26011" });
          ElMessage.success(`同步成功，新增 ${response.count} 条数据`);
          await fetchData();
        });
      } catch (error) {
        console.error('同步竞彩数据失败:', error);
        ElMessage.error('同步竞彩数据失败');
      } finally {
        loading.value = false;
      }
    };

    // 事件处理
    const handleSizeChange = (size) => {
      pageSize.value = size;
      fetchData();
    };

    const handleCurrentChange = (page) => {
      currentPage.value = page;
      fetchData();
    };

    const handleFilterChange = () => {
      currentPage.value = 1; // 重置到第一页
      fetchData();
    };

    const resetFilters = () => {
      filters.homeTeam = '';
      filters.guestTeam = '';
      filters.gameShortName = '';
      currentPage.value = 1;
      fetchData();
    };

    // 详情操作
    const viewDetail = (row) => {
      currentDetail.value = row;
      detailDialogVisible.value = true;
    };

    const closeDetailDialog = () => {
      detailDialogVisible.value = false;
      currentDetail.value = null;
    };

    // 初始化
    onMounted(() => {
      fetchData();
    });

    return {
      tableData,
      loading,
      currentPage,
      pageSize,
      total,
      detailDialogVisible,
      currentDetail,
      filters,
      loadData: fetchData,
      syncFromApi,
      handleSizeChange,
      handleCurrentChange,
      handleFilterChange,
      resetFilters,
      viewDetail,
      closeDetailDialog
    };
  }
};
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.button-group {
  display: flex;
  gap: 10px;
}

.filter-section {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.detail-content {
  max-height: 60vh;
  overflow-y: auto;
}
</style>