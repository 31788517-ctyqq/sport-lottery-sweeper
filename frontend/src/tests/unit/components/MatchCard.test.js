// AI_WORKING: coder1 @2026-01-29 18:40:00 - 重建 MatchCard 测试文件
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import MatchCard from '../../components/MatchCard.vue'

// 模拟全局对象
global.alert = vi.fn()

describe('MatchCard.vue', () => {
  let wrapper
  const mockMatch = {
    id: 1,
    league_name: '英超',
    home_team: '曼城',
    away_team: '阿森纳',
    match_time: '2024-01-22 20:00:00',
    home_score: null,
    away_score: null,
    status: '未开始',
    is_favorite: false
  }
  
  beforeEach(() => {
    vi.clearAllMocks()
    
    wrapper = mount(MatchCard, {
      props: {
        match: mockMatch
      },
      global: {
        mocks: {
          $t: (key) => key
        },
        stubs: {
          'el-card': true,
          'el-tag': true,
          'el-button': true,
          'el-icon': true
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('组件渲染', () => {
    it('应该正确渲染比赛信息', () => {
      expect(wrapper.text()).toContain('曼城')
      expect(wrapper.text()).toContain('阿森纳')
      expect(wrapper.text()).toContain('英超')
    })

    it('应该显示比赛时间', () => {
      expect(wrapper.text()).toContain('2024-01-22')
    })

    it('应该显示比赛状态', () => {
      expect(wrapper.text()).toContain('未开始')
    })
  })

  describe('比赛状态显示', () => {
    it('进行中比赛应该显示不同样式', async () => {
      const liveMatch = { ...mockMatch, status: '进行中', home_score: 1, away_score: 0 }
      await wrapper.setProps({ match: liveMatch })
      
      expect(wrapper.text()).toContain('1')
      expect(wrapper.text()).toContain('0')
      expect(wrapper.text()).toContain('进行中')
    })

    it('已结束比赛应该显示最终比分', async () => {
      const finishedMatch = { ...mockMatch, status: '已结束', home_score: 2, away_score: 1 }
      await wrapper.setProps({ match: finishedMatch })
      
      expect(wrapper.text()).toContain('2')
      expect(wrapper.text()).toContain('1')
      expect(wrapper.text()).toContain('已结束')
    })
  })

  describe('收藏功能', () => {
    it('未收藏比赛应该显示收藏按钮', () => {
      expect(wrapper.find('.favorite-btn').exists()).toBe(true)
    })

    it('点击收藏按钮应该触发事件', async () => {
      const favoriteBtn = wrapper.find('.favorite-btn')
      if (favoriteBtn.exists()) {
        await favoriteBtn.trigger('click')
        expect(wrapper.emitted('toggle-favorite')).toBeTruthy()
        expect(wrapper.emitted('toggle-favorite')[0]).toEqual([mockMatch.id])
      }
    })

    it('已收藏比赛应该显示取消收藏按钮', async () => {
      const favoritedMatch = { ...mockMatch, is_favorite: true }
      await wrapper.setProps({ match: favoritedMatch })
      
      expect(wrapper.text()).toContain('已收藏')
    })
  })

  describe('点击事件', () => {
    it('点击比赛卡片应该触发选择事件', async () => {
      await wrapper.trigger('click')
      expect(wrapper.emitted('select')).toBeTruthy()
      expect(wrapper.emitted('select')[0]).toEqual([mockMatch])
    })

    it('点击收藏按钮不应该触发选择事件', async () => {
      const favoriteBtn = wrapper.find('.favorite-btn')
      if (favoriteBtn.exists()) {
        await favoriteBtn.trigger('click')
        expect(wrapper.emitted('toggle-favorite')).toBeTruthy()
        expect(wrapper.emitted('select')).toBeFalsy()
      }
    })
  })
})
// AI_DONE: coder1 @2026-01-29 18:40:00
