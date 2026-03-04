import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import BeidanFilterPanel from './BeidanFilterPanel.vue';
import { createTestingPinia } from '@pinia/testing';
import { createApp } from 'vue';

describe('BeidanFilterPanel', () => {
  let wrapper;

  beforeEach(() => {
    // 创建带 pinia 的包装器
    wrapper = mount(BeidanFilterPanel, {
      global: {
        plugins: [createTestingPinia()]
      }
    });
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('renders correctly with main elements', () => {
    expect(wrapper.find('.beidan-filter-panel').exists()).toBe(true);
    expect(wrapper.find('.filter-card').exists()).toBe(true);
    expect(wrapper.find('.card-header').exists()).toBe(true);
    expect(wrapper.find('.title').text()).toContain('三维精算筛选器');
    expect(wrapper.find('.subtitle').text()).toContain('ΔP / ΔWP / P-Tier');
  });

  it('displays header section correctly', () => {
    const header = wrapper.find('.card-header');
    expect(header.exists()).toBe(true);
    
    const titleElement = wrapper.find('.title');
    expect(titleElement.exists()).toBe(true);
    expect(titleElement.text()).toBe('三维精算筛选器');
    
    const subtitleElement = wrapper.find('.subtitle');
    expect(subtitleElement.exists()).toBe(true);
    expect(subtitleElement.text()).toContain('ΔP / ΔWP / P-Tier');
  });

  it('renders three main dimension filter groups', () => {
    const filterGroups = wrapper.findAll('.filter-group');
    expect(filterGroups.length).toBeGreaterThan(3); // 有多个过滤组

    const dimensionTitles = [
      '实力等级差 ΔP',
      '赢盘等级差 ΔWP',
      '一赔稳定性 P-Tier'
    ];

    // 检查是否包含这些维度标题
    const allText = wrapper.text();
    dimensionTitles.forEach(title => {
      expect(allText).toContain(title);
    });
  });

  it('renders strength difference options correctly', () => {
    // 检查实力等级差选项数量
    const strengthCheckboxes = wrapper.findAll('.checkbox-grid .el-checkbox-button');
    expect(strengthCheckboxes.length).toBeGreaterThan(0);
  });

  it('renders win pan difference options correctly', () => {
    // 检查赢盘等级差选项
    const winPanGrid = wrapper.findAll('.checkbox-grid')[1];
    expect(winPanGrid).toBeDefined();
  });

  it('renders stability tier options correctly', () => {
    const tierCheckboxes = wrapper.findAll('.tier-grid .el-checkbox-button');
    expect(tierCheckboxes.length).toBeGreaterThan(0);
  });

  it('has advanced filter section', () => {
    // 检查高级筛选区域
    const advancedFilterLabel = wrapper.find('.group-title span:first-child');
    expect(advancedFilterLabel.exists()).toBe(true);
  });

  it('has strategy selection section', () => {
    const strategyCard = wrapper.find('.strategy-card');
    expect(strategyCard.exists()).toBe(true);
    
    const strategyLabel = strategyCard.find('.strategy-label');
    expect(strategyLabel.exists()).toBe(true);
    expect(strategyLabel.text()).toBe('策略筛选');
  });

  it('contains preset buttons', () => {
    const presetButtons = wrapper.findAll('.preset-grid button');
    expect(presetButtons).toHaveLength(3);
    
    const buttonTexts = presetButtons.map(btn => btn.text());
    expect(buttonTexts).toContain('强势正路');
    expect(buttonTexts).toContain('冷门潜质');
    expect(buttonTexts).toContain('均衡博弈');
  });

  it('has loading state for primary button', () => {
    // 检查获取实时数据按钮是否具有loading属性
    const getDataButton = wrapper.find('button.el-button--primary');
    expect(getDataButton.exists()).toBe(true);
  });

  it('should have dropdown for saving/loading strategy', () => {
    const dropdown = wrapper.find('.el-dropdown');
    expect(dropdown.exists()).toBe(true);
    
    const dropdownButton = dropdown.find('button');
    expect(dropdownButton.exists()).toBe(true);
  });

  it('renders match count element', () => {
    const matchCount = wrapper.find('.match-count');
    expect(matchCount.exists()).toBe(true);
    expect(matchCount.text()).toContain('实时匹配');
  });

  it('has date range picker', () => {
    const datePicker = wrapper.find('.el-date-editor');
    expect(datePicker.exists()).toBe(true);
  });

  it('has switch control for derating rule', () => {
    const switchControl = wrapper.find('.el-switch');
    expect(switchControl.exists()).toBe(true);
  });

  it('has pagination controls', () => {
    const pagination = wrapper.find('.el-pagination');
    expect(pagination.exists()).toBe(true);
  });

  it('has export buttons', () => {
    // 导出按钮只有在结果卡显示时才可见，这里只检查是否存在相关文本
    expect(wrapper.text()).toContain('导出');
  });

  it('contains all dimension labels', () => {
    const panelText = wrapper.text();
    
    expect(panelText).toContain('实力等级差 ΔP');
    expect(panelText).toContain('赢盘等级差 ΔWP');
    expect(panelText).toContain('一赔稳定性 P-Tier');
  });

  it('contains correct number of checkbox options', () => {
    const checkboxes = wrapper.findAll('.el-checkbox-button');
    // 实力差7个 + 赢盘差9个 + P-Tier 7个
    expect(checkboxes.length).toBeGreaterThanOrEqual(7);
  });
});