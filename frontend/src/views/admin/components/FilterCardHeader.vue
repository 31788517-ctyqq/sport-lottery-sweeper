<template>
  <el-card class="filter-card">
    <template #header>
      <div class="card-header">
        <div class="header-title">
          <div class="title">三维精算筛选器</div>
          <div class="subtitle">基于 ΔP / ΔWP / P-Tier 的联动筛选</div>
        </div>
        <div class="header-actions">
          <div class="match-count">实时匹配 <span>{{ totalResults }}</span> 场</div>
          <el-button type="primary" @click="onFetchRealData" :loading="loading">获取实时数据</el-button>
          <el-button @click="onShowPLevelRules">P级规则</el-button>
          <slot name="extra-actions"></slot>
        </div>
      </div>
    </template>
  </el-card>
</template>

<script>
import { defineComponent } from 'vue';
import { ElCard, ElButton } from 'element-plus';

export default defineComponent({
  name: 'FilterCardHeader',
  components: {
    ElCard,
    ElButton
  },
  props: {
    totalResults: {
      type: Number,
      required: true
    },
    loading: {
      type: Boolean,
      required: true
    }
  },
  emits: ['fetchRealData', 'showPLevelRules'],
  setup(props, { emit }) {
    const onFetchRealData = () => {
      emit('fetchRealData');
    };

    const onShowPLevelRules = () => {
      emit('showPLevelRules');
    };

    return {
      onFetchRealData,
      onShowPLevelRules
    };
  }
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.header-title .title {
  font-size: 20px;
  font-weight: 600;
  color: #6b6763;
}

.header-title .subtitle {
  font-size: 13px;
  color: #8b8680;
  margin-top: 4px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.match-count {
  font-size: 13px;
  color: #6b6763;
  background: #f3efe8;
  padding: 6px 14px;
  border-radius: 8px;
  border: 1px solid #d6d2cb;
  font-weight: 500;
  line-height: 1.2;
}

.match-count span {
  color: #9fb1c4;
  font-weight: 700;
}

.filter-card {
  margin-bottom: 24px;
  border: 1px solid #d6d2cb;
  background: #fbfaf8;
  box-shadow: 0 14px 24px rgba(107, 103, 99, 0.12);
}
</style>
