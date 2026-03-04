<template>
  <div class="filter-section-mobile">
    <!-- 三维筛选区域 - 垂直堆叠 -->
    <div class="dimension-stack">
      <!-- 实力等级差 ΔP -->
      <div class="filter-group-mobile">
        <div class="group-title">
          <span>实力等级差 ΔP</span>
          <span class="group-hint">主客实力差分层</span>
        </div>
        <el-checkbox-group v-model="filterForm.powerDiffs" class="checkbox-grid-mobile strength-options">
          <el-checkbox-button
            v-for="option in strengthOptions"
            :key="option.value"
            :value="option.value"
            class="checkbox-button-mobile"
          >
            <div class="option-tile-mobile">
              <div class="option-value">{{ option.label }}</div>
              <div class="option-desc">{{ option.desc }}</div>
              <div class="option-range">{{ option.range }}</div>
            </div>
          </el-checkbox-button>
        </el-checkbox-group>
      </div>

      <!-- 赢盘等级差 ΔWP -->
      <div class="filter-group-mobile">
        <div class="group-title">
          <span>赢盘等级差 ΔWP</span>
          <span class="group-hint">盘路兑现力对撞</span>
        </div>
        <el-checkbox-group v-model="filterForm.winPanDiffs" class="checkbox-grid-mobile win-pan-options">
          <el-checkbox-button
            v-for="option in winPanOptions"
            :key="option.value"
            :value="option.value"
            class="checkbox-button-mobile"
          >
            <div class="option-tile-mobile">
              <div class="option-value">{{ option.label }}</div>
              <div class="option-desc">{{ option.desc }}</div>
              <div class="option-range">{{ option.range }}</div>
            </div>
          </el-checkbox-button>
        </el-checkbox-group>
      </div>

      <!-- 一赔稳定性 P-Tier -->
      <div class="filter-group-mobile">
        <div class="group-title">
          <span>一赔稳定性 P-Tier</span>
          <span class="group-hint">正路可信度等级</span>
        </div>
        <el-checkbox-group v-model="filterForm.stabilityTiers" class="tier-grid-mobile stability-options">
          <el-checkbox-button
            v-for="option in stabilityOptions"
            :key="option.value"
            :value="option.value"
            class="checkbox-button-mobile"
          >
            <div class="tier-tile-mobile">
              <div class="tier-label">{{ option.label }}</div>
              <div class="tier-desc">{{ option.desc }}</div>
              <div class="tier-range">{{ option.range }}</div>
            </div>
          </el-checkbox-button>
        </el-checkbox-group>
      </div>
    </div>

    <!-- 其它条件 - 垂直堆叠 -->
    <div class="control-stack">
      <!-- 其它条件 -->
      <div class="filter-group-mobile">
        <div class="group-title">
          <span>其它条件</span>
          <span class="group-hint">多维叠加</span>
        </div>
        <div class="filter-item">
          <label>联赛筛选</label>
          <el-select
            v-model="filterForm.leagues"
            placeholder="请选择联赛"
            multiple
            collapse-tags
            style="width: 100%"
          >
            <el-option
              v-for="league in availableLeagues"
              :key="league"
              :label="league"
              :value="league"
            />
          </el-select>
        </div>
        <div class="filter-item">
          <label>date_time</label>
          <el-select
            v-model="filterForm.dateTime"
            placeholder="date_time"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="value in dateTimeOptions"
              :key="value"
              :label="value"
              :value="value"
            />
          </el-select>
        </div>
        <div class="filter-item">
          <label>日期范围</label>
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%"
          />
        </div>
      </div>

      <!-- 策略筛选 -->
      <div class="filter-group-mobile">
        <div class="group-title">
          <span>策略筛选</span>
          <span class="group-hint">排序与规则</span>
        </div>
        <div class="filter-item">
          <label>排序方式</label>
          <el-radio-group v-model="filterForm.sortBy">
            <el-radio value="p_level">P级</el-radio>
            <el-radio value="delta_wp">ΔWP</el-radio>
            <el-radio value="power_diff">ΔP</el-radio>
          </el-radio-group>
        </div>
        <div class="filter-item">
          <label>排序顺序</label>
          <el-radio-group v-model="filterForm.sortOrder">
            <el-radio value="asc">升序</el-radio>
            <el-radio value="desc">降序</el-radio>
          </el-radio-group>
        </div>
        <div class="filter-item switch-item">
          <label>应用降级规则</label>
          <el-switch v-model="filterForm.includeDerating" />
        </div>
        <div class="rule-preview">排序预览：P级降序 → ΔWP降序</div>
      </div>

      <!-- 策略应用和保存 -->
      <div class="filter-group-mobile">
        <div class="group-title">
          <span>策略应用和保存</span>
          <span class="group-hint">策略管理操作区</span>
        </div>
        <div class="example-strategies">
          <div class="group-title">示例策略</div>
          <div class="preset-grid-mobile">
            <el-button @click="onLoadExampleStrategy('strong')" class="preset-button">强势正路</el-button>
            <el-button @click="onLoadExampleStrategy('upset')" class="preset-button">冷门潜质</el-button>
            <el-button @click="onLoadExampleStrategy('balance')" class="preset-button">均衡博弈</el-button>
          </div>
        </div>

        <el-alert
          v-if="directionWarning"
          title="方向背离预警：实力与盘路选择方向相反，可能触发降级"
          type="warning"
          :closable="false"
          class="direction-alert"
        />

        <div class="filter-actions-mobile">
          <el-button type="primary" @click="onApplyAdvancedFilter" :loading="loading" class="action-button">生成当前策略</el-button>
          <el-button @click="onResetFilters" class="action-button">重置</el-button>
          <el-button type="success" @click="onSaveStrategy" class="action-button">保存策略</el-button>
          <el-button @click="onManageStrategies" class="action-button">管理策略</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { 
  ElCheckboxGroup, 
  ElCheckboxButton, 
  ElSelect, 
  ElOption, 
  ElDatePicker, 
  ElRadioGroup, 
  ElRadio, 
  ElSwitch, 
  ElAlert, 
  ElButton,
  ElTooltip
} from 'element-plus';

export default defineComponent({
  name: 'FilterSectionMobile',
  components: {
    ElCheckboxGroup,
    ElCheckboxButton,
    ElSelect,
    ElOption,
    ElDatePicker,
    ElRadioGroup,
    ElRadio,
    ElSwitch,
    ElAlert,
    ElButton,
    ElTooltip
  },
  props: {
    filterForm: {
      type: Object,
      required: true
    },
    strengthOptions: {
      type: Array,
      required: true
    },
    winPanOptions: {
      type: Array,
      required: true
    },
    stabilityOptions: {
      type: Array,
      required: true
    },
    availableLeagues: {
      type: Array,
      required: true
    },
    dateTimeOptions: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      required: true
    },
    directionWarning: {
      type: Boolean,
      required: true
    }
  },
  emits: ['applyPreset', 'saveStrategy', 'manageStrategies', 'applyAdvancedFilter', 'resetFilters', 'loadExampleStrategy'],
  setup(props, { emit }) {
    const onApplyPreset = (preset) => {
      emit('applyPreset', preset);
    };

    const onSaveStrategy = () => {
      emit('saveStrategy');
    };

    const onManageStrategies = () => {
      emit('manageStrategies');
    };

    const onApplyAdvancedFilter = () => {
      emit('applyAdvancedFilter');
    };

    const onResetFilters = () => {
      emit('resetFilters');
    };

    const onLoadExampleStrategy = (exampleName) => {
      emit('loadExampleStrategy', exampleName);
    };

    return {
      onApplyPreset,
      onSaveStrategy,
      onManageStrategies,
      onApplyAdvancedFilter,
      onResetFilters,
      onLoadExampleStrategy
    };
  }
});
</script>

<style scoped>
.filter-section-mobile {
  margin-top: 16px;
}

.dimension-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.control-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-group-mobile {
  border: 1px solid #d6d2cb;
  border-radius: 12px;
  padding: 16px;
  background-color: #fdfcfb;
  box-shadow: 0 6px 12px rgba(107, 103, 99, 0.08);
}

.group-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #6b6763;
}

.group-hint {
  font-size: 13px;
  color: #8b8680;
  font-weight: normal;
}

.filter-item {
  margin-bottom: 16px;
}

.filter-item label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #6b6763;
  font-size: 14px;
}

/* 移动端优化复选框网格 */
.checkbox-grid-mobile,
.tier-grid-mobile {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

/* 触摸目标优化 */
.checkbox-button-mobile {
  min-height: 60px;
  min-width: 0; /* 允许按钮收缩 */
  padding: 8px;
  border-radius: 8px;
}

.checkbox-button-mobile :deep(.el-checkbox-button__inner) {
  width: 100%;
  height: 100%;
  padding: 8px;
  border-radius: 8px;
  font-size: 13px;
}

.option-tile-mobile,
.tier-tile-mobile {
  text-align: left;
  line-height: 1.3;
  padding: 4px 6px;
}

.option-value,
.tier-label {
  font-weight: 700;
  color: #6b6763;
  font-size: 13px;
}

.option-desc,
.tier-desc {
  font-size: 12px;
  color: #9fb1c4;
  margin-top: 2px;
}

.option-range,
.tier-range {
  font-size: 11px;
  color: #8b8680;
  margin-top: 2px;
}

.switch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.rule-preview {
  margin-top: 12px;
  font-size: 13px;
  color: #8b8680;
  font-style: italic;
}

.preset-grid-mobile {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 16px;
}

.preset-button {
  width: 100%;
  font-size: 13px;
  padding: 8px 4px;
}

.direction-alert {
  margin-bottom: 16px;
}

.example-strategies .group-title {
  font-size: 14px;
  color: #8b8680;
  margin-bottom: 8px;
  font-weight: 600;
}

.filter-actions-mobile {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-button {
  width: 100%;
  height: 44px;
  font-size: 14px;
  border-radius: 8px;
}

/* 响应式调整 */
@media (max-width: 480px) {
  .checkbox-grid-mobile,
  .tier-grid-mobile {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .preset-grid-mobile {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .filter-group-mobile {
    padding: 12px;
  }
  
  .group-title {
    font-size: 15px;
  }
}

@media (max-width: 375px) {
  .preset-grid-mobile {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}
</style>