// AI_WORKING: coder1 @2026-01-29 19:20:00 - 验证Vitest基本功能
import { describe, it, expect } from 'vitest'

describe('Vitest基础功能验证', () => {
  it('应该正常运行纯JavaScript测试', () => {
    expect(1 + 1).toBe(2)
  })

  it('应该支持异步测试', async () => {
    const result = await Promise.resolve('success')
    expect(result).toBe('success')
  })

  it('应该支持对象相等性检查', () => {
    const obj = { a: 1, b: 2 }
    expect(obj).toEqual({ a: 1, b: 2 })
  })
})