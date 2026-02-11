// @vitest-environment jsdom
import { describe, it, expect } from 'vitest'

describe('基础测试', () => {
  it('应该通过', () => {
    expect(1 + 1).toBe(2)
  })
})