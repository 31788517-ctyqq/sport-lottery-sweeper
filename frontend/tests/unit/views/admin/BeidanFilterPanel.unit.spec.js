// Unit tests for BeidanFilterPanel component
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import BeidanFilterPanel from '@/views/admin/BeidanFilterPanel.vue';
import { createTestingPinia } from '@pinia/testing';

// Mock the request utility
vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}));

describe('BeidanFilterPanel.vue', () => {
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

  it('renders correctly', () => {
    expect(wrapper.find('.beidan-filter-panel').exists()).toBe(true);
    expect(wrapper.find('.title').text()).toBe('三维精算筛选器');
  });

  it('initializes with empty filter values', () => {
    expect(wrapper.vm.filterForm.powerDiffs).toEqual([]);
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([]);
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual([]);
  });

  it('correctly calculates strength difference', () => {
    const calcDeltaPLevel = wrapper.vm.calcDeltaPLevel;
    expect(calcDeltaPLevel(100, 70)).toBe(3); // Difference > 25
    expect(calcDeltaPLevel(50, 30)).toBe(2); // Difference 17-25
    expect(calcDeltaPLevel(40, 30)).toBe(1); // Difference 9-16
    expect(calcDeltaPLevel(35, 30)).toBe(0); // Difference -8 to +8
    expect(calcDeltaPLevel(30, 40)).toBe(-1); // Difference -9 to -16
    expect(calcDeltaPLevel(30, 50)).toBe(-2); // Difference -17 to -25
    expect(calcDeltaPLevel(30, 60)).toBe(-3); // Difference < -25
  });

  it('correctly calculates win pan difference', () => {
    const calcDeltaWp = wrapper.vm.calcDeltaWp;
    expect(calcDeltaWp(2.0, 0.5)).toBe(3); // 4 - 1 = 3
    expect(calcDeltaWp(1.3, 0.5)).toBe(2); // 3 - 1 = 2
    expect(calcDeltaWp(1.0, 0.5)).toBe(1); // 2 - 1 = 1
    expect(calcDeltaWp(0.7, 0.5)).toBe(0); // 1 - 1 = 0
    expect(calcDeltaWp(0.5, 0.5)).toBe(0); // 0 - 0 = 0
  });

  it('correctly formats match time', () => {
    const formatMatchTime = wrapper.vm.formatMatchTime;
    
    // Test valid date
    const date = new Date('2023-01-01T12:00:00');
    expect(formatMatchTime(date)).toBe('2023/01/01 12:00:00');
    
    // Test ISO string
    expect(formatMatchTime('2023-01-01T12:00:00')).toBe('2023/01/01 12:00:00');
    
    // Test empty values
    expect(formatMatchTime(null)).toBe('-');
    expect(formatMatchTime(undefined)).toBe('-');
    expect(formatMatchTime('')).toBe('-');
  });

  it('applies preset strategies correctly', () => {
    // Test strong preset
    wrapper.vm.applyPreset('strong');
    expect(wrapper.vm.filterForm.powerDiffs).toEqual([2, 3]);
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([3, 4]);
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual(['S', 'A', 'B']);

    // Reset and test upset preset
    wrapper.vm.resetFilters();
    wrapper.vm.applyPreset('upset');
    expect(wrapper.vm.filterForm.powerDiffs).toEqual([-1, 0]);
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([-3, -4]);
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual(['D', 'E']);

    // Reset and test balance preset
    wrapper.vm.resetFilters();
    wrapper.vm.applyPreset('balance');
    expect(wrapper.vm.filterForm.powerDiffs).toEqual([0]);
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([0]);
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual(['B', 'C']);
  });

  it('normalizes matches correctly', () => {
    const mockMatches = [{
      match_id: '123',
      home_team: '主队',
      away_team: '客队',
      league: '联赛',
      match_time: '2023-01-01T12:00:00',
      power_home: '50',
      power_away: '40',
      win_pan_home: '1.2',
      win_pan_away: '0.8',
      home_feature: '一赔70%',
      away_feature: '一赔40%'
    }];

    const normalized = wrapper.vm.normalizeMatches(mockMatches);
    expect(normalized).toHaveLength(1);
    expect(normalized[0].power_diff).toBe(1); // 50-40=10 -> +1
    expect(normalized[0].win_pan_diff).toBe(1); // 1.2 -> 2, 0.8 -> 1, 2-1=1
    expect(normalized[0].p_level).toBe(2); // 70+40=110 -> P2
  });

  it('displays value correctly when null', () => {
    const displayValue = wrapper.vm.displayValue;
    expect(displayValue(null)).toBe('-');
    expect(displayValue(undefined)).toBe('-');
    expect(displayValue('')).toBe('-');
    expect(displayValue('test')).toBe('test');
  });
});