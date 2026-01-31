// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
import { beforeEach, afterEach } from 'vitest'

import { describe, it, expect } from 'vitest'

describe('基础测试', () => {
  it('基础数学运算', () => {
    expect(1 + 1).toBe(2)
  })

  it('字符串测试', () => {
    expect('hello').toBe('hello')
  })

  it('数组测试', () => {
    expect([1, 2, 3]).toContain(2)
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
