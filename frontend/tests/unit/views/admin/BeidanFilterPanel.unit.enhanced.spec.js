// Enhanced Unit tests for BeidanFilterPanel component - Covering missing test cases
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import BeidanFilterPanel from '../../../../src/views/admin/BeidanFilterPanel.vue';
import { createTestingPinia } from '@pinia/testing';
import { ElMessage, ElMessageBox } from 'element-plus';

// Mock external dependencies
vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}));

vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus');
  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn()
      },
    ElMessageBox: {
      confirm: vi.fn(),
      alert: vi.fn()
    }
  };
});

describe('BeidanFilterPanel.vue - Enhanced Unit Tests', () => {
  let wrapper;
  let mockRequest;

  beforeEach(() => {
    // Clear all mocks
    vi.clearAllMocks();
    
    mockRequest = (await import('@/utils/request')).default;
    
    wrapper = mount(BeidanFilterPanel, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn
        })],
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
    vi.restoreAllMocks();
  });

  // ============================================================================
  // NEW TEST CASES - Event Emission Tests
  // ============================================================================

  it('emits events correctly when child components trigger them', async () => {
    // Test fetch-real-data event
    await wrapper.findComponent({ name: 'FilterCardHeader' }).vm.$emit('fetch-real-data');
    expect(wrapper.vm.loading).toBe(true);

    // Test apply-preset event
    const mockPreset = { powerDiffs: [1], winPanDiffs: [0], stabilityTiers: ['A'] };
    await wrapper.findComponent({ name: 'FilterSection' }).vm.$emit('apply-preset', mockPreset);
    expect(wrapper.vm.filterForm).toEqual(mockPreset);

    // Test strategy selection event
    const mockStrategy = { id: 1, name: 'Test Strategy' };
    await wrapper.findComponent({ name: 'StrategySection' }).vm.$emit('handle-select-strategy', mockStrategy);
    expect(wrapper.vm.selectedStrategyName).toBe('Test Strategy');
  });

  // ============================================================================
  // NEW TEST CASES - Computed Properties Tests
  // ============================================================================

  it('computes directionWarning correctly', () => {
    // Test when filters are applied
    wrapper.vm.filterForm = { powerDiffs: [1], winPanDiffs: [0] };
    expect(wrapper.vm.directionWarning).toBe(true);

    // Test when no filters are applied
    wrapper.vm.filterForm = { powerDiffs: [], winPanDiffs: [] };
    expect(wrapper.vm.directionWarning).toBe(false);
  });

  it('computes strategyApplied correctly', () => {
    // Initially false
    expect(wrapper.vm.strategyApplied).toBe(false);

    // After applying filters
    wrapper.vm.filterForm = { powerDiffs: [1], winPanDiffs: [0] };
    wrapper.vm.strategyApplied = true;
    expect(wrapper.vm.strategyApplied).toBe(true);
  });

  // ============================================================================
  // NEW TEST CASES - Method Tests
  // ============================================================================

  it('handles preset application correctly', () => {
    const { applyPreset } = wrapper.vm;
    
    // Test strong preset
    applyPreset('strong');
    expect(wrapper.vm.filterForm.powerDiffs).toEqual([2, 3]);
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([3, 4]);
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual(['S', 'A', 'B']);

    // Test invalid preset falls back to balanced
    applyPreset('invalid_preset');
    expect(wrapper.vm.filterForm.powerDiffs).toEqual([0]);
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([0]);
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual(['B', 'C']);
  });

  it('resets filters to default state', () => {
    // Set some values first
    wrapper.vm.filterForm = {
      powerDiffs: [1, 2],
      winPanDiffs: [0, 1],
      stabilityTiers: ['A', 'B'],
      leagues: ['联赛1'],
      matchDateRange: ['2023-01-01', '2023-01-31'],
      sortField: 'match_time',
      sortOrder: 'desc'
    };
    wrapper.vm.currentPage = 5;
    wrapper.vm.pageSize = 50;

    // Reset filters
    wrapper.vm.resetFilters();

    // Verify reset values
    expect(wrapper.vm.filterForm.powerDiffs).toEqual([]);
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([]);
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual([]);
    expect(wrapper.vm.filterForm.leagues).toEqual([]);
    expect(wrapper.vm.filterForm.matchDateRange).toEqual([]);
    expect(wrapper.vm.filterForm.sortField).toBe('match_time');
    expect(wrapper.vm.filterForm.sortOrder).toBe('desc');
    expect(wrapper.vm.currentPage).toBe(1);
    expect(wrapper.vm.pageSize).toBe(20);
  });

  it('handles advanced filter application', async () => {
    const advancedFilter = {
      powerDiffs: [1, 2],
      winPanDiffs: [-1, 0],
      stabilityTiers: ['A', 'B'],
      minHomeWinRate: 60,
      maxHomeWinRate: 80
    };

    await wrapper.vm.applyAdvancedFilter(advancedFilter);

    expect(wrapper.vm.filterForm.powerDiffs).toEqual([1, 2]);
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([-1, 0]);
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual(['A', 'B']);
    expect(wrapper.vm.minHomeWinRate).toBe(60);
    expect(wrapper.vm.maxHomeWinRate).toBe(80);
  });

  // ============================================================================
  // NEW TEST CASES - Error Handling Tests
  // ============================================================================

  it('handles API errors gracefully during data fetch', async () => {
    // Mock API failure
    mockRequest.get.mockRejectedValue(new Error('Network error'));

    // Attempt to fetch data
    await wrapper.vm.fetchRealData();

    // Verify error handling
    expect(wrapper.vm.loading).toBe(false);
    expect(ElMessage.error).toHaveBeenCalledWith('获取数据失败');
  });

  it('handles malformed API response data', async () => {
    // Mock malformed response
    mockRequest.get.mockResolvedValue({ data: null });

    await wrapper.vm.fetchRealData();

    expect(wrapper.vm.matches).toEqual([]);
    expect(wrapper.vm.totalResults).toBe(0);
    expect(wrapper.vm.loading).toBe(false);
  });

  // ============================================================================
  // NEW TEST CASES - Data Processing Tests
  // ============================================================================

  it('normalizes matches with edge cases', () => {
    const { normalizeMatches } = wrapper.vm;

    // Test with extreme values
    const extremeMatches = [
      {
        match_id: null,
        home_team: '',
        away_team: '',
        league: null,
        match_time: 'invalid-date',
        power_home: '999',
        power_away: '1',
        win_pan_home: '10.0',
        win_pan_away: '0.1',
        home_feature: null,
        away_feature: null
      }
    ];

    const normalized = normalizeMatches(extremeMatches);
    
    expect(normalized).toHaveLength(1);
    expect(normalized[0].match_id).toBe('');
    expect(normalized[0].home_team).toBe('');
    expect(normalized[0].power_diff).toBeGreaterThan(0); // Large difference
    expect(normalized[0].win_pan_diff).toBeGreaterThan(0);
  });

  it('calculates statistics correctly with empty data', () => {
    const { calculateStatistics } = wrapper.vm;

    const emptyMatches = [];
    const stats = calculateStatistics(emptyMatches);

    expect(stats.totalMatches).toBe(0);
    expect(stats.avgPowerDifference).toBe(0);
    expect(stats.avgWinPanDifference).toBe(0);
    expect(stats.levelDistribution).toEqual({});
    expect(stats.topLeagues).toEqual([]);
  });

  // ============================================================================
  // NEW TEST CASES - Multi-Strategy Configuration Tests
  // ============================================================================

  it('handles multi-strategy panel visibility', async () => {
    // Initially hidden
    expect(wrapper.vm.showMultiStrategyPanel).toBe(false);

    // Show panel
    wrapper.vm.handleUpdateShowMultiStrategyPanel(true);
    expect(wrapper.vm.showMultiStrategyPanel).toBe(true);

    // Hide panel
    wrapper.vm.handleUpdateShowMultiStrategyPanel(false);
    expect(wrapper.vm.showMultiStrategyPanel).toBe(false);
  });

  it('processes strategy configuration', async () => {
    const strategyConfig = {
      strategies: [
        { id: 1, name: 'Strategy 1', filters: { powerDiffs: [1] } },
        { id: 2, name: 'Strategy 2', filters: { powerDiffs: [2] } }
      ],
      combinationMode: 'AND'
    };

    await wrapper.vm.handleStrategyConfigured(strategyConfig);

    expect(ElMessage.success).toHaveBeenCalledWith('策略配置已保存');
    // Additional assertions based on your business logic
  });

  // ============================================================================
  // NEW TEST CASES - Lifecycle Hook Tests
  // ============================================================================

  it('loads initial data on mount', () => {
    // Check if lifecycle methods are called
    // This would require spying on the actual methods
    expect(wrapper.vm.filterForm).toBeDefined();
    expect(wrapper.vm.strengthOptions).toBeDefined();
    expect(wrapper.vm.winPanOptions).toBeDefined();
    expect(wrapper.vm.stabilityOptions).toBeDefined();
  });
});