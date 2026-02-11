<template>
  <div class="beidan-filter-panel">
    <FilterCardHeader 
      :total-results="totalResults" 
      :loading="loading"
      @fetch-real-data="fetchRealData"
    />
    
    <FilterSection
      :filter-form="filterForm"
      :strength-options="strengthOptions"
      :win-pan-options="winPanOptions"
      :stability-options="stabilityOptions"
      :available-leagues="availableLeagues"
      :date-time-options="dateTimeOptions"
      :loading="loading"
      :direction-warning="directionWarning"
      @apply-preset="handlePreset"
      @handle-save-strategy="handleSaveStrategy"
      @apply-advanced-filter="applyAdvancedFilter"
      @reset-filters="resetFilters"
    />
    
    <StrategySection
      :selected-strategy-name="selectedStrategyName"
      :strategy-options="strategyOptions"
      :strategy-detail-items="strategyDetailItems"
      @handle-select-strategy="handleSelectStrategy"
      @load-strategy-options="loadStrategyOptions"
    />
    <StatsCard 
      v-if="showStats && strategyApplied"
      :statistics="statistics"
      :filter-form="filterForm"
    />

    <ResultsSection
      v-if="strategyApplied"
      :paged-results="pagedResults"
      :loading="loading"
      :show-stats="showStats"
      :total-results="totalResults"
      :current-page="currentPage"
      :page-size="pageSize"
      @toggle-stats="toggleStats"
      @export-results="exportResults"
      @handle-sort-change="handleSortChange"
      @handle-size-change="handleSizeChange"
      @handle-current-change="handleCurrentChange"
      @open-analysis="openAnalysis"
    />

    <RulesDialog 
      v-model:visible="showRulesDialog"
      :rules="pLevelRules"
    />

    <AnalysisDialog 
      v-model:visible="showAnalysisDialog"
      :analysis-data="analysisData"
    />
    
    <!-- 新增多策略配置组件 -->
    <MultiStrategyConfig
      :show-multi-strategy-panel="showMultiStrategyPanel"
      @update:show-multi-strategy-panel="handleUpdateShowMultiStrategyPanel"
      @strategy-configured="handleStrategyConfigured"
    />
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '@/utils/request';

// 引入拆分的子组件
import FilterCardHeader from './components/FilterCardHeader.vue';
import FilterSection from './components/FilterSection.vue';
import StrategySection from './components/StrategySection.vue';
import StatsCard from './components/StatsCard.vue';
import ResultsSection from './components/ResultsSection.vue';
import RulesDialog from './components/RulesDialog.vue';
import AnalysisDialog from './components/AnalysisDialog.vue';
import MultiStrategyConfig from './components/MultiStrategyConfig.vue';  // 新增多策略配置组件

export default {
  name: 'BeidanFilterPanel',
  components: {
    FilterCardHeader,
    FilterSection,
    StrategySection,
    StatsCard,
    ResultsSection,
    RulesDialog,
    AnalysisDialog,
    MultiStrategyConfig  // 注册新组件
  },
  setup() {
    // 筛选表单数据
    const filterForm = reactive({
      powerDiffs: [],
      winPanDiffs: [],
      stabilityTiers: [],
      leagues: [],
      dateTime: '',
      dateRange: null,
      sortBy: 'p_level',
      sortOrder: 'desc',
      includeDerating: true
    });

    const strengthOptions = [
      { value: -3, label: '-3', range: '< -25', desc: '客队统治' },
      { value: -2, label: '-2', range: '-25 ~ -17', desc: '客队压制' },
      { value: -1, label: '-1', range: '-16 ~ -9', desc: '客队微优' },
      { value: 0, label: '0', range: '-8 ~ +8', desc: '旗鼓相当' },
      { value: 1, label: '+1', range: '+9 ~ +16', desc: '主队微优' },
      { value: 2, label: '+2', range: '+17 ~ +25', desc: '强力压制' },
      { value: 3, label: '+3', range: '> +25', desc: '降维打击' }
    ];

    const winPanOptions = [
      { value: 4, label: '+4', range: 'S', desc: '主极火热' },
      { value: 3, label: '+3', range: 'S', desc: '主极火热' },
      { value: 2, label: '+2', range: 'A', desc: '主获利走强' },
      { value: 1, label: '+1', range: 'A', desc: '主获利走强' },
      { value: 0, label: '0', range: 'B', desc: '数据均衡' },
      { value: -1, label: '-1', range: 'C', desc: '客获利走强' },
      { value: -2, label: '-2', range: 'C', desc: '客获利走强' },
      { value: -3, label: '-3', range: 'D', desc: '客极火热' },
      { value: -4, label: '-4', range: 'D', desc: '客极火热' }
    ];

    const stabilityOptions = [
      { value: 'S', label: 'S', range: 'P1', desc: '正路稳胆' },
      { value: 'A', label: 'A', range: 'P2', desc: '正路首选' },
      { value: 'B', label: 'B', range: 'P3', desc: '正路保障' },
      { value: 'B-', label: 'B-', range: 'P4', desc: '正路分歧' },
      { value: 'C', label: 'C', range: 'P5', desc: '正路存疑' },
      { value: 'D', label: 'D', range: 'P6', desc: '正路脆弱' },
      { value: 'E', label: 'E', range: 'P7', desc: '正路缺失' }
    ];

    // 数据状态
    const loading = ref(false);
    const rawMatches = ref([]);
    const filterResults = ref([]);
    const totalResults = ref(0);
    const currentPage = ref(1);
    const pageSize = ref(10);
    const showStats = ref(true);
    const showAnalysisDialog = ref(false);
    const analysisData = ref(null);

    // 可用联赛列表
    const availableLeagues = ref([]);
    const dateTimeOptions = ref([]);
    const strategyOptions = ref([]);
    const selectedStrategyName = ref('');
    const selectedStrategy = ref(null);
    const strategyApplied = ref(false);

    // P级规则弹窗
    const showRulesDialog = ref(false);
    const pLevelRules = ref(null);

    // 统计数据
    const statistics = ref({
      total_matches: 0,
      average_power_diff: 0,
      average_win_pan_diff: 0,
      average_stability: 0,
      delta_p_count: 0,
      delta_wp_count: 0,
      p_tier_count: 0
    });

    // 计算属性
    const pagedResults = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value;
      return filterResults.value.slice(start, start + pageSize.value);
    });

    const strategyPreviewMap = ref({});

    const CURRENT_STRATEGY = '当前应用';

    // 在这里保留所有的业务逻辑函数
    const displayValue = (value) => {
      if (value === null || value === undefined || value === '') return '-';
      return value;
    };

    const formatSourceAttributes = (value) => {
      if (!value) return '-';
      try {
        const text = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
        return text.length > 1200 ? `${text.slice(0, 1200)}...` : text;
      } catch (error) {
        return String(value);
      }
    };

    const getJiaoFenMatches = (data) => {
      if (!data) return [];
      const matches = [];
      for (let i = 1; i <= 6; i += 1) {
        const key = `jiaoFenMatch${i}`;
        if (data[key]) matches.push(data[key]);
      }
      return matches;
    };

    const getPercentValue = (value) => {
      if (!value) return 0;
      const match = String(value).match(/(\d+)(?:\.\d+)?%/);
      if (match) return Math.min(100, Number(match[1]));
      return 0;
    };

    const getProgressValue = (value) => {
      const num = Number(value);
      if (Number.isNaN(num)) return 0;
      return Math.max(0, Math.min(100, num));
    };

    const getEfficiencyValue = (value) => {
      if (!value) return 0;
      const parts = String(value).split(':');
      if (parts.length < 2) return 0;
      const num = Number(parts[1]);
      return Number.isNaN(num) ? 0 : num;
    };

    const getSpfWins = (value) => {
      if (!value) return 0;
      const match = String(value).match(/(\d+)胜/);
      if (!match) return 0;
      return Number(match[1]);
    };

    const compareAdvantage = (homeValue, awayValue) => {
      const homeNum = Number(homeValue);
      const awayNum = Number(awayValue);
      if (Number.isNaN(homeNum) || Number.isNaN(awayNum)) return '持平';
      if (homeNum > awayNum) return '主队';
      if (homeNum < awayNum) return '客队';
      return '持平';
    };

    const getStatusLabel = (data) => {
      const status = data?.matchStatus || data?.status;
      if (!status) return "未开始";
      if (status === "finished" || status === "已结束") return "已结束";
      if (status === "ongoing" || status === "进行中") return "进行中";
      return String(status);
    };

    const openAnalysis = async (row) => {
      const raw = row?.source_attributes;
      if (raw) {
        analysisData.value = raw;
        showAnalysisDialog.value = true;
        return;
      }

      const matchId = row?.match_id;
      if (!matchId) {
        analysisData.value = null;
        showAnalysisDialog.value = true;
        return;
      }

      try {
        const response = await request.get(`/api/v1/data-source-100qiu/match/${matchId}`);
        const payload = response?.data?.source_attributes;
        analysisData.value = payload || null;
      } catch (error) {
        analysisData.value = null;
      } finally {
        showAnalysisDialog.value = true;
      }
    };

    const formatMatchId = (value) => {
      if (value === null || value === undefined || value === '') return '-';
      return String(value);
    };

    const formatMatchTime = (value) => {
      if (value === null || value === undefined || value === '') return '-';
      const date = value instanceof Date ? value : new Date(value);
      if (Number.isNaN(date.getTime())) return String(value);
      const pad = (num) => String(num).padStart(2, '0');
      return `${date.getFullYear()}/${pad(date.getMonth() + 1)}/${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
    };

    const parsePercents = (text) => {
      if (!text) return [];
      const matches = String(text).match(/(\d+(?:\.\d+)?)%/g) || [];
      return matches.map((m) => Number(m.replace('%', ''))).filter((v) => !Number.isNaN(v));
    };

    const calcDeltaPLevel = (homePower, awayPower) => {
      if (homePower === '-' || awayPower === '-') return 0;
      const diff = Number(homePower) - Number(awayPower);
      if (diff > 25) return 3;
      if (diff >= 17) return 2;
      if (diff >= 9) return 1;
      if (diff >= -8) return 0;
      if (diff >= -16) return -1;
      if (diff >= -25) return -2;
      return -3;
    };

    const wpToScore = (wp) => {
      const value = Number(wp);
      if (Number.isNaN(value)) return 0;
      if (value > 1.4) return 4;
      if (value >= 1.2) return 3;
      if (value >= 0.8) return 2;
      if (value >= 0.6) return 1;
      return 0;
    };

    const calcDeltaWp = (homeWp, awayWp) => {
      return wpToScore(homeWp) - wpToScore(awayWp);
    };

    const calcStabilityTier = (homeFeature, guestFeature) => {
      const homeText = homeFeature || '';
      const guestText = guestFeature || '';
      const homePercents = parsePercents(homeText);
      const guestPercents = parsePercents(guestText);
      const homeOne = /一赔/.test(homeText) ? (homePercents[0] ?? 0) : null;
      const guestOne = /一赔/.test(guestText) ? (guestPercents[0] ?? 0) : null;

      if (homeOne !== null && guestOne !== null) {
        const pValue = homeOne + guestOne;
        if (pValue >= 140) return { tier: 'S', pLevel: 1 };
        if (pValue >= 110) return { tier: 'A', pLevel: 2 };
        return { tier: 'B-', pLevel: 4 };
      }

      if (homeOne !== null || guestOne !== null) {
        const oneValue = homeOne !== null ? homeOne : guestOne;
        const opponentPercents = homeOne !== null ? guestPercents : homePercents;
        const opponentMax = opponentPercents.length ? Math.max(...opponentPercents) : 0;
        const pValue = oneValue - opponentMax;
        if (pValue >= 40) return { tier: 'B', pLevel: 3 };
        if (pValue >= 15) return { tier: 'C', pLevel: 5 };
        if (pValue >= 0) return { tier: 'D', pLevel: 6 };
        return { tier: 'E', pLevel: 7 };
      }

      return { tier: 'E', pLevel: 7 };
    };

    const normalizeMatches = (matches = [], dateTime = null) => {
      return matches.map((item, index) => {
        const matchId = item.match_id ?? item.id ?? item.lineId ?? item.line_id ?? `match-${index}`;
        const raw = item.source_attributes ?? item.sourceAttributes ?? item.raw_data ?? item.rawData ?? null;
        const homeTeam = raw?.homeTeam ?? item.home_team ?? item.homeTeam ?? item.home ?? '-';
        const awayTeam = raw?.guestTeam ?? item.away_team ?? item.awayTeam ?? item.guestTeam ?? item.guest_team ?? item.away ?? '-';
        const league = raw?.gameShortName ?? item.league ?? item.gameShortName ?? item.leagueName ?? '-';
        const matchTime = raw?.matchTimeStr ?? item.match_time ?? item.matchTime ?? item.matchTimeStr ?? item.startTime ?? item.matchDate ?? '-';
        const powerHome = raw?.homePower ?? item.power_home ?? item.powerHome ?? item.homePower ?? item.home_power ?? '-';
        const powerAway = raw?.guestPower ?? item.power_away ?? item.powerAway ?? item.guestPower ?? item.awayPower ?? item.away_power ?? '-';
        const winPanHome = raw?.homeWinPan ?? item.win_pan_home ?? item.winPanHome ?? item.homeWinPan ?? item.home_win_pan ?? '-';
        const winPanAway = raw?.guestWinPan ?? item.win_pan_away ?? item.winPanAway ?? item.guestWinPan ?? item.awayWinPan ?? item.away_win_pan ?? '-';
        const homeFeature = raw?.homeFeature ?? item.home_feature ?? item.homeFeature ?? '-';
        const awayFeature = raw?.guestFeature ?? item.away_feature ?? item.awayFeature ?? item.guestFeature ?? item.guest_feature ?? '-';
        const deltaPLevel = calcDeltaPLevel(powerHome, powerAway);
        const deltaWp = calcDeltaWp(winPanHome, winPanAway);
        const stabilityResult = calcStabilityTier(raw?.homeFeature, raw?.guestFeature);
        const stabilityValue = stabilityResult.tier;
        const pLevel = stabilityResult.pLevel;
        const powerDiff = deltaPLevel;
        const winPanDiff = deltaWp;
        const lineId = raw?.lineId ?? item.lineId ?? item.line_id ?? matchId;
        
        // 现在match_id已经是date_time_lineId格式，直接使用
        const formattedMatchId = item.match_id || String(matchId);
        // 优先从 raw.data_source 中获取 date_time，如果不存在则使用传入的 dateTime 参数或 filterForm.dateTime
        const dateTimeFromRaw = raw?.date_time ?? raw?.dateTime ?? raw?.['date_time'];
        let dateTimePart = dateTimeFromRaw || dateTime || filterForm.dateTime;
        
        // 如果还没有dateTimePart，尝试从matchTime中提取YYMMDD格式
        if (!dateTimePart && matchTime) {
          try {
            const dateStr = String(matchTime).split('T')[0];
            const yearMatch = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})$/);
            if (yearMatch) {
              const [, year, month, day] = yearMatch;
              const yy = year.slice(-2);
              const d = parseInt(day, 10);
              // 100球格式：YYMM + D（如果D<10则不加前导零，否则加前导零）
              // 例如：2026-02-03 -> 26023, 2026-02-13 -> 260213
              dateTimePart = d < 10 ? `${yy}${month}${d}` : `${yy}${month}${d}`;
            }
          } catch (e) {
            console.warn('Failed to extract date_time from matchTime:', matchTime, e);
          }
        }
        
        // 如果还是没有dateTimePart，回退到原有的逻辑
        if (!dateTimePart) {
          dateTimePart = String(matchTime || '').split('T')[0].replace(/-/g, '').slice(2);
        }
        
        return {
          match_id: formattedMatchId,
          home_team: homeTeam,
          away_team: awayTeam,
          league,
          match_time: matchTime,
          power_home: powerHome,
          power_away: powerAway,
          win_pan_home: winPanHome,
          win_pan_away: winPanAway,
          home_feature: homeFeature,
          away_feature: awayFeature,
          p_level: pLevel,
          delta_wp: deltaWp,
          power_diff: powerDiff,
          win_pan_diff: winPanDiff,
          stability: stabilityValue,
          source_attributes: item.source_attributes ?? item.sourceAttributes ?? item.raw_data ?? item.rawData ?? null
        };
      });
    };

    const fetchPLevelRules = async () => {
      try {
        const response = await request.get('/api/v1/beidan-filter/p-level-rules');
        pLevelRules.value = response.data.rules;
        showRulesDialog.value = true;
      } catch (error) {
        console.error('获取P级规则失败:', error);
        ElMessage.error('获取P级规则失败');
      }
    };

    const fetchDateTimeOptions = async () => {
      try {
        const response = await request.get('/api/v1/data-source-100qiu/date-time-options');
        const options = response?.data?.options || [];
        dateTimeOptions.value = options;
        if (!filterForm.dateTime && options.length > 0) {
          filterForm.dateTime = options[0];
        }
      } catch (error) {
        console.error('Failed to load date_time options:', error);
      }
    };

    const buildStrategyPreview = (strategy) => {
      if (!strategy) return '未设置';
      const parts = [];
      if (strategy.dateTime) parts.push(`date_time:${strategy.dateTime}`);
      if (strategy.pLevels?.length) parts.push(`P${strategy.pLevels.join('/')}`);
      if (strategy.leagues?.length) parts.push(`联赛:${strategy.leagues.slice(0, 2).join(',')}`);
      if (strategy.dateRange?.length) {
        const range = strategy.dateRange.map((item) => {
          if (!item) return '';
          if (typeof item === 'string') return item.split('T')[0];
          if (item.toISOString) return item.toISOString().split('T')[0];
          return String(item);
        }).join('~');
        if (range) parts.push(`日期:${range}`);
      }
      return parts.join(' | ') || '未设置';
    };

    const serializeStrategy = () => JSON.stringify({
      powerDiffs: filterForm.powerDiffs,
      winPanDiffs: filterForm.winPanDiffs,
      stabilityTiers: filterForm.stabilityTiers,
      pLevels: filterForm.pLevels,
      leagues: filterForm.leagues,
      dateTime: filterForm.dateTime,
      dateRange: filterForm.dateRange,
      sortBy: filterForm.sortBy,
      sortOrder: filterForm.sortOrder,
      includeDerating: filterForm.includeDerating
    });

    const loadStrategyOptions = () => {
      const keys = Object.keys(localStorage).filter(key => key.startsWith('beidan_strategy_'));
      const names = keys.map(key => key.replace('beidan_strategy_', ''));
      strategyOptions.value = [CURRENT_STRATEGY, ...names];
      const map = {};
      names.forEach((name) => {
        try {
          const saved = localStorage.getItem(`beidan_strategy_${name}`);
          map[name] = buildStrategyPreview(saved ? JSON.parse(saved) : null);
        } catch (error) {
          map[name] = '未设置';
        }
      });
      strategyPreviewMap.value = map;
    };

    const formatDateRange = (range) => {
      if (!Array.isArray(range) || range.length !== 2) return '未设置';
      return range.map((item) => {
        if (!item) return '';
        if (typeof item === 'string') return item.split('T')[0];
        if (item.toISOString) return item.toISOString().split('T')[0];
        return String(item);
      }).join(' ~ ');
    };

    const strategyDetailItems = computed(() => {
      if (!selectedStrategy.value) return [];
      const detail = selectedStrategy.value;
      return [
        { label: 'P等级', value: detail.pLevels?.length ? detail.pLevels.map(v => `P${v}`).join(', ') : '未设置' },
        { label: '联赛', value: detail.leagues?.length ? detail.leagues.join(', ') : '未设置' },
        { label: 'date_time', value: detail.dateTime || '未设置' },
        { label: '日期范围', value: formatDateRange(detail.dateRange) },
        { label: '实力差', value: detail.powerDiffs?.length ? detail.powerDiffs.join(', ') : '未设置' },
        { label: '赢盘差', value: detail.winPanDiffs?.length ? detail.winPanDiffs.join(', ') : '未设置' },
        { label: 'P-Tier', value: detail.stabilityTiers?.length ? detail.stabilityTiers.join(', ') : '未设置' }
      ];
    });

    const clearResults = () => {
      filterResults.value = [];
      totalResults.value = 0;
      currentPage.value = 1;
    };

    const handleSelectStrategy = async (name) => {
      if (!name) {
        selectedStrategy.value = null;
        selectedStrategyName.value = '';
        strategyApplied.value = false;
        clearResults();
        return;
      }

      if (name === CURRENT_STRATEGY) {
        selectedStrategyName.value = CURRENT_STRATEGY;
        selectedStrategy.value = { ...filterForm };
        if (!strategyApplied.value) {
          clearResults();
        }
        return;
      }

      const savedStrategy = localStorage.getItem(`beidan_strategy_${name}`);
      if (!savedStrategy) {
        ElMessage.error('策略不存在或已被删除');
        return;
      }
      try {
        const parsed = JSON.parse(savedStrategy);
        Object.assign(filterForm, parsed);
        selectedStrategy.value = parsed;
        selectedStrategyName.value = name;
        strategyApplied.value = true;
        await applyAdvancedFilter();
      } catch (error) {
        console.error('加载策略失败:', error);
        ElMessage.error('加载策略失败');
      }
    };

    const fetchRealData = async () => {
      loading.value = true;
      try {
        const response = await request.get('/api/v1/data-source-100qiu/latest-matches', {
          params: { limit: 200, include_raw: true }
        });

        const matches = response?.data?.matches || response?.matches || [];
        if (response?.success !== false) {
          rawMatches.value = normalizeMatches(matches, filterForm.dateTime);
          filterResults.value = [...rawMatches.value];
          totalResults.value = response?.data?.total ?? rawMatches.value.length;
          currentPage.value = 1;

          const leaguesSet = new Set(rawMatches.value.map(match => match.league));
          availableLeagues.value = Array.from(leaguesSet).filter(league => league);

          await updateStatistics();
        } else {
          console.error('Failed to load 100qiu data:', response?.message || 'Unknown error');
          ElMessage.error('Failed to load 100qiu data: ' + (response?.message || 'Unknown error'));
        }
      } catch (error) {
        console.error('Failed to load 100qiu data:', error);
        ElMessage.error('Failed to load 100qiu data');
      } finally {
        loading.value = false;
      }
    };

    const applyAdvancedFilter = async () => {
      if (!strategyApplied.value && !selectedStrategyName.value) {
        ElMessage.info('请先从策略筛选栏选择策略');
        return;
      }

      // 检查是否有有效的认证token
      const token = localStorage.getItem('access_token') || localStorage.getItem('token');
      if (!token) {
        ElMessage.error('请先登录以使用策略筛选功能');
        return;
      }

      loading.value = true;

      try {
        // 将前端的离散筛选值转换为后端期望的连续范围格式
        let strengthFilter = null;
        if (filterForm.powerDiffs.length > 0) {
          // 根据文档规范映射到正确的连续范围
          const getRangeForPowerDiff = (value) => {
            if (value === -3) return [-100.0, -25.0]; // < -25
            if (value === -2) return [-25.0, -17.0];  // -17 ~ -25
            if (value === -1) return [-16.0, -9.0];   // -9 ~ -16  
            if (value === 0) return [-8.0, 8.0];      // -8 ~ +8
            if (value === 1) return [9.0, 16.0];      // +9 ~ +16
            if (value === 2) return [17.0, 25.0];     // +17 ~ +25
            if (value === 3) return [25.0, 100.0];    // > +25
            return [-100.0, 100.0];
          };
          
          // 收集所有选中的范围
          const allRanges = filterForm.powerDiffs.map(v => getRangeForPowerDiff(v));
          const overallMin = Math.min(...allRanges.map(r => r[0]));
          const overallMax = Math.max(...allRanges.map(r => r[1]));
          
          strengthFilter = {
            min_strength: overallMin,
            max_strength: overallMax
          };
        }

        let winPanFilter = null;
        if (filterForm.winPanDiffs.length > 0) {
          const minWinPan = Math.min(...filterForm.winPanDiffs);
          const maxWinPan = Math.max(...filterForm.winPanDiffs);
          
          const getRangeForWinPanDiff = (value) => {
            if (value <= -4) return [-4.0, -3.5];
            if (value === -3) return [-3.5, -2.5];
            if (value === -2) return [-2.5, -1.5];
            if (value === -1) return [-1.5, -0.5];
            if (value === 0) return [-0.5, 0.5];
            if (value === 1) return [0.5, 1.5];
            if (value === 2) return [1.5, 2.5];
            if (value === 3) return [2.5, 3.5];
            if (value >= 4) return [3.5, 4.0];
            return [-4.0, 4.0];
          };
          
          const allRanges = filterForm.winPanDiffs.map(v => getRangeForWinPanDiff(v));
          const overallMin = Math.min(...allRanges.map(r => r[0]));
          const overallMax = Math.max(...allRanges.map(r => r[1]));
          
          winPanFilter = {
            min_win_pan: overallMin,
            max_win_pan: overallMax
          };
        }

        let stabilityFilter = null;
        if (filterForm.stabilityTiers.length > 0) {
          stabilityFilter = {
            tiers: filterForm.stabilityTiers
          };
        }

        // 构造筛选请求对象
        const requestPayload = {
          strength_filter: strengthFilter,
          win_pan_filter: winPanFilter,
          stability_filter: stabilityFilter,
          leagues: filterForm.leagues.length > 0 ? filterForm.leagues : null,
          date_time: filterForm.dateTime || null,
          date_range: filterForm.dateRange ? [
            filterForm.dateRange[0]?.toISOString().split('T')[0],
            filterForm.dateRange[1]?.toISOString().split('T')[0]
          ] : null,
          sort_by: filterForm.sortBy,
          sort_order: filterForm.sortOrder,
          include_derating: filterForm.includeDerating
        };

        const response = await request.post('/api/v1/beidan-filter/advanced-filter', requestPayload);
        
        if (response.data && response.data.matches) {
          const normalized = normalizeMatches(response.data.matches, filterForm.dateTime);
          filterResults.value = normalized;
          totalResults.value = response.data.total ?? normalized.length;
          currentPage.value = 1;
          strategyApplied.value = true; // 确保策略应用状态为true
          
          // 更新统计信息
          await updateStatistics();
        } else {
          console.error('应用筛选失败:', response.data?.detail || '未知错误');
          ElMessage.error('应用筛选失败: ' + (response.data?.detail || '未知错误'));
          filterResults.value = [];
          totalResults.value = 0;
        }
      } catch (error) {
        console.error('应用筛选时发生错误:', error);
        ElMessage.error('应用筛选时发生错误');
        filterResults.value = [];
        totalResults.value = 0;
      } finally {
        loading.value = false;
      }
    };

    const updateStatistics = async () => {
      // 检查是否有有效的token
      const token = localStorage.getItem('access_token') || localStorage.getItem('token');
      if (!token) {
        console.warn('No valid token found, skipping statistics update');
        return;
      }
      
      try {
        // 将前端的离散筛选值转换为后端期望的连续范围格式（与applyAdvancedFilter保持一致）
        let strengthFilter = null;
        if (filterForm.powerDiffs.length > 0) {
          // 根据文档规范映射到正确的连续范围
          const getRangeForPowerDiff = (value) => {
            if (value === -3) return [-100.0, -25.0]; // < -25
            if (value === -2) return [-25.0, -17.0];  // -17 ~ -25
            if (value === -1) return [-16.0, -9.0];   // -9 ~ -16  
            if (value === 0) return [-8.0, 8.0];      // -8 ~ +8
            if (value === 1) return [9.0, 16.0];      // +9 ~ +16
            if (value === 2) return [17.0, 25.0];     // +17 ~ +25
            if (value === 3) return [25.0, 100.0];    // > +25
            return [-100.0, 100.0];
          };
          
          const allRanges = filterForm.powerDiffs.map(v => getRangeForPowerDiff(v));
          const overallMin = Math.min(...allRanges.map(r => r[0]));
          const overallMax = Math.max(...allRanges.map(r => r[1]));
          
          strengthFilter = {
            min_strength: overallMin,
            max_strength: overallMax
          };
        }

        let winPanFilter = null;
        if (filterForm.winPanDiffs.length > 0) {
          const minWinPan = Math.min(...filterForm.winPanDiffs);
          const maxWinPan = Math.max(...filterForm.winPanDiffs);
          
          const getRangeForWinPanDiff = (value) => {
            if (value <= -4) return [-4.0, -3.5];
            if (value === -3) return [-3.5, -2.5];
            if (value === -2) return [-2.5, -1.5];
            if (value === -1) return [-1.5, -0.5];
            if (value === 0) return [-0.5, 0.5];
            if (value === 1) return [0.5, 1.5];
            if (value === 2) return [1.5, 2.5];
            if (value === 3) return [2.5, 3.5];
            if (value >= 4) return [3.5, 4.0];
            return [-4.0, 4.0];
          };
          
          const allRanges = filterForm.winPanDiffs.map(v => getRangeForWinPanDiff(v));
          const overallMin = Math.min(...allRanges.map(r => r[0]));
          const overallMax = Math.max(...allRanges.map(r => r[1]));
          
          winPanFilter = {
            min_win_pan: overallMin,
            max_win_pan: overallMax
          };
        }

        let stabilityFilter = null;
        if (filterForm.stabilityTiers.length > 0) {
          stabilityFilter = {
            tiers: filterForm.stabilityTiers
          };
        }

        // 构造筛选请求对象
        const requestPayload = {
          strength_filter: strengthFilter,
          win_pan_filter: winPanFilter,
          stability_filter: stabilityFilter,
          leagues: filterForm.leagues.length > 0 ? filterForm.leagues : null,
          date_time: filterForm.dateTime || null,
          date_range: filterForm.dateRange ? [
            filterForm.dateRange[0]?.toISOString().split('T')[0],
            filterForm.dateRange[1]?.toISOString().split('T')[0]
          ] : null,
          sort_by: filterForm.sortBy,
          sort_order: filterForm.sortOrder,
          include_derating: filterForm.includeDerating
        };

        const response = await request.post('/api/v1/beidan-filter/statistics', requestPayload);
        
        if (response.data) {
          statistics.value = {
            total_matches: response.data.total_matches,
            average_power_diff: response.data.average_strength_diff,
            average_win_pan_diff: response.data.average_win_pan_diff,
            average_stability: response.data.average_stability,
            delta_p_count: response.data.delta_p_count,
            delta_wp_count: response.data.delta_wp_count,
            p_tier_count: response.data.p_tier_count
          };
        }
      } catch (error) {
        console.error('更新统计信息时发生错误:', error);
        // 不显示错误消息，因为统计信息不是必需的
      }
    };

    const resetFilters = () => {
      filterForm.powerDiffs = [];
      filterForm.winPanDiffs = [];
      filterForm.stabilityTiers = [];

      if (selectedStrategyName.value === CURRENT_STRATEGY) {
        strategyApplied.value = false;
        clearResults();
      }
    };

    const toggleStats = () => {
      showStats.value = !showStats.value;
    };

    const exportResults = (format) => {
      ElMessage.info(`导出功能开发中，格式: ${format}`);
      // 实际应用中应实现具体的导出逻辑
    };

    const viewDetails = (row) => {
      console.log('查看比赛详情:', row);
      ElMessage.info(`查看比赛 ${row.home_team} vs ${row.away_team} 的详情`);
    };

    const getPLevelTagType = (level) => {
      switch (level) {
        case 1: return 'success'; // P1级用绿色
        case 2: return 'primary'; // P2级用蓝色
        case 3: return 'warning'; // P3级用黄色
        case 4: return 'danger';  // P4级用红色
        case 5: return 'info';    // P5级用灰色
        default: return 'info';
      }
    };

    const handleSortChange = (params) => {
      console.log('排序变化:', params);
      // 实现客户端排序或重新请求数据
    };

    const handleSizeChange = (size) => {
      pageSize.value = size;
      currentPage.value = 1;
    };

    const handleCurrentChange = (page) => {
      currentPage.value = page;
    };

    const handleSaveStrategy = (command) => {
      if (command === 'save') {
        ElMessageBox.prompt('请输入策略名称', '保存策略', {
          confirmButtonText: '保存',
          cancelButtonText: '取消',
          inputPattern: /\S+/,
          inputErrorMessage: '策略名称不能为空'
        }).then(({ value }) => {
          const strategyName = value.trim();
          localStorage.setItem(`beidan_strategy_${strategyName}`, serializeStrategy());
          loadStrategyOptions();
          ElMessage.success('策略已保存');
        }).catch(() => {
          // 用户取消
        });
      } else if (command === 'load') {
        const strategyKeys = Object.keys(localStorage).filter(key => key.startsWith('beidan_strategy_'));
        if (strategyKeys.length === 0) {
          ElMessage.info('暂无可加载策略');
          return;
        }

        const strategyNames = strategyKeys.map(key => key.replace('beidan_strategy_', ''));
        let optionsHtml = '';
        strategyNames.forEach(name => {
          optionsHtml += `<option value="${name}">${name}</option>`;
        });

        ElMessageBox({
          title: '加载策略',
          message: `
            <select id="strategySelect" style="width:100%;padding:5px;">
              ${optionsHtml}
            </select>
            <div style="display:flex;gap:8px;margin-top:10px;">
              <button id="strategyOverwrite" style="flex:1;padding:6px;border:1px solid #d6d2cb;border-radius:6px;background:#f6f5f4;cursor:pointer;">覆盖保存</button>
              <button id="strategyDelete" style="flex:1;padding:6px;border:1px solid #d6d2cb;border-radius:6px;background:#f6f5f4;cursor:pointer;">删除</button>
            </div>
            <div style="margin-top:8px;font-size:12px;color:#8b8680;">提示：覆盖保存会更新当前筛选内容。</div>
          `,
          showCancelButton: true,
          confirmButtonText: '加载',
          cancelButtonText: '取消',
          dangerouslyUseHTMLString: true,
          didOpen: () => {
            const selectEl = document.getElementById('strategySelect');
            if (selectEl && strategyNames.length > 0) {
              selectEl.value = strategyNames[0];
            }

            const overwriteBtn = document.getElementById('strategyOverwrite');
            if (overwriteBtn) {
              overwriteBtn.addEventListener('click', () => {
                const name = selectEl ? selectEl.value : '';
                if (!name) return;
                localStorage.setItem(`beidan_strategy_${name}`, serializeStrategy());
                loadStrategyOptions();
                ElMessage.success('策略已覆盖');
              });
            }

            const deleteBtn = document.getElementById('strategyDelete');
            if (deleteBtn) {
              deleteBtn.addEventListener('click', () => {
                const name = selectEl ? selectEl.value : '';
                if (!name) return;
                localStorage.removeItem(`beidan_strategy_${name}`);
                if (selectedStrategyName.value === name) {
                  selectedStrategyName.value = '';
                  selectedStrategy.value = null;
                  strategyApplied.value = false;
                  clearResults();
                }
                loadStrategyOptions();
                ElMessage.success('策略已删除');
              });
            }
          }
        }).then(() => {
          const selectEl = document.getElementById('strategySelect');
          if (selectEl) {
            const selectedStrategy = selectEl.value;
            const savedStrategy = localStorage.getItem(`beidan_strategy_${selectedStrategy}`);
            if (savedStrategy) {
              const parsed = JSON.parse(savedStrategy);
              Object.assign(filterForm, parsed);
              selectedStrategyName.value = selectedStrategy;
              selectedStrategy.value = parsed;
              strategyApplied.value = true;
              ElMessage.success('策略已加载');
              applyAdvancedFilter(); // 加载后刷新结果
            } else {
              ElMessage.error('策略加载失败');
            }
          }
        }).catch(() => {
          // 用户取消
        });
      }
    };

    const directionWarning = computed(() => {
      const hasPositiveStrength = filterForm.powerDiffs.some((v) => v > 0);
      const hasNegativeStrength = filterForm.powerDiffs.some((v) => v < 0);
      const hasPositiveWinPan = filterForm.winPanDiffs.some((v) => v > 0);
      const hasNegativeWinPan = filterForm.winPanDiffs.some((v) => v < 0);

      if ((hasPositiveStrength && hasNegativeWinPan) || (hasNegativeStrength && hasPositiveWinPan)) {
        return true;
      }
      return false;
    });

    const applyPreset = (preset) => {
      if (preset === 'strong') {
        filterForm.powerDiffs = [2, 3];
        filterForm.winPanDiffs = [3, 4];
        filterForm.stabilityTiers = ['S', 'A', 'B'];
      } else if (preset === 'upset') {
        filterForm.powerDiffs = [-1, 0];
        filterForm.winPanDiffs = [-3, -4];
        filterForm.stabilityTiers = ['D', 'E'];
      } else if (preset === 'balance') {
        filterForm.powerDiffs = [0];
        filterForm.winPanDiffs = [0];
        filterForm.stabilityTiers = ['B', 'C'];
      }
      
      ElMessage.success(`已应用"${preset === 'strong' ? '强势正路' : preset === 'upset' ? '冷门潜质' : '均衡博弈'}"预设`);
    };

    // 在setup函数末尾返回所有需要暴露给模板的属性和方法
    return {
      filterForm,
      loading,
      rawMatches,
      filterResults,
      totalResults,
      currentPage,
      pageSize,
      showStats,
      showAnalysisDialog,
      analysisData,
      availableLeagues,
      dateTimeOptions,
      strategyOptions,
      selectedStrategyName,
      selectedStrategy,
      strategyApplied,
      showRulesDialog,
      pLevelRules,
      statistics,
      pagedResults,
      displayValue,
      formatSourceAttributes,
      getJiaoFenMatches,
      getPercentValue,
      getProgressValue,
      getEfficiencyValue,
      getSpfWins,
      compareAdvantage,
      getStatusLabel,
      openAnalysis,
      formatMatchId,
      formatMatchTime,
      parsePercents,
      calcDeltaPLevel,
      wpToScore,
      calcDeltaWp,
      calcStabilityTier,
      fetchPLevelRules,
      fetchDateTimeOptions,
      buildStrategyPreview,
      serializeStrategy,
      loadStrategyOptions,
      formatDateRange,
      strategyDetailItems,
      clearResults,
      handleSelectStrategy,
      fetchRealData,
      applyAdvancedFilter,
      updateStatistics,
      resetFilters,
      toggleStats,
      exportResults,
      viewDetails,
      getPLevelTagType,
      handleSortChange,
      handleSizeChange,
      handleCurrentChange,
      handleSaveStrategy,
      directionWarning,
      applyPreset,
      strengthOptions,
      winPanOptions,
      stabilityOptions,
      CURRENT_STRATEGY
    };
  }
};
</script>

<style scoped>
.beidan-filter-panel {
  padding: 24px;
  background: linear-gradient(180deg, #f6f5f4 0%, #f0eeeb 100%);
  border-radius: 18px;
  min-height: 100%;
}

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

.filter-card, .stats-card, .result-card {
  margin-bottom: 24px;
  border: 1px solid #d6d2cb;
  background: #fbfaf8;
  box-shadow: 0 14px 24px rgba(107, 103, 99, 0.12);
}

.strategy-card {
  margin-bottom: 24px;
  border: 1px solid #d6d2cb;
  background: #fbfaf8;
  box-shadow: 0 12px 20px rgba(107, 103, 99, 0.1);
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

.result-card .el-table {
  margin-bottom: 24px;
  border-radius: 10px;
  overflow: hidden;
}

.raw-json {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 12px;
  color: #6f6a64;
}

.analysis-header {
  margin-bottom: 16px;
}

.analysis-hero {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 16px;
  align-items: center;
  margin-bottom: 18px;
  background: linear-gradient(135deg, #2e5a2f, #3b7a39);
  border-radius: 16px;
  padding: 18px;
  color: #f6f3ee;
}

.team-card {
  border: 1px solid #d6d2cb;
  border-radius: 14px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.12);
  color: #f6f3ee;
  border-color: rgba(255, 255, 255, 0.18);
}

.team-card--away {
  background: rgba(255, 255, 255, 0.16);
}

.team-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.75);
}

.team-name {
  font-size: 18px;
  font-weight: 700;
  color: #f6f3ee;
  margin-top: 6px;
}

.team-meta {
  margin-top: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.75);
}

.hero-center {
  text-align: center;
  padding: 12px 16px;
  color: #f6f3ee;
}

.match-title {
  font-size: 16px;
  font-weight: 700;
  color: #f6f3ee;
}

.match-time {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  margin-top: 6px;
}

.match-meta {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.75);
  margin-top: 6px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.2);
  color: #f6f3ee;
  font-size: 12px;
  font-weight: 600;
  margin-top: 8px;
}

.analysis-columns {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 16px;
  margin-bottom: 16px;
}

.analysis-dialog :deep(.el-dialog) {
  max-width: 920px;
  width: 92%;
}

.analysis-sim-container {
  display: grid;
  gap: 16px;
}

.analysis-sim-header {
  padding: 12px 16px;
  border-radius: 12px;
  background: #f4f1ed;
  border: 1px solid #e4dfd8;
}

.analysis-sim-title {
  font-size: 18px;
  font-weight: 700;
  color: #5a534e;
}

.analysis-sim-subtitle {
  font-size: 13px;
  color: #8b8680;
  margin-top: 4px;
}

.analysis-sim-card {
  border: 1px solid #e2ddd6;
  border-radius: 12px;
  padding: 14px 16px;
  background: #fdfcfb;
}

.analysis-sim-card-title {
  font-size: 14px;
  font-weight: 600;
  color: #6b6763;
  margin-bottom: 10px;
}

.analysis-sim-basic {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.analysis-sim-team {
  text-align: center;
}

.analysis-sim-team-name {
  font-size: 18px;
  font-weight: 700;
  color: #5a534e;
}

.analysis-sim-team-meta {
  font-size: 12px;
  color: #8b8680;
  margin-top: 4px;
}

.analysis-sim-vs {
  text-align: center;
  color: #7a7067;
}

.analysis-sim-league {
  font-size: 13px;
  font-weight: 600;
}

.analysis-sim-vs-text {
  font-size: 22px;
  font-weight: 700;
  margin: 4px 0;
  color: #b36b5e;
}

.analysis-sim-time {
  font-size: 12px;
  color: #8b8680;
}

.analysis-sim-odds {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.analysis-sim-odds-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
  border-radius: 8px;
  background: #f6f2ee;
  border: 1px solid #e4dfd8;
  font-size: 12px;
  color: #8b8680;
  text-align: center;
}

.analysis-sim-odds-item strong {
  color: #5a534e;
  font-size: 16px;
}

.analysis-sim-progress {
  display: grid;
  gap: 8px;
  margin-bottom: 12px;
}

.analysis-sim-progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #6f6a64;
}

.analysis-sim-progress-bars :deep(.el-progress__bar) {
  height: 10px;
  border-radius: 999px;
}

.analysis-sim-table {
  border: 1px solid #ece6df;
  border-radius: 10px;
  overflow: hidden;
}

.analysis-sim-table-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(90px, 1fr));
  padding: 10px 12px;
  font-size: 13px;
  color: #6f6a64;
  border-bottom: 1px solid #eee8e1;
}

.analysis-sim-table-row:last-child {
  border-bottom: none;
}

.analysis-sim-table-head {
  background: #f2eeea;
  font-weight: 600;
  color: #6b6763;
}

.analysis-sim-odds-panels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.analysis-sim-odds-panel,
.analysis-sim-lose-panel {
  border: 1px solid #e4dfd8;
  border-radius: 10px;
  padding: 12px;
  background: #f8f5f1;
  text-align: center;
}

.analysis-sim-panel-title {
  font-size: 13px;
  color: #8b8680;
  margin-bottom: 6px;
}

.analysis-sim-panel-value {
  font-size: 22px;
  font-weight: 700;
  color: #b36b5e;
  margin-bottom: 8px;
}

.analysis-sim-panel-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  font-size: 12px;
  color: #6f6a64;
}

.analysis-sim-lose {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.analysis-sim-summary {
  padding: 10px 12px;
  background: #f4f1ed;
  border-radius: 8px;
  color: #6f6a64;
  font-size: 13px;
}

.analysis-sim-history {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}

.analysis-sim-history-item {
  padding: 8px 10px;
  border: 1px solid #e4dfd8;
  border-radius: 8px;
  background: #fdfcfb;
  font-size: 12px;
  color: #6f6a64;
}

.analysis-sim-source {
  display: grid;
  gap: 8px;
  font-size: 12px;
  color: #6f6a64;
}

.analysis-sim-source span {
  color: #8b8680;
  margin-right: 6px;
}

@media (max-width: 900px) {
  .analysis-sim-basic {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .analysis-sim-table-row {
    grid-template-columns: repeat(2, minmax(90px, 1fr));
    row-gap: 6px;
  }
}

.analysis-tabs {
  margin-top: 14px;
}

.analysis-tabs :deep(.el-tabs__header) {
  margin: 0 0 12px;
  border-bottom: 1px solid #e2ddd6;
}

.analysis-tabs :deep(.el-tabs__nav-wrap::after) {
  background: transparent;
}

.analysis-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  color: #6f6a64;
  padding: 0 18px;
}

.analysis-tabs :deep(.el-tabs__item.is-active) {
  color: #c24a3a;
  font-weight: 600;
}

.analysis-tabs :deep(.el-tabs__active-bar) {
  background-color: #c24a3a;
  height: 2px;
}

.analysis-section {
  margin-bottom: 16px;
}

.analysis-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #6b6763;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.analysis-section-title::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c24a3a;
}

.analysis-table {
  border: 1px solid #e5e0da;
  border-radius: 12px;
  overflow: hidden;
  background: #fdfcfb;
}

.analysis-table-row {
  display: grid;
  grid-template-columns: repeat(7, minmax(70px, 1fr));
  gap: 6px;
  padding: 10px 12px;
  font-size: 13px;
  color: #6f6a64;
  border-bottom: 1px solid #eee8e1;
}

.analysis-table-row:last-child {
  border-bottom: none;
}

.analysis-table-head {
  background: #f2eeea;
  color: #6b6763;
  font-weight: 600;
}

.analysis-split {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  text-align: center;
  gap: 12px;
}

.analysis-number {
  font-size: 20px;
  font-weight: 700;
  color: #c24a3a;
}

.analysis-muted {
  font-size: 12px;
  color: #8b8680;
  margin-top: 4px;
}

.analysis-split-center {
  font-size: 12px;
  color: #8b8680;
  font-weight: 600;
}

.analysis-matrix {
  display: grid;
  gap: 12px;
}

.analysis-matrix-row {
  display: grid;
  grid-template-columns: 120px repeat(3, 1fr);
  gap: 8px;
  align-items: center;
  padding: 10px;
  border: 1px solid #e5e0da;
  border-radius: 12px;
  background: #fdfcfb;
}

.analysis-matrix-label {
  font-size: 13px;
  color: #6b6763;
  font-weight: 600;
}

.analysis-matrix-cell {
  text-align: center;
}

.analysis-heat {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
  gap: 12px;
}

.analysis-heat-item {
  border: 1px solid #e5e0da;
  border-radius: 12px;
  padding: 12px;
  text-align: center;
  background: #fdfcfb;
}

.analysis-left,
.analysis-right {
  display: grid;
  gap: 16px;
}

.analysis-title {
  font-size: 20px;
  font-weight: 700;
  color: #5a534e;
}

.analysis-subtitle {
  font-size: 13px;
  color: #8b8680;
  margin-top: 6px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.analysis-card,
.analysis-block {
  border: 1px solid #d6d2cb;
  border-radius: 10px;
  padding: 12px;
  background: #fdfcfb;
}

.analysis-card-title {
  font-size: 13px;
  font-weight: 600;
  color: #6b6763;
  margin-bottom: 8px;
}

.analysis-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
  color: #6f6a64;
  padding: 4px 0;
}

.analysis-row strong {
  color: #5a534e;
  font-weight: 600;
}

.bar {
  height: 8px;
  border-radius: 999px;
  background: #ebe7e1;
  overflow: hidden;
  margin: 6px 0 10px;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #aeb7bf, #8fa0b1);
}

.bar-fill--alt {
  background: linear-gradient(90deg, #c5b8a8, #a99683);
}

.analysis-list {
  display: grid;
  gap: 6px;
  font-size: 13px;
  color: #6f6a64;
}

.analysis-list-item {
  padding: 6px 8px;
  border-radius: 8px;
  background: #f7f5f1;
  border: 1px solid #e2ddd6;
}

@media (max-width: 900px) {
  .analysis-hero {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .analysis-columns {
    grid-template-columns: 1fr;
  }

  .analysis-table-row {
    grid-template-columns: repeat(3, minmax(70px, 1fr));
    row-gap: 8px;
  }

  .analysis-matrix-row {
    grid-template-columns: 1fr;
    text-align: left;
  }

  .analysis-matrix-cell {
    text-align: left;
  }
}

.analysis-empty {
  color: #8b8680;
  font-size: 14px;
  padding: 16px 0;
}

.pagination-total {
  margin-right: 12px;
  color: #6b6763;
  font-size: 13px;
}

:deep(.el-button) {
  transition: transform 0.15s ease, box-shadow 0.2s ease, background-color 0.2s ease, color 0.2s ease;
}

:deep(.el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(107, 103, 99, 0.2);
}

:deep(.el-button:active) {
  transform: translateY(0);
  box-shadow: 0 4px 10px rgba(107, 103, 99, 0.16);
}

:deep(.el-button--primary) {
  background-color: #d4b3a1;
  border-color: #d4b3a1;
  color: #4c4743;
}

:deep(.el-button--primary:hover) {
  background-color: #c9a595;
  border-color: #c9a595;
  color: #4c4743;
}

:deep(.el-button--success) {
  background-color: #aabead;
  border-color: #aabead;
  color: #4c4743;
}

:deep(.el-button--success:hover) {
  background-color: #9daf9f;
  border-color: #9daf9f;
  color: #4c4743;
}

:deep(.el-button--default) {
  background-color: #f3efe8;
  border-color: #d6d2cb;
  color: #6b6763;
}

:deep(.el-checkbox-button__inner) {
  background-color: #f6f3f0;
  border-color: #d6d2cb;
  color: #6b6763;
  transition: all 0.2s ease;
}

:deep(.el-checkbox-button__inner:hover) {
  border-color: #bfb8b0;
  color: #5a5652;
}

:deep(.el-checkbox-button.is-checked .el-checkbox-button__inner) {
  background-color: #d4b3a1;
  border-color: #c6a1a6;
  color: #4c4743;
  box-shadow: inset 0 0 0 1px rgba(107, 103, 99, 0.2);
}

:deep(.el-radio__inner) {
  border-color: #d6d2cb;
  background-color: #f6f3f0;
}

:deep(.el-radio__label) {
  color: #6b6763;
}

:deep(.el-radio__input.is-checked .el-radio__inner) {
  border-color: #9fb1c4;
  background-color: #9fb1c4;
}

:deep(.el-radio__input.is-checked + .el-radio__label) {
  color: #4c4743;
  font-weight: 600;
}
</style>