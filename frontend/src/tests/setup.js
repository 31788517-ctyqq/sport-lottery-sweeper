// AI_WORKING: coder1 @2026-01-30 14:30:00 - 移除手动全局变量设置，依赖vitest.config.mjs中的globals:true
import { expect, vi, test, describe, it, beforeEach, afterEach } from 'vitest'
import { createTestingPinia } from '@pinia/testing'
import { config } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { ElButton, ElTable, ElTableColumn, ElTag, ElInput, ElSelect, ElOption, ElDatePicker, ElCard, ElRow, ElCol, ElPagination, ElDialog, ElFormItem, ElForm } from 'element-plus'

// 注册Element Plus全局组件
config.global.plugins = [ElementPlus]
config.global.components = {
  ElButton,
  ElTable,
  ElTableColumn,
  ElTag,
  ElInput,
  ElSelect,
  ElOption,
  ElDatePicker,
  ElCard,
  ElRow,
  ElCol,
  ElPagination,
  ElDialog,
  ElFormItem,
  ElForm
}

// 模拟浏览器 API - 如果 jsdom 已提供这些，这里只是增强
if (typeof window !== 'undefined') {
  // 确保 scrollTo 存在
  if (!window.scrollTo) {
    window.scrollTo = vi.fn()
  }
  
  // 确保 localStorage 存在
  if (!window.localStorage) {
    window.localStorage = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn()
    }
  }
  
  // 确保 matchMedia 存在
  if (!window.matchMedia) {
    window.matchMedia = vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }))
  }
}

// 模拟 ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// 全局测试工具
global.createTestPinia = () => createTestingPinia({
  createSpy: vi.fn,
  initialState: {
    auth: { user: null, token: null, loading: false },
    matches: { matches: [], loading: false },
    bets: { bets: [], loading: false }
  }
})