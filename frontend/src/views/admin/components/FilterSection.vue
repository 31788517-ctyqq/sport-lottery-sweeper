<template>
  <div class="filter-section">
    <el-row :gutter="20" class="dimension-row">
      <el-col :span="8">
        <div class="filter-group">
          <div class="group-title">
            <span>实力等级差 ΔP</span>
            <span class="group-hint">主客实力差分层</span>
          </div>
          <el-checkbox-group v-model="filterForm.powerDiffs" class="checkbox-grid strength-options">
            <el-checkbox-button
              v-for="option in strengthOptions"
              :key="option.value"
              :value="option.value"
            >
              <div class="option-tile">
                <div class="option-value">{{ option.label }}</div>
                <div class="option-desc">{{ option.desc }}</div>
                <div class="option-range">{{ option.range }}</div>
              </div>
            </el-checkbox-button>
          </el-checkbox-group>
        </div>
      </el-col>

      <el-col :span="8">
        <div class="filter-group">
          <div class="group-title">
            <span>赢盘等级差 ΔWP</span>
            <span class="group-hint">盘路兑现力对撞</span>
          </div>
          <el-checkbox-group v-model="filterForm.winPanDiffs" class="checkbox-grid win-pan-options">
            <el-checkbox-button
              v-for="option in winPanOptions"
              :key="option.value"
              :value="option.value"
            >
              <div class="option-tile">
                <div class="option-value">{{ option.label }}</div>
                <div class="option-desc">{{ option.desc }}</div>
                <div class="option-range">{{ option.range }}</div>
              </div>
            </el-checkbox-button>
          </el-checkbox-group>
        </div>
      </el-col>

      <el-col :span="8">
        <div class="filter-group">
          <div class="group-title">
            <span>一赔稳定性 P-Tier</span>
            <span class="group-hint">正路可信度等级</span>
          </div>
          <el-checkbox-group v-model="filterForm.stabilityTiers" class="tier-grid stability-options">
            <el-checkbox-button
              v-for="option in stabilityOptions"
              :key="option.value"
              :value="option.value"
            >
              <div class="tier-tile">
                <div class="tier-label">{{ option.label }}</div>
                <div class="tier-desc">{{ option.desc }}</div>
                <div class="tier-range">{{ option.range }}</div>
              </div>
            </el-checkbox-button>
          </el-checkbox-group>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="control-row">
      <el-col :span="8">
        <div class="filter-group">
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
      </el-col>

      <el-col :span="8">
        <div class="filter-group">
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
      </el-col>

      <el-col :span="8">
        <div class="filter-group">
          <div class="group-title">
            <span>策略应用和保存</span>
            <span class="group-hint">策略管理操作区</span>
          </div>
          <div class="example-strategies">
            <div class="group-title">示例策略</div>
            <div class="preset-grid">
              <el-button @click="onLoadExampleStrategy('strong')">强势正路</el-button>
              <el-button @click="onLoadExampleStrategy('upset')">冷门潜质</el-button>
              <el-button @click="onLoadExampleStrategy('balance')">均衡博弈</el-button>
            </div>
          </div>

          <el-alert
            v-if="directionWarning"
            title="方向背离预警：实力与盘路选择方向相反，可能触发降级"
            type="warning"
            :closable="false"
            class="direction-alert"
          />

          <div class="filter-actions">
            <el-tooltip content="根据当前条件生成临时策略" placement="top">
              <el-button type="primary" @click="onApplyAdvancedFilter" :loading="loading">生成当前策略</el-button>
            </el-tooltip>
            
            <el-tooltip content="清除所有筛选条件" placement="top">
              <el-button @click="onResetFilters">重置</el-button>
            </el-tooltip>
            
            <el-tooltip content="将当前三维筛选条件保存为永久策略" placement="top">
              <el-button type="success" @click="onSaveStrategy">保存策略</el-button>
            </el-tooltip>
            
            <el-tooltip content="修改或删除已保存的策略" placement="top">
              <el-button @click="onManageStrategies">管理策略</el-button>
            </el-tooltip>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { 
  ElRow, 
  ElCol, 
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
  ElDropdown, 
  ElDropdownMenu, 
  ElDropdownItem,
  ElTooltip
} from 'element-plus';

export default defineComponent({
  name: 'FilterSection',
  components: {
    ElRow,
    ElCol,
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
    ElDropdown,
    ElDropdownMenu,
    ElDropdownItem,
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
.filter-section {
  margin-top: 24px;
}

.dimension-row {
  margin-bottom: 24px;
}

.control-row {
  margin-top: 20px;
}

.filter-group {
  border: 1px solid #d6d2cb;
  border-radius: 10px;
  padding: 18px 20px;
  margin-bottom: 16px;
  background-color: #fdfcfb;
  box-shadow: 0 10px 18px rgba(107, 103, 99, 0.08);
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

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.tier-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.option-tile {
  text-align: left;
  line-height: 1.3;
  padding: 6px 8px;
}

.option-value {
  font-weight: 700;
  color: #6b6763;
  font-size: 13px;
}

.option-desc {
  font-size: 12px;
  color: #9fb1c4;
  margin-top: 2px;
}

.option-range {
  font-size: 11px;
  color: #8b8680;
  margin-top: 2px;
}

.tier-tile {
  text-align: left;
  line-height: 1.3;
  padding: 6px 8px;
}

.tier-label {
  font-weight: 700;
  color: #6b6763;
  font-size: 13px;
}

.tier-desc {
  font-size: 12px;
  color: #aabead;
  margin-top: 2px;
}

.tier-range {
  font-size: 11px;
  color: #8b8680;
  margin-top: 2px;
}

.pill-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 4px;
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

.preset-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.direction-alert {
  margin-bottom: 20px;
}

.example-strategies {
  margin-bottom: 20px;
}

.example-strategies .group-title {
  font-size: 14px;
  color: #8b8680;
  margin-bottom: 8px;
  font-weight: 600;
}

.filter-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-start;
}

.control-row .el-col:last-child .filter-group {
  background-color: #f6f5f4;
  border-color: #d6d2cb;
  box-shadow: none;
}
</style>
