// Enhanced Integration tests for BeidanFilterPanel component interactions
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import { nextTick } from 'vue';
import BeidanFilterPanel from '../../../../src/views/admin/BeidanFilterPanel.vue';

// Mock child components to test interactions
vi.mock('./components/FilterCardHeader.vue', () => ({
  default: {
    name: 'FilterCardHeader',
    template: '<div class="filter-card-header"><slot /></div>',
    emits: ['fetch-real-data']
  }
}));

vi.mock('./components/FilterSection.vue', () => ({
  default: {
    name: 'FilterSection',
    template: '<div class="filter-section"><slot /></div>',
    props: ['filterForm', 'loading', 'directionWarning'],
    emits: ['apply-preset', 'handle-save-strategy', 'apply-advanced-filter', 'reset-filters']
  }
}));

vi.mock('./components/StrategySection.vue', () => ({
  default: {
    name: 'StrategySection',
    template: '<div class="strategy-section"><slot /></div>',
    props: ['selectedStrategyName', 'strategyOptions'],
    emits: ['handle-select-strategy', 'load-strategy-options']
  }
}));

vi.mock('./components/StatsCard.vue', () => ({
  default: {
    name: 'StatsCard',
    template: '<div class="stats-card"><slot /></div>',
    props: ['statistics', 'filterForm']
  }
}));

vi.mock('./components/ResultsSection.vue', () => ({
  default: {
    name: 'ResultsSection',
    template: '<div class="results-section"><slot /></div>',
    props: ['pagedResults', 'loading', 'showStats', 'totalResults', 'currentPage', 'pageSize'],
    emits: ['toggle-stats', 'export-results', 'handle-sort-change', 'handle-size-change', 'handle-current-change', 'open-analysis']
  }
}));

vi.mock('./components/MultiStrategyConfig.vue', () => ({
  default: {
    name: 'MultiStrategyConfig',
    template: '<div class="multi-strategy-config"><slot /></div>',
    props: ['showMultiStrategyPanel'],
    emits: ['update:show-multi-strategy-panel', 'strategy-configured']
  }
}));

describe('BeidanFilterPanel.vue - Component Integration Tests', () => {
  let wrapper;
  let mockStore;

  beforeEach(() => {
    mockStore = createTestingPinia({
      createSpy: vi.fn,
      initialState: {
        user: {
          userInfo: { role: 'admin' }
        }
      }
    });

    wrapper = mount(BeidanFilterPanel, {
      global: {
        plugins: [mockStore],
        stubs: {
          'el-card': true,
          'el-dialog': true,
          'el-table': true,
          'el-pagination': true
        }
      }
    });
  });

  // ============================================================================
  // INTEGRATION TESTS - Component Communication
  // ============================================================================

  it('coordinates data flow between FilterCardHeader and parent component', async () => {
    // Simulate fetching real data
    const headerComponent = wrapper.findComponent({ name: 'FilterCardHeader' });
    await headerComponent.vm.$emit('fetch-real-data');

    // Verify parent component state changes
    expect(wrapper.vm.loading).toBe(true);
    
    // Simulate async data loading completion
    await wrapper.setData({ loading: false, matches: [{ match_id: '1' }] });
    expect(wrapper.vm.totalResults).toBe(1);
  });

  it('propagates filter changes from FilterSection to parent and ResultsSection', async () => {
    const filterSection = wrapper.findComponent({ name: 'FilterSection' });
    const mockFilters = {
      powerDiffs: [1, 2],
      winPanDiffs: [0, 1],
      stabilityTiers: ['A', 'B'],
      leagues: ['英超'],
      matchDateRange: ['2023-01-01', '2023-01-31']
    };

    // Apply filters
    await filterSection.vm.$emit('apply-preset', mockFilters);
    
    // Verify filters are set in parent
    expect(wrapper.vm.filterForm).toEqual(mockFilters);
    expect(wrapper.vm.strategyApplied).toBe(true);

    // Verify ResultsSection receives updated props (when it becomes visible)
    await wrapper.setData({ strategyApplied: true });
    const resultsSection = wrapper.findComponent({ name: 'ResultsSection' });
    expect(resultsSection.props('totalResults')).toBe(0); // Initially 0 until data loads
  });

  it('handles strategy selection and cascades to filter application', async () => {
    const strategySection = wrapper.findComponent({ name: 'StrategySection' });
    const mockStrategy = {
      id: 1,
      name: 'High Confidence Strategy',
      config: {
        powerDiffs: [2, 3],
        winPanDiffs: [3, 4],
        stabilityTiers: ['S', 'A']
      }
    };

    // Select strategy
    await strategySection.vm.$emit('handle-select-strategy', mockStrategy);
    
    // Verify strategy name is displayed
    expect(wrapper.vm.selectedStrategyName).toBe('High Confidence Strategy');
    
    // Verify filters are automatically applied
    expect(wrapper.vm.filterForm.powerDiffs).toEqual([2, 3]);
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([3, 4]);
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual(['S', 'A']);
  });

  it('integrates StatsCard display with filter results', async () => {
    // Setup test data
    const testMatches = [
      {
        match_id: '1',
        home_team: 'Team A',
        away_team: 'Team B',
        league: 'Premier League',
        match_time: '2023-01-01T15:00:00',
        power_home: '80',
        power_away: '60',
        win_pan_home: '1.5',
        win_pan_away: '0.8',
        home_feature: '一赔70%',
        away_feature: '一赔40%'
      }
    ];

    // Load data and apply filters
    await wrapper.setData({
      matches: testMatches,
      filteredMatches: testMatches,
      strategyApplied: true,
      showStats: true
    });

    // Verify StatsCard receives correct props
    const statsCard = wrapper.findComponent({ name: 'StatsCard' });
    expect(statsCard.exists()).toBe(true);
    expect(statsCard.props('statistics')).toBeDefined();
    expect(statsCard.props('filterForm')).toEqual(wrapper.vm.filterForm);
  });

  it('coordinates pagination between ResultsSection and parent component', async () => {
    // Setup paginated data
    const testMatches = Array.from({ length: 25 }, (_, i) => ({
      match_id: `${i + 1}`,
      home_team: `Team ${i + 1}A`,
      away_team: `Team ${i + 1}B`,
      league: 'Test League',
      match_time: '2023-01-01T15:00:00',
      power_home: '70',
      power_away: '60',
      win_pan_home: '1.2',
      win_pan_away: '0.9',
      home_feature: '一赔60%',
      away_feature: '一赔50%'
    }));

    await wrapper.setData({
      matches: testMatches,
      filteredMatches: testMatches,
      strategyApplied: true,
      currentPage: 1,
      pageSize: 10,
      totalResults: testMatches.length
    });

    // Test page size change
    const resultsSection = wrapper.findComponent({ name: 'ResultsSection' });
    await resultsSection.vm.$emit('handle-size-change', 20);
    
    expect(wrapper.vm.pageSize).toBe(20);
    expect(wrapper.vm.currentPage).toBe(1); // Should reset to first page

    // Test page change
    await resultsSection.vm.$emit('handle-current-change', 2);
    expect(wrapper.vm.currentPage).toBe(2);
  });

  it('integrates MultiStrategyConfig component workflow', async () => {
    // Initially hidden
    expect(wrapper.vm.showMultiStrategyPanel).toBe(false);
    expect(wrapper.findComponent({ name: 'MultiStrategyConfig' }).exists()).toBe(false);

    // Show multi-strategy panel
    wrapper.vm.handleUpdateShowMultiStrategyPanel(true);
    await nextTick();
    
    expect(wrapper.vm.showMultiStrategyPanel).toBe(true);
    expect(wrapper.findComponent({ name: 'MultiStrategyConfig' }).exists()).toBe(true);

    // Configure strategy
    const strategyConfig = {
      strategies: [
        { id: 1, name: 'Strategy A', enabled: true },
        { id: 2, name: 'Strategy B', enabled: false }
      ],
      combinationMode: 'OR'
    };

    await wrapper.findComponent({ name: 'MultiStrategyConfig' }).vm.$emit('strategy-configured', strategyConfig);
    
    // Verify configuration was processed
    // Add assertions based on your multi-strategy logic
    expect(wrapper.vm.showMultiStrategyPanel).toBe(false); // Should close after configuration
  });

  // ============================================================================
  // INTEGRATION TESTS - Event Chain Reactions
  // ============================================================================

  it('handles complete filter workflow: apply -> results -> stats -> export', async () => {
    // Step 1: Apply filters
    const filterSection = wrapper.findComponent({ name: 'FilterSection' });
    const filters = {
      powerDiffs: [1],
      winPanDiffs: [0],
      stabilityTiers: ['A']
    };
    
    await filterSection.vm.$emit('apply-preset', filters);
    expect(wrapper.vm.strategyApplied).toBe(true);

    // Step 2: Simulate results display
    const testMatches = [{ match_id: '1', home_team: 'A', away_team: 'B' }];
    await wrapper.setData({
      filteredMatches: testMatches,
      totalResults: 1,
      pagedResults: testMatches
    });

    // Step 3: Show stats
    wrapper.vm.toggleStats(true);
    await nextTick();
    expect(wrapper.vm.showStats).toBe(true);

    // Step 4: Export results
    const resultsSection = wrapper.findComponent({ name: 'ResultsSection' });
    await resultsSection.vm.$emit('export-results');
    
    // Verify export functionality was triggered
    // Add assertions for export logic
  });

  it('manages component visibility based on application state', async () => {
    // Initially, only FilterCardHeader and FilterSection should be visible
    expect(wrapper.findComponent({ name: 'FilterCardHeader' }).exists()).toBe(true);
    expect(wrapper.findComponent({ name: 'FilterSection' }).exists()).toBe(true);
    expect(wrapper.findComponent({ name: 'StrategySection' }).exists()).toBe(true);
    expect(wrapper.findComponent({ name: 'StatsCard' }).exists()).toBe(false);
    expect(wrapper.findComponent({ name: 'ResultsSection' }).exists()).toBe(false);
    expect(wrapper.findComponent({ name: 'MultiStrategyConfig' }).exists()).toBe(false);

    // After applying filters, StatsCard and ResultsSection should appear
    await wrapper.setData({ strategyApplied: true, showStats: true });
    expect(wrapper.findComponent({ name: 'StatsCard' }).exists()).toBe(true);
    expect(wrapper.findComponent({ name: 'ResultsSection' }).exists()).toBe(true);

    // StatsCard should disappear when toggled off
    wrapper.vm.toggleStats(false);
    await nextTick();
    expect(wrapper.findComponent({ name: 'StatsCard' }).exists()).toBe(false);
  });

  // ============================================================================
  // INTEGRATION TESTS - Error Propagation
  // ============================================================================

  it('propagates loading states across all components', async () => {
    // Start loading
    await wrapper.findComponent({ name: 'FilterCardHeader' }).vm.$emit('fetch-real-data');
    expect(wrapper.vm.loading).toBe(true);

    // All relevant components should reflect loading state
    const filterSection = wrapper.findComponent({ name: 'FilterSection' });
    expect(filterSection.props('loading')).toBe(true);

    // Complete loading
    await wrapper.setData({ loading: false });
    expect(filterSection.props('loading')).toBe(false);
  });

  it('handles direction warning propagation correctly', async () => {
    const filterSection = wrapper.findComponent({ name: 'FilterSection' });
    
    // Initially no warning (no filters)
    expect(filterSection.props('directionWarning')).toBe(false);

    // Apply filters - should trigger warning
    await filterSection.vm.$emit('apply-preset', {
      powerDiffs: [1],
      winPanDiffs: [0]
    });
    
    expect(filterSection.props('directionWarning')).toBe(true);

    // Reset filters - warning should disappear
    await filterSection.vm.$emit('reset-filters');
    expect(filterSection.props('directionWarning')).toBe(false);
  });
});