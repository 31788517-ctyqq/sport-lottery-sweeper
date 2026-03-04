<template>
  <el-card class="stats-card-mobile">
    <template #header>
      <div class="card-header">
        <span>筛选统计</span>
        <el-tooltip content="显示当前筛选条件下的统计信息" placement="top">
          <el-icon><InfoFilled /></el-icon>
        </el-tooltip>
      </div>
    </template>

    <!-- 移动端垂直布局 -->
    <div class="stats-list">
      <div class="stat-item-mobile">
        <div class="stat-number">{{ totalMatches }}</div>
        <div class="stat-label">符合条件场次</div>
      </div>

      <div class="stat-item-mobile">
        <div class="stat-number">{{ filterForm.powerDiffs.length > 0 ? deltaPCount : '未设置' }}</div>
        <div class="stat-label">实力等级差 ΔP</div>
      </div>

      <div class="stat-item-mobile">
        <div class="stat-number">{{ filterForm.winPanDiffs.length > 0 ? deltaWpCount : '未设置' }}</div>
        <div class="stat-label">赢盘等级差 ΔWP</div>
      </div>

      <div class="stat-item-mobile">
        <div class="stat-number">{{ filterForm.stabilityTiers.length > 0 ? pTierCount : '未设置' }}</div>
        <div class="stat-label">一赔稳定性 P-Tier</div>
      </div>
    </div>
  </el-card>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { ElCard, ElTooltip } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'

export default defineComponent({
  name: 'StatsCardMobile',
  components: {
    ElCard,
    ElTooltip,
    InfoFilled
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
  },
  setup(props) {
    const totalMatches = computed(() => {
      return props.statistics?.filteredMatches
        ?? props.statistics?.filtered_matches
        ?? props.statistics?.total_matches
        ?? props.statistics?.totalMatches
        ?? props.statistics?.filteredMatches
        ?? 0
    })

    const deltaPCount = computed(() => {
      return props.statistics?.delta_p_count ?? props.statistics?.deltaPCount ?? 0
    })

    const deltaWpCount = computed(() => {
      return props.statistics?.delta_wp_count ?? props.statistics?.deltaWpCount ?? 0
    })

    const pTierCount = computed(() => {
      return props.statistics?.p_tier_count ?? props.statistics?.pTierCount ?? 0
    })

    return {
      totalMatches,
      deltaPCount,
      deltaWpCount,
      pTierCount
    }
  }
})
</script>

<style scoped>
.stats-card-mobile {
  margin-bottom: 16px;
  border-radius: 16px;
  background: #fbfaf8;
  box-shadow: 0 4px 12px rgba(107, 103, 99, 0.08);
  border: 1px solid #e8e6e3;
  width: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  color: #5a5a5a;
  font-size: 16px;
  padding: 4px 0;
}

.card-header .el-icon {
  color: #9fb1c4;
  font-size: 16px;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 8px 0;
}

.stat-item-mobile {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border: 1px solid #e8e6e3;
  border-radius: 12px;
  background-color: #ffffff;
  box-shadow: 0 2px 6px rgba(107, 103, 99, 0.04);
  transition: all 0.2s ease;
}

.stat-item-mobile:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(107, 103, 99, 0.08);
  border-color: #d6d2cb;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: #9fb1c4;
  text-align: center;
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #8b8680;
  font-weight: 500;
  text-align: left;
  flex: 2;
  padding-left: 12px;
}

/* 响应式调整 */
@media (max-width: 480px) {
  .stat-item-mobile {
    padding: 14px 16px;
  }
  
  .stat-number {
    font-size: 22px;
  }
  
  .stat-label {
    font-size: 13px;
  }
}

/* 暗色模式适配 */
@media (prefers-color-scheme: dark) {
  .stats-card-mobile {
    background: #2d2d2d;
    border-color: #444;
  }
  
  .card-header {
    color: #e0e0e0;
  }
  
  .stat-item-mobile {
    background-color: #363636;
    border-color: #444;
  }
  
  .stat-number {
    color: #8ab4f8;
  }
  
  .stat-label {
    color: #b0b0b0;
  }
}
</style>