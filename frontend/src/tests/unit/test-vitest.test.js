import { describe, it, expect } from 'vitest'

describe('Vitest 测试', () => {
  it('应该通过基本测试', () => {
    console.log('测试运行中...')
    expect(1 + 1).toBe(2)
  })
  
  it('应该失败', () => {
    expect(1 + 1).toBe(3)
  })
})