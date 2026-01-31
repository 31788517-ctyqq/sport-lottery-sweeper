// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
import { beforeEach, afterEach } from 'vitest'

import { describe, it, expect } from 'vitest'

describe('jsdom environment test', () => {
  it('should have document', () => {
    expect(typeof document).toBe('object')
    expect(typeof window).toBe('object')
  })
  
  it('should have window.location', () => {
    expect(window.location).toBeDefined()
  })
  
  it('should have document.createElement', () => {
    expect(typeof document.createElement).toBe('function')
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
