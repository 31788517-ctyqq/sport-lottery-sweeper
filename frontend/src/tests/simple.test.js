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