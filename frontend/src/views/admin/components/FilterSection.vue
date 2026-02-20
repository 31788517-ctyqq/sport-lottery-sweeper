<template>
  <div class="filter-section">
    <el-row :gutter="16" class="dimension-row">
      <el-col :xs="24" :sm="24" :md="12" :lg="8">
        <div class="filter-group">
          <div class="group-title">
            <span>实力等级差 ΔP</span>
            <span class="group-hint">主客实力分层</span>
          </div>
          <el-checkbox-group v-model="filterForm.powerDiffs" class="checkbox-grid">
            <el-checkbox-button v-for="option in strengthOptions" :key="option.value" :value="option.value">
              <div class="option-tile">
                <div class="option-value">{{ option.label }}</div>
                <div class="option-desc">{{ option.desc }}</div>
                <div class="option-range">{{ option.range }}</div>
              </div>
            </el-checkbox-button>
          </el-checkbox-group>
        </div>
      </el-col>

      <el-col :xs="24" :sm="24" :md="12" :lg="8">
        <div class="filter-group">
          <div class="group-title">
            <span>赢盘等级差 ΔWP</span>
            <span class="group-hint">盘路兑现对照</span>
          </div>
          <el-checkbox-group v-model="filterForm.winPanDiffs" class="checkbox-grid">
            <el-checkbox-button v-for="option in winPanOptions" :key="option.value" :value="option.value">
              <div class="option-tile">
                <div class="option-value">{{ option.label }}</div>
                <div class="option-desc">{{ option.desc }}</div>
                <div class="option-range">{{ option.range }}</div>
              </div>
            </el-checkbox-button>
          </el-checkbox-group>
        </div>
      </el-col>

      <el-col :xs="24" :sm="24" :md="12" :lg="8">
        <div class="filter-group">
          <div class="group-title">
            <span>一赔稳定性 P-Tier</span>
            <span class="group-hint">正路可信度分级</span>
          </div>
          <el-checkbox-group v-model="filterForm.stabilityTiers" class="tier-grid">
            <el-checkbox-button v-for="option in stabilityOptions" :key="option.value" :value="option.value">
              <div class="option-tile">
                <div class="option-value">{{ option.label }}</div>
                <div class="option-desc">{{ option.desc }}</div>
                <div class="option-range">{{ option.range }}</div>
              </div>
            </el-checkbox-button>
          </el-checkbox-group>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="control-row">
      <el-col :xs="24" :sm="24" :md="12" :lg="8">
        <div class="filter-group">
          <div class="group-title">
            <span>其它条件</span>
            <span class="group-hint">补充筛选</span>
          </div>
          <div class="filter-item">
            <label>联赛筛选</label>
            <el-select v-model="filterForm.leagues" placeholder="请选择联赛" multiple collapse-tags style="width: 100%">
              <el-option v-for="league in availableLeagues" :key="league" :label="league" :value="league" />
            </el-select>
          </div>
          <div class="filter-item">
            <label>期号筛选</label>
            <el-select v-model="filterForm.dateTime" placeholder="请选择期号" clearable style="width: 100%">
              <el-option v-for="value in dateTimeOptions" :key="value" :label="value" :value="value" />
            </el-select>
          </div>
          <div class="filter-item">
            <label>时间范围</label>
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

      <el-col :xs="24" :sm="24" :md="12" :lg="8">
        <div class="filter-group">
          <div class="group-title">
            <span>策略规则</span>
            <span class="group-hint">排序与降级</span>
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
          <div class="rule-preview">排序预览：P级优先，次级按 ΔWP 排序</div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="24" :md="24" :lg="8">
        <div class="filter-group">
          <div class="group-title">
            <span>策略应用</span>
            <span class="group-hint">应用、保存与管理</span>
          </div>

          <div class="example-strategies">
            <div class="quick-title">示例策略</div>
            <div class="preset-grid">
              <el-button @click="emit('loadExampleStrategy', 'strong')">强势正路</el-button>
              <el-button @click="emit('loadExampleStrategy', 'upset')">冷门潜质</el-button>
              <el-button @click="emit('loadExampleStrategy', 'balance')">均衡博弈</el-button>
            </div>
          </div>

          <el-alert
            v-if="directionWarning"
            title="方向背离预警：实力与盘路筛选方向相反，可能触发降级"
            type="warning"
            :closable="false"
            class="direction-alert"
          />

          <div class="filter-actions">
            <el-tooltip content="基于当前三维条件执行筛选" placement="top">
              <el-button type="primary" @click="emit('applyAdvancedFilter')" :loading="loading">应用筛选</el-button>
            </el-tooltip>
            <el-tooltip content="清空全部筛选条件" placement="top">
              <el-button @click="emit('resetFilters')">重置</el-button>
            </el-tooltip>
            <el-tooltip content="保存当前筛选为策略" placement="top">
              <el-button type="success" @click="emit('saveStrategy')">保存策略</el-button>
            </el-tooltip>
            <el-tooltip content="查看、修改或删除已保存策略" placement="top">
              <el-button @click="emit('manageStrategies')">管理策略</el-button>
            </el-tooltip>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
defineProps({
  filterForm: { type: Object, required: true },
  strengthOptions: { type: Array, required: true },
  winPanOptions: { type: Array, required: true },
  stabilityOptions: { type: Array, required: true },
  availableLeagues: { type: Array, required: true },
  dateTimeOptions: { type: Array, required: true },
  loading: { type: Boolean, required: true },
  directionWarning: { type: Boolean, required: true }
})

const emit = defineEmits([
  'applyPreset',
  'saveStrategy',
  'manageStrategies',
  'applyAdvancedFilter',
  'resetFilters',
  'loadExampleStrategy'
])
</script>

<style scoped>
.filter-section {
  margin-top: 0;
}

.dimension-row {
  margin-bottom: 14px;
}

.control-row {
  margin-top: 6px;
}

.filter-group {
  border: 1px solid #d6d2cb;
  border-radius: 10px;
  padding: 16px 18px;
  margin-bottom: 10px;
  background-color: #fdfcfb;
  box-shadow: 0 8px 16px rgba(107, 103, 99, 0.06);
}

.group-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  font-size: 15px;
  font-weight: 600;
  color: #6b6763;
}

.group-hint {
  font-size: 12px;
  color: #8b8680;
  font-weight: normal;
}

.filter-item {
  margin-bottom: 12px;
}

.filter-item label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #6b6763;
  font-size: 13px;
}

.checkbox-grid,
.tier-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.option-tile {
  text-align: left;
  line-height: 1.25;
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

.switch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.rule-preview {
  margin-top: 8px;
  font-size: 12px;
  color: #8b8680;
}

.quick-title {
  font-size: 13px;
  color: #8b8680;
  margin-bottom: 8px;
  font-weight: 600;
}

.preset-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 14px;
}

.direction-alert {
  margin-bottom: 12px;
}

.filter-actions {
  margin-top: 8px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.control-row .el-col:last-child .filter-group {
  background-color: #f6f5f4;
  border-color: #d6d2cb;
}

@media (max-width: 1200px) {
  .checkbox-grid,
  .tier-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .checkbox-grid,
  .tier-grid,
  .preset-grid {
    grid-template-columns: 1fr;
  }
}
</style>
