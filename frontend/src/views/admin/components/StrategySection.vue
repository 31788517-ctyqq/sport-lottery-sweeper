<template>
  <el-card class="strategy-card">
    <div class="strategy-bar">
      <div class="strategy-select">
        <span class="strategy-label">策略筛选</span>
        <el-select
          v-model="selectedStrategyName"
          placeholder="选择已保存的策略"
          clearable
          filterable
          style="width: 260px"
          @change="onHandleSelectStrategy"
        >
          <el-option
            v-for="name in strategyOptions"
            :key="name"
            :label="name"
            :value="name"
          />
        </el-select>
        <el-button size="small" @click="onLoadStrategyOptions">刷新</el-button>
      </div>
      <div class="strategy-detail" v-if="strategyDetailItems.length">
        <div class="detail-item" v-for="item in strategyDetailItems" :key="item.label">
          <span class="detail-label">{{ item.label }}:</span>
          <span class="detail-value">{{ item.value }}</span>
        </div>
      </div>
      <div class="strategy-empty" v-else>
        选择策略后将显示详情
      </div>
    </div>
    <div class="strategy-list" v-if="strategyOptions.length">
      <div class="strategy-list-title">策略列表</div>
      <div class="strategy-grid">
        <div
          class="strategy-item"
          v-for="name in strategyOptions"
          :key="name"
          :class="{ active: name === selectedStrategyName }"
          @click="onHandleSelectStrategy(name)"
        >
          <div class="strategy-item-header">
            <span class="strategy-item-name">{{ name }}</span>
            <span class="strategy-item-tag" v-if="name === selectedStrategyName">已选</span>
          </div>
        </div>
      </div>
    </div>
    <div class="strategy-list-empty" v-else>
      暂无已保存策略
    </div>
  </el-card>
</template>

<script>
import { defineComponent } from 'vue';
import { ElCard, ElSelect, ElOption, ElButton } from 'element-plus';

export default defineComponent({
  name: 'StrategySection',
  components: {
    ElCard,
    ElSelect,
    ElOption,
    ElButton
  },
  props: {
    selectedStrategyName: {
      type: String,
      required: true
    },
    strategyOptions: {
      type: Array,
      required: true
    },
    strategyDetailItems: {
      type: Array,
      required: true
    }
  },
  emits: ['handleSelectStrategy', 'loadStrategyOptions'],
  setup(props, { emit }) {
    const onHandleSelectStrategy = (name) => {
      emit('handleSelectStrategy', name);
    };

    const onLoadStrategyOptions = () => {
      emit('loadStrategyOptions');
    };

    return {
      onHandleSelectStrategy,
      onLoadStrategyOptions
    };
  }
});
</script>

<style scoped>
.strategy-card {
  margin-bottom: 24px;
  border: 1px solid #d6d2cb;
  background: #fbfaf8;
  box-shadow: 0 12px 20px rgba(107, 103, 99, 0.1);
  width: 100%;
  max-width: 100%;
}

.strategy-bar {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.strategy-select {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.strategy-label {
  font-weight: 600;
  color: #6b6763;
}

.strategy-detail {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 16px;
  padding: 12px;
  background: #f6f5f4;
  border: 1px solid #d6d2cb;
  border-radius: 10px;
}

.detail-item {
  display: flex;
  gap: 6px;
  font-size: 13px;
  color: #6b6763;
}

.detail-label {
  color: #8b8680;
  font-weight: 600;
}

.detail-value {
  color: #4c4743;
}

.strategy-empty {
  font-size: 13px;
  color: #8b8680;
}

.strategy-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.strategy-list-title {
  font-weight: 600;
  color: #6b6763;
}

.strategy-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.strategy-item {
  border: 1px solid #d6d2cb;
  border-radius: 10px;
  padding: 12px;
  background: #fdfcfb;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.strategy-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 16px rgba(107, 103, 99, 0.15);
  border-color: #c6bdb4;
}

.strategy-item.active {
  border-color: #d4b3a1;
  box-shadow: 0 12px 20px rgba(212, 179, 161, 0.25);
}

.strategy-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.strategy-item-name {
  font-weight: 600;
  color: #4c4743;
}

.strategy-item-tag {
  background: #d4b3a1;
  color: #4c4743;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
}

.strategy-list-empty {
  font-size: 13px;
  color: #8b8680;
}
</style>