<template>
  <el-card class="strategy-card">
    <div class="strategy-bar">
      <div class="strategy-select">
        <span class="strategy-label">策略筛选</span>
        <el-select
          :model-value="selectedStrategyName"
          placeholder="请选择策略"
          clearable
          filterable
          style="width: 260px"
          @update:model-value="onHandleSelectStrategy"
        >
          <el-option v-for="name in strategyOptions" :key="name" :label="name" :value="name" />
        </el-select>
        <el-button size="small" @click="onLoadStrategyOptions">刷新</el-button>
      </div>

      <div class="strategy-detail" v-if="strategyDetailItems.length">
        <div class="detail-item" v-for="item in strategyDetailItems" :key="item.label">
          <span class="detail-label">{{ item.label }}:</span>
          <span class="detail-value">{{ item.value }}</span>
        </div>
      </div>
      <div class="strategy-empty" v-else>选择策略后显示条件摘要</div>
    </div>

    <div class="strategy-list" v-if="strategyOptions.length > 1">
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
  </el-card>
</template>

<script setup>
const props = defineProps({
  selectedStrategyName: { type: String, required: true },
  strategyOptions: { type: Array, required: true },
  strategyDetailItems: { type: Array, required: true }
})

const emit = defineEmits(['handleSelectStrategy', 'loadStrategyOptions'])

const onHandleSelectStrategy = (name) => emit('handleSelectStrategy', name)
const onLoadStrategyOptions = () => emit('loadStrategyOptions')
</script>

<style scoped>
.strategy-card {
  margin-bottom: 12px;
  border: 1px solid #d6d2cb;
  background: #fbfaf8;
  box-shadow: 0 10px 16px rgba(107, 103, 99, 0.08);
  width: 100%;
}

.strategy-bar {
  display: flex;
  flex-direction: column;
  gap: 10px;
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
  gap: 8px 14px;
  padding: 8px 2px;
  background: transparent;
  border: none;
  border-radius: 0;
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
  gap: 8px;
}

.strategy-list-title {
  font-weight: 600;
  color: #6b6763;
}

.strategy-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.strategy-item {
  border: 1px solid #e1ddd7;
  border-radius: 10px;
  padding: 10px 12px;
  background: #f8f7f4;
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.2s ease, background-color 0.2s ease;
}

.strategy-item:hover {
  transform: translateY(-1px);
  border-color: #c6bdb4;
  background: #f3f1ed;
}

.strategy-item.active {
  border-color: #8ea3b0;
  background: #e8eef2;
}

.strategy-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.strategy-item-name {
  font-weight: 600;
  color: #4c4743;
}

.strategy-item-tag {
  background: #dfe7ec;
  color: #4f5963;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .strategy-grid,
  .strategy-detail {
    grid-template-columns: 1fr;
  }
}
</style>
