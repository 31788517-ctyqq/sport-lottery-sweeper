<template>
  <div class="strategy-section-mobile">
    <!-- 策略选择区域 -->
    <div class="strategy-select-mobile">
      <div class="select-header">
        <span class="strategy-label">策略筛选</span>
        <el-button size="small" @click="onLoadStrategyOptions" class="refresh-button">刷新</el-button>
      </div>
      <el-select
        v-model="selectedStrategyName"
        placeholder="请选择策略"
        clearable
        filterable
        class="strategy-select-dropdown"
        @change="onHandleSelectStrategy"
      >
        <el-option
          v-for="name in strategyOptions"
          :key="name"
          :label="name"
          :value="name"
        />
      </el-select>
    </div>

    <!-- 策略详情 -->
    <div class="strategy-detail-mobile" v-if="strategyDetailItems.length">
      <div class="detail-header">
        <span>策略详情</span>
      </div>
      <div class="detail-grid">
        <div class="detail-item" v-for="item in strategyDetailItems" :key="item.label">
          <span class="detail-label">{{ item.label }}:</span>
          <span class="detail-value">{{ item.value }}</span>
        </div>
      </div>
    </div>
    <div class="strategy-empty-mobile" v-else>
      <i class="el-icon-info"></i>
      <span>选择策略后将显示详情</span>
    </div>

    <!-- 策略列表（移动端垂直列表） -->
    <div class="strategy-list-mobile" v-if="strategyOptions.length">
      <div class="list-header">
        <span>策略列表</span>
        <span class="list-count">{{ strategyOptions.length }} 个策略</span>
      </div>
      <div class="strategy-vertical-list">
        <div
          class="strategy-item-mobile"
          v-for="name in strategyOptions"
          :key="name"
          :class="{ active: name === selectedStrategyName }"
          @click="onHandleSelectStrategy(name)"
        >
          <div class="item-content">
            <div class="item-header">
              <span class="item-name">{{ name }}</span>
              <div class="item-tags">
                <span class="item-tag-new" v-if="name === '当前策略'">NEW</span>
                <span class="item-tag-selected" v-if="name === selectedStrategyName">已选</span>
              </div>
            </div>
            <div class="item-actions">
              <el-button size="mini" @click.stop="onHandleSelectStrategy(name)">选择</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="strategy-list-empty-mobile" v-else>
      <i class="el-icon-folder-opened"></i>
      <span>暂无已保存策略</span>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { ElSelect, ElOption, ElButton } from 'element-plus';

export default defineComponent({
  name: 'StrategySectionMobile',
  components: {
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
.strategy-section-mobile {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

.strategy-select-mobile {
  background-color: #fdfcfb;
  border: 1px solid #d6d2cb;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 6px 12px rgba(107, 103, 99, 0.08);
}

.select-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.strategy-label {
  font-weight: 600;
  color: #6b6763;
  font-size: 16px;
}

.refresh-button {
  font-size: 13px;
  padding: 6px 12px;
  height: 32px;
}

.strategy-select-dropdown {
  width: 100%;
}

.strategy-select-dropdown :deep(.el-input__inner) {
  height: 44px;
  font-size: 15px;
  border-radius: 8px;
}

.strategy-detail-mobile {
  background-color: #f6f5f4;
  border: 1px solid #d6d2cb;
  border-radius: 12px;
  padding: 16px;
}

.detail-header {
  font-weight: 600;
  color: #6b6763;
  margin-bottom: 12px;
  font-size: 15px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}

.detail-label {
  color: #8b8680;
  font-weight: 600;
}

.detail-value {
  color: #4c4743;
  word-break: break-word;
}

.strategy-empty-mobile {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  background-color: #f9f8f7;
  border: 1px dashed #d6d2cb;
  border-radius: 12px;
  color: #8b8680;
  font-size: 14px;
}

.strategy-empty-mobile i {
  font-size: 16px;
}

.strategy-list-mobile {
  background-color: #fdfcfb;
  border: 1px solid #d6d2cb;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 6px 12px rgba(107, 103, 99, 0.08);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  color: #6b6763;
  font-size: 16px;
}

.list-count {
  font-size: 13px;
  color: #8b8680;
  font-weight: normal;
}

.strategy-vertical-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.strategy-item-mobile {
  border: 1px solid #d6d2cb;
  border-radius: 10px;
  padding: 16px;
  background: #fdfcfb;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.strategy-item-mobile:active {
  transform: translateY(1px);
  box-shadow: 0 4px 8px rgba(107, 103, 99, 0.1);
}

.strategy-item-mobile.active {
  border-color: #d4b3a1;
  box-shadow: 0 8px 16px rgba(212, 179, 161, 0.2);
  background-color: #fef9f7;
}

.item-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.item-name {
  font-weight: 600;
  color: #4c4743;
  font-size: 15px;
  word-break: break-word;
}

.item-tags {
  display: flex;
  gap: 6px;
}

.item-tag-new {
  background: #67c23a;
  color: white;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
}

.item-tag-selected {
  background: #d4b3a1;
  color: #4c4743;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
}

.item-actions {
  flex-shrink: 0;
  margin-left: 12px;
}

.item-actions .el-button {
  font-size: 12px;
  padding: 6px 12px;
  height: 32px;
}

.strategy-list-empty-mobile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 32px 20px;
  background-color: #f9f8f7;
  border: 1px dashed #d6d2cb;
  border-radius: 12px;
  color: #8b8680;
  font-size: 14px;
}

.strategy-list-empty-mobile i {
  font-size: 32px;
  color: #c6bdb4;
}

/* 响应式调整 */
@media (max-width: 480px) {
  .detail-grid {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .item-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .item-actions {
    margin-left: 0;
    width: 100%;
  }
  
  .item-actions .el-button {
    width: 100%;
  }
}

@media (max-width: 375px) {
  .strategy-select-mobile,
  .strategy-detail-mobile,
  .strategy-list-mobile {
    padding: 12px;
  }
  
  .strategy-label,
  .list-header {
    font-size: 15px;
  }
}
</style>