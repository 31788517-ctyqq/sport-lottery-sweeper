// AI_WORKING: coder1 @2026-01-30 15:03:00 - 检查测试环境
import { describe, it, expect } from 'vitest'

describe('测试环境检查', () => {
  it('应该显示当前环境', () => {
    console.log('typeof window:', typeof window)
    console.log('typeof document:', typeof document)
    console.log('typeof localStorage:', typeof localStorage)
    console.log('process.env.VITEST_ENVIRONMENT:', process.env.VITEST_ENVIRONMENT)
    console.log('process.env.NODE_ENV:', process.env.NODE_ENV)
  })

  it('应该验证基本JavaScript功能', () => {
    expect(1 + 1).toBe(2)
  })
})