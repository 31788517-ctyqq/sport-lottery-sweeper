<template>
  <el-card class="stats-card">
    <template #header>
      <div class="card-header">
        <span>筛选统计</span>
      </div>
    </template>

    <el-row :gutter="20">
      <el-col :span="6">
        <div class="stat-item">
          <div class="stat-number">{{ statistics.total_matches }}</div>
          <div class="stat-label">符合条件场次</div>
        </div>
      </el-col>

      <el-col :span="6">
        <div class="stat-item">
          <div class="stat-number">{{ filterForm.powerDiffs.length > 0 ? statistics.delta_p_count || 0 : '未设置' }}</div>
          <div class="stat-label">实力等级差 ΔP</div>
        </div>
      </el-col>

      <el-col :span="6">
        <div class="stat-item">
          <div class="stat-number">{{ filterForm.winPanDiffs.length > 0 ? statistics.delta_wp_count || 0 : '未设置' }}</div>
          <div class="stat-label">赢盘等级差 ΔWP</div>
        </div>
      </el-col>

      <el-col :span="6">
        <div class="stat-item">
          <div class="stat-number">{{ filterForm.stabilityTiers.length > 0 ? statistics.p_tier_count || 0 : '未设置' }}</div>
          <div class="stat-label">一赔稳定性 P-Tier</div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script>
import { defineComponent } from 'vue';
import { ElCard, ElRow, ElCol } from 'element-plus';

export default defineComponent({
  name: 'StatsCard',
  components: {
    ElCard,
    ElRow,
    ElCol
  },
  props: {
    statistics: {
      type: Object,
      required: true
    },
    filterForm: {
      type: Object,
      required: true
    }
  }
});
</script>

<style scoped>
.stats-card {
  margin-bottom: 24px;
  border: 1px solid #d6d2cb;
  background: #fbfaf8;
  box-shadow: 0 14px 24px rgba(107, 103, 99, 0.12);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  display: block;
}

.stat-item {
  text-align: center;
  padding: 20px;
  border: 1px solid #d6d2cb;
  border-radius: 10px;
  background-color: #fdfcfb;
  box-shadow: 0 10px 18px rgba(107, 103, 99, 0.08);
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #9fb1c4;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #8b8680;
  font-weight: 500;
}
</style>