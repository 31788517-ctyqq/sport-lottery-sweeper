// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
import { beforeEach, afterEach } from 'vitest'

import { describe, it, expect, beforeAll } from 'vitest'

describe('Debug Environment', () => {
  beforeAll(() => {
    console.log('typeof window:', typeof window)
    console.log('typeof global:', typeof global)
    console.log('typeof document:', typeof document)
    console.log('global.window:', global.window)
    console.log('global.document:', global.document)
  })

  it('should have window', () => {
    console.log('In test - window:', window)
    expect(typeof window).toBe('object')
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
