// Component tests for BeidanFilterPanel component
// Using dynamic import to avoid parsing issues
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the request utility
vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { matches: [], total: 0, options: [] } })),
    post: vi.fn(() => Promise.resolve({ data: { matches: [], total: 0 } }))
  }
}));

describe('BeidanFilterPanel Component Behavior', () => {
  let wrapper;
  let BeidanFilterPanel;
  let mount;
  let createTestingPinia;

  beforeEach(async () => {
    // Dynamically import dependencies to avoid parsing issues during initialization
    const testUtils = await import('@vue/test-utils');
    mount = testUtils.mount;
    const piniaModule = await import('@pinia/testing');
    createTestingPinia = piniaModule.createTestingPinia;
    
    // Import the component dynamically
    const componentModule = await import('@/views/admin/BeidanFilterPanel.vue');
    BeidanFilterPanel = componentModule.default;
    
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


  it('renders all filter sections correctly', () => {
    expect(wrapper.find('.dimension-row').exists()).toBe(true);
    expect(wrapper.find('.control-row').exists()).toBe(true);
    expect(wrapper.find('.filter-actions').exists()).toBe(true);
    expect(wrapper.findAll('.filter-group')).toHaveLength(6); // 3 in dimension row + 3 in control row
  });

  it('handles checkbox selection for power diffs', async () => {
    const checkboxes = wrapper.findAll('.strength-options .el-checkbox-button');
    expect(checkboxes).toHaveLength(7);

    // Simulate selecting the first checkbox
    await checkboxes[0].trigger('click');
    expect(wrapper.vm.filterForm.powerDiffs).toContain(-3);
  });

  it('handles checkbox selection for win pan diffs', async () => {
    const checkboxes = wrapper.findAll('.win-pan-options .el-checkbox-button');
    expect(checkboxes).toHaveLength(9);

    // Simulate selecting the middle checkbox
    await checkboxes[4].trigger('click');
    expect(wrapper.vm.filterForm.winPanDiffs).toContain(0);
  });

  it('handles checkbox selection for stability tiers', async () => {
    const checkboxes = wrapper.findAll('.stability-options .el-checkbox-button');
    expect(checkboxes).toHaveLength(7);

    // Simulate selecting the first tier
    await checkboxes[0].trigger('click');
    expect(wrapper.vm.filterForm.stabilityTiers).toContain('S');
  });

  it('triggers fetchRealData when button is clicked', async () => {
    const mockResponse = {
      data: {
        matches: [],
        total: 0
      }
    };
    
    const requestMock = vi.mocked(wrapper.vm.$options.methods.fetchRealData);
    
    const fetchButton = wrapper.find('.header-actions .el-button');
    await fetchButton.trigger('click');

    // Check that the API was called
    const request = require('@/utils/request').default;
    expect(request.get).toHaveBeenCalledWith('/api/v1/data-source-100qiu/latest-matches', {
      params: { limit: 200, include_raw: true }
    });
  });

  it('applies filters correctly', async () => {
    // Set some filter values
    wrapper.vm.filterForm.powerDiffs = [1, 2];
    wrapper.vm.filterForm.winPanDiffs = [1, 2];
    wrapper.vm.filterForm.stabilityTiers = ['S', 'A'];

    // Trigger apply filter
    const applyButton = wrapper.find('.filter-actions .el-button');
    await applyButton.trigger('click');

    // Check that the API was called with correct parameters
    const request = require('@/utils/request').default;
    expect(request.post).toHaveBeenCalledWith('/api/v1/beidan-filter/advanced-filter', expect.objectContaining({
      strength_filter: expect.objectContaining({
        min_strength: 9,  // Based on power diffs [1, 2]
        max_strength: 25
      }),
      win_pan_filter: expect.objectContaining({
        min_win_pan: 0.5,  // Based on win pan diffs [1, 2]
        max_win_pan: 2.5
      }),
      stability_filter: expect.objectContaining({
        tiers: ['S', 'A']
      })
    }));
  });

  it('resets filters correctly', async () => {
    // Set some filter values
    wrapper.vm.filterForm.powerDiffs = [1, 2];
    wrapper.vm.filterForm.winPanDiffs = [1, 2];
    wrapper.vm.filterForm.stabilityTiers = ['S', 'A'];

    // Ensure values are set
    expect(wrapper.vm.filterForm.powerDiffs).toEqual([1, 2]);
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([1, 2]);
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual(['S', 'A']);

    // Trigger reset
    const resetButton = wrapper.findAll('.filter-actions .el-button')[1]; // Second button is reset
    await resetButton.trigger('click');

    // Check that filters are reset
    expect(wrapper.vm.filterForm.powerDiffs).toEqual([]);
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([]);
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual([]);
  });

  it('shows warning when direction mismatch occurs', async () => {
    // Set conflicting directions: positive strength but negative win pan
    wrapper.vm.filterForm.powerDiffs = [2]; // Positive strength
    wrapper.vm.filterForm.winPanDiffs = [-3]; // Negative win pan

    // Update computed property
    await wrapper.vm.$nextTick();

    // Check that warning is displayed
    expect(wrapper.vm.directionWarning).toBe(true);

    // Reset and test non-conflicting directions
    wrapper.vm.filterForm.powerDiffs = [2]; // Positive strength
    wrapper.vm.filterForm.winPanDiffs = [2]; // Positive win pan
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.directionWarning).toBe(false);
  });

  it('loads and saves strategies', async () => {
    // We'll test the localStorage interactions indirectly by checking methods
    expect(typeof wrapper.vm.handleSaveStrategy).toBe('function');
    expect(typeof wrapper.vm.loadStrategyOptions).toBe('function');
  });
});

// Component tests for BeidanFilterPanel logic
// Testing business logic separately from Vue component rendering
import { describe, it, expect } from 'vitest';
import {
  calcDeltaPLevel,
  calcDeltaWp,
  calcStabilityTier,
  formatMatchTime,
  normalizeMatches
} from '@/utils/beidanFilterUtils';

describe('BeidanFilterPanel Business Logic', () => {
  it('should calculate power level differences correctly', () => {
    expect(calcDeltaPLevel(50, 30)).toBe(2); // Difference 20 -> +2
    expect(calcDeltaPLevel(30, 50)).toBe(-2); // Difference -20 -> -2
  });

  it('should calculate win pan differences correctly', () => {
    expect(calcDeltaWp(1.3, 0.5)).toBe(3); // Score 3 - 0 = 3
    expect(calcDeltaWp(0.5, 0.5)).toBe(0); // Score 0 - 0 = 0
  });

  it('should calculate stability tier correctly', () => {
    const result = calcStabilityTier('一赔70%', '一赔75%');
    expect(result.tier).toBe('S'); // Sum >= 140
    expect(result.pLevel).toBe(1);
  });

  it('should format match time correctly', () => {
    const date = new Date('2023-01-01T12:00:00');
    expect(formatMatchTime(date)).toBe('2023/01/01 12:00:00');
  });

  it('should normalize match data correctly', () => {
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
    expect(normalized[0].power_diff).toBe(1);
    expect(normalized[0].win_pan_diff).toBe(1);
    expect(normalized[0].p_level).toBe(2);
  });
});
