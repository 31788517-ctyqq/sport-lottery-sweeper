import { expect, vi } from 'vitest'
import { createTestingPinia } from '@pinia/testing'

// 模拟浏览器 API
Object.defineProperty(window, 'scrollTo', { value: vi.fn() })
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn()
  },
  writable: true
})

// 模拟 matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

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