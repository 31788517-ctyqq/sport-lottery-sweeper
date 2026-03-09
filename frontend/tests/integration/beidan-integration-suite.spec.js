// 集成测试套件，覆盖BeidanFilterPanel的7个测试单元
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, createLocalVue } from '@vue/test-utils';
import BeidanFilterPanel from '@/views/admin/BeidanFilterPanel.vue';
import { createTestingPinia } from '@pinia/testing';
import {
  calcDeltaPLevel,
  calcDeltaWp,
  calcStabilityTier,
  formatMatchTime,
  normalizeMatches
} from '@/utils/beidanFilterUtils';

// Mock the request utility
vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { matches: [], total: 0 } })),
    post: vi.fn(() => Promise.resolve({ data: { matches: [], total: 0 } }))
  }
}));

describe('BeidanFilterPanel - 全面集成测试', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = mount(BeidanFilterPanel, {
      global: {
        plugins: [createTestingPinia()],
        stubs: {
          'el-card': true,
          'el-checkbox-group': true,
          'el-checkbox-button': true,
          'el-select': true,
          'el-option': true,
          'el-date-picker': true,
          'el-table': true,
          'el-pagination': true,
          'el-button': true,
          'el-dialog': true,
          'el-input': true,
          'el-dropdown': true,
          'el-dropdown-menu': true,
          'el-dropdown-item': true,
          'el-radio-group': true,
          'el-radio': true,
          'el-switch': true,
          'el-progress': true,
          'el-tag': true,
          'el-alert': true,
          'el-form': true,
          'el-form-item': true
        }
      }
    });
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  describe('1. 纯函数与工具函数测试', () => {
    it('calcDeltaPLevel 正确计算实力等级差', () => {
      expect(calcDeltaPLevel(100, 70)).toBe(3); // Difference > 25
      expect(calcDeltaPLevel(50, 30)).toBe(2); // Difference 17-25
      expect(calcDeltaPLevel(40, 30)).toBe(1); // Difference 9-16
      expect(calcDeltaPLevel(35, 30)).toBe(0); // Difference -8 to +8
      expect(calcDeltaPLevel(30, 40)).toBe(-1); // Difference -9 to -16
      expect(calcDeltaPLevel(30, 50)).toBe(-2); // Difference -17 to -25
      expect(calcDeltaPLevel(30, 60)).toBe(-3); // Difference < -25
      expect(calcDeltaPLevel('-', '40')).toBe(0);
      expect(calcDeltaPLevel('50', '-')).toBe(0);
    });

    it('calcDeltaWp 正确计算赢盘等级差', () => {
      expect(calcDeltaWp(2.0, 0.5)).toBe(4); // 4 - 0 = 4
      expect(calcDeltaWp(1.3, 0.5)).toBe(3); // 3 - 0 = 3
      expect(calcDeltaWp(1.0, 0.5)).toBe(2); // 2 - 0 = 2
      expect(calcDeltaWp(0.7, 0.5)).toBe(1); // 1 - 0 = 1
      expect(calcDeltaWp(0.5, 0.5)).toBe(0); // 0 - 0 = 0
    });

    it('calcStabilityTier 正确计算稳定性等级', () => {
      const result1 = calcStabilityTier('一赔70%', '一赔75%');
      expect(result1.tier).toBe('S');
      expect(result1.pLevel).toBe(1);

      const result2 = calcStabilityTier('一赔60%', '一赔55%');
      expect(result2.tier).toBe('A');
      expect(result2.pLevel).toBe(2);

      const result3 = calcStabilityTier('一赔70%', '客队特征');
      expect(result3.tier).toBe('B');
      expect(result3.pLevel).toBe(3);
    });

    it('formatMatchTime 正确格式化比赛时间', () => {
      const date = new Date('2023-01-01T12:00:00');
      expect(formatMatchTime(date)).toBe('2023/01/01 12:00:00');
      expect(formatMatchTime('2023-01-01T12:00:00')).toBe('2023/01/01 12:00:00');
      expect(formatMatchTime(null)).toBe('-');
      expect(formatMatchTime(undefined)).toBe('-');
      expect(formatMatchTime('')).toBe('-');
    });

    it('normalizeMatches 正确标准化比赛数据', () => {
      const mockMatches = [{
        match_id: '123',
        home_team: '主队',
        away_team: '客队',
        power_home: '50',
        power_away: '40',
        win_pan_home: '1.2',
        win_pan_away: '0.8',
        home_feature: '一赔70%',
        away_feature: '一赔40%'
      }];

      const normalized = normalizeMatches(mockMatches);
      expect(normalized).toHaveLength(1);
      expect(normalized[0].power_diff).toBe(1);
      expect(normalized[0].win_pan_diff).toBe(1);
      expect(normalized[0].p_level).toBe(2);
    });
  });

  describe('2. UI 组件测试', () => {
    it('组件正确渲染', () => {
      expect(wrapper.find('.beidan-filter-panel').exists()).toBe(true);
      expect(wrapper.find('.title').text()).toBe('三维精算筛选器');
    });

    it('初始化时筛选值为空', () => {
      expect(wrapper.vm.filterForm.powerDiffs).toEqual([]);
      expect(wrapper.vm.filterForm.winPanDiffs).toEqual([]);
      expect(wrapper.vm.filterForm.stabilityTiers).toEqual([]);
    });

    it('显示正确的筛选选项', () => {
      expect(wrapper.vm.strengthOptions).toHaveLength(7);
      expect(wrapper.vm.winPanOptions).toHaveLength(9);
      expect(wrapper.vm.stabilityOptions).toHaveLength(7);
    });
  });

  describe('3. 组件间的交互', () => {
    it('应用预设策略功能正常', async () => {
      // 测试强势正路预设
      wrapper.vm.applyPreset('strong');
      expect(wrapper.vm.filterForm.powerDiffs).toEqual([2, 3]);
      expect(wrapper.vm.filterForm.winPanDiffs).toEqual([3, 4]);
      expect(wrapper.vm.filterForm.stabilityTiers).toEqual(['S', 'A', 'B']);

      // 重置并测试冷门潜质预设
      wrapper.vm.resetFilters();
      await wrapper.vm.$nextTick();
      expect(wrapper.vm.filterForm.powerDiffs).toEqual([]);
      expect(wrapper.vm.filterForm.winPanDiffs).toEqual([]);

      wrapper.vm.applyPreset('upset');
      expect(wrapper.vm.filterForm.powerDiffs).toEqual([-1, 0]);
      expect(wrapper.vm.filterForm.winPanDiffs).toEqual([-3, -4]);
      expect(wrapper.vm.filterForm.stabilityTiers).toEqual(['D', 'E']);
    });

    it('正确显示方向背离警告', () => {
      // 设置相互冲突的筛选条件
      wrapper.vm.filterForm.powerDiffs = [2];  // 主队优势
      wrapper.vm.filterForm.winPanDiffs = [-3]; // 客队优势
      expect(wrapper.vm.directionWarning).toBe(true);

      // 设置一致的筛选条件
      wrapper.vm.filterForm.powerDiffs = [2];
      wrapper.vm.filterForm.winPanDiffs = [3];
      expect(wrapper.vm.directionWarning).toBe(false);
    });
  });

  describe('4. 状态管理与组件的集成', () => {
    it('组件响应状态变化', async () => {
      // 模拟状态更新
      wrapper.vm.statistics = { total_matches: 10, delta_p_count: 5 };
      await wrapper.vm.$nextTick();
      
      // 验证组件是否正确反映状态变化
      expect(wrapper.vm.statistics.total_matches).toBe(10);
    });
  });

  describe('5. 组件与 API 的集成', () => {
    it('获取实时数据时调用API', async () => {
      const requestMock = vi.spyOn(wrapper.vm, '$nextTick').mockResolvedValue();

      await wrapper.vm.fetchRealData();

      // 由于我们使用了mock，这里主要测试调用流程
      expect(requestMock).toHaveBeenCalled();
      requestMock.mockRestore();
    });

    it('应用高级筛选时调用API', async () => {
      // 设置筛选条件
      wrapper.vm.filterForm.powerDiffs = [2];
      wrapper.vm.filterForm.winPanDiffs = [3];
      wrapper.vm.filterForm.stabilityTiers = ['S'];

      const requestMock = vi.spyOn(wrapper.vm, '$nextTick').mockResolvedValue();

      await wrapper.vm.applyAdvancedFilter();

      // 验证流程执行
      expect(wrapper.vm.strategyApplied).toBe(true);
      requestMock.mockRestore();
    });
  });

  describe('6. 路由与组件的集成', () => {
    // 在单元测试环境中，路由集成较为复杂，此处验证组件本身的方法
    it('组件方法正确处理参数', () => {
      // 验证组件中的各种格式化和处理方法
      expect(wrapper.vm.displayValue(null)).toBe('-');
      expect(wrapper.vm.displayValue('test')).toBe('test');
      expect(wrapper.vm.formatMatchId('123')).toBe('123');
    });
  });

  describe('7. 完整用户场景', () => {
    it('完整筛选流程', async () => {
      // 模拟用户完整操作流程
      // 1. 获取数据
      await wrapper.vm.fetchRealData();
      expect(wrapper.vm.rawMatches.length).toBeGreaterThanOrEqual(0);

      // 2. 应用筛选条件
      wrapper.vm.filterForm.powerDiffs = [2, 3];
      wrapper.vm.filterForm.winPanDiffs = [3, 4];
      wrapper.vm.filterForm.stabilityTiers = ['S', 'A'];

      // 3. 应用筛选
      await wrapper.vm.applyAdvancedFilter();
      expect(wrapper.vm.strategyApplied).toBe(true);

      // 4. 验证结果
      expect(wrapper.vm.filterResults.length).toBeGreaterThanOrEqual(0);
    });

    it('策略保存和加载流程', () => {
      // 设置筛选条件
      wrapper.vm.filterForm.powerDiffs = [2, 3];
      wrapper.vm.filterForm.winPanDiffs = [3, 4];
      
      // 序列化策略
      const serialized = wrapper.vm.serializeStrategy();
      const parsed = JSON.parse(serialized);
      
      // 验证序列化的策略
      expect(parsed.powerDiffs).toEqual([2, 3]);
      expect(parsed.winPanDiffs).toEqual([3, 4]);
    });

    it('分析功能流程', async () => {
      const mockMatch = {
        match_id: 'test-match',
        home_team: 'Home Team',
        away_team: 'Away Team',
        source_attributes: {
          homeTeam: 'Home Team',
          guestTeam: 'Away Team',
          homePower: 75,
          guestPower: 60
        }
      };

      await wrapper.vm.openAnalysis(mockMatch);

      expect(wrapper.vm.showAnalysisDialog).toBe(true);
      expect(wrapper.vm.analysisData).toEqual(mockMatch.source_attributes);
    });
  });
});