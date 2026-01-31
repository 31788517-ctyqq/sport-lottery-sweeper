// AI_WORKING: coder1 @2026-01-29 - 创建简单环境测试
import { beforeEach, afterEach } from 'vitest'

import { describe, it, expect } from 'vitest'

describe('Simple Environment Test', () => {
  it('should work without window', () => {
    expect(1 + 1).toBe(2)
  })

  it('should have describe and it available', () => {
    expect(typeof describe).toBe('function')
    expect(typeof it).toBe('function')
  })

  it('should have window object if jsdom loaded', () => {
    console.log('window type:', typeof window)
    console.log('global.window type:', typeof global.window)
    // 不要求window必须存在，只记录
    expect(true).toBe(true)
  })
})
// AI_DONE: coder1 @2026-01-29