import { expect, vi } from 'vitest'
import { createTestingPinia } from '@pinia/testing'

// 模拟浏览器API
Object.defineProperty(window, 'scrollTo', { value: vi.fn() })
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn()
  }
})

// 全局测试工具
global.createTestPinia = () => createTestingPinia({
  createSpy: vi.fn,
  initialState: {
    auth: { user: null, token: null, loading: false },
    matches: { matches: [], loading: false },
    bets: { bets: [], loading: false }
  }
})
